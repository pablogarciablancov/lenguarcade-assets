"""Extract the 48 original dragon figures by alpha components, never grid cells.

Usage: python scripts/extract-devorapalabras.py
Requires Pillow, numpy and scipy. Existing v1 atlases are preserved unchanged.
"""
from pathlib import Path
import hashlib
from io import BytesIO
import json
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/events/devorapalabras'
DEST = ASSETS / 'frames-v2'
DEST.mkdir(parents=True, exist_ok=True)
manifest = {'version': 2, 'size': [512, 512], 'baseline': 464, 'phases': []}
for phase in ['healthy', 'cracked', 'torn', 'critical']:
    source = ASSETS / f'dragon-{phase}-idle-v1.webp'
    rgba = np.array(Image.open(source).convert('RGBA'))
    alpha = rgba[:, :, 3]
    labels, count = ndimage.label(alpha > 32, structure=np.ones((3, 3)))
    sizes = np.bincount(labels.ravel())
    large = np.flatnonzero(sizes > 1500)
    large = large[large != 0]
    assert len(large) == 12, (phase, len(large))
    boxes = ndimage.find_objects(labels)
    # Main silhouettes do not touch at alpha > 32. Weak alpha bridges between
    # neighbors are assigned to the nearest complete silhouette, not a cell.
    main = np.where(np.isin(labels, large), labels, 0)
    distance, indices = ndimage.distance_transform_edt(main == 0, return_indices=True)
    owner = main[tuple(indices)]
    ordered = sorted(large, key=lambda k: ((boxes[k-1][0].start + boxes[k-1][0].stop)//2//(alpha.shape[0]/3), (boxes[k-1][1].start + boxes[k-1][1].stop)/2))
    frames = []
    for index, label in enumerate(ordered):
        by, bx = boxes[label - 1]
        feet_y = max(by.start, by.stop - 14)
        feet = np.where(labels[feet_y:by.stop] == label)[1]
        anchor_x = int(round(float(np.median(feet))))
        anchor_y = by.stop
        visible = (owner == label) & (alpha > 0) & ((alpha > 32) | (distance <= 2))
        ys, xs = np.where(visible)
        left, right, top, bottom = xs.min(), xs.max()+1, ys.min(), ys.max()+1
        cutout = rgba[top:bottom, left:right].copy()
        cutout[:, :, 3] = np.where(visible[top:bottom, left:right], cutout[:, :, 3], 0)
        canvas = Image.new('RGBA', (512, 512))
        dx, dy = 256 - anchor_x + left, 464 - anchor_y + top
        assert min(dx, dy) >= 24 and max(dx+right-left, dy+bottom-top) <= 488, (phase, index, dx, dy)
        canvas.paste(Image.fromarray(cutout), (int(dx), int(dy)))
        output = DEST / f'{phase}-{index:02}.webp'
        encoded=BytesIO()
        canvas.save(encoded, 'WEBP', lossless=True, method=6, exact=True)
        temporary=output.with_suffix('.tmp')
        temporary.write_bytes(encoded.getvalue())
        temporary.replace(output)
        check = np.array(Image.open(output))[:, :, 3]
        assert not check[:24].any() and not check[-24:].any()
        assert not check[:, :24].any() and not check[:, -24:].any()
        assert np.count_nonzero(check) == np.count_nonzero(alpha[visible]), 'Pixels clipped'
        frames.append(output.name)
    manifest['phases'].append({'id': phase, 'sourceSha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'frames': frames})
    print(phase, len(frames), 'isolated figures, fixed foot baseline, >=24px transparent border')
(DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
