"""Regression: one full dragon per file, fixed canvas and clear safety border."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy import ndimage

root=Path(__file__).resolve().parents[1]/'assets/events/devorapalabras/frames-v2'
manifest=json.loads((root/'manifest.json').read_text())
seen=set()
for phase in manifest['phases']:
    assert len(phase['frames'])==12
    for name in phase['frames']:
        assert name not in seen;seen.add(name)
        image=Image.open(root/name).convert('RGBA')
        assert image.size==(512,512)
        alpha=np.array(image)[:,:,3]
        assert not alpha[:24].any() and not alpha[-24:].any()
        assert not alpha[:,:24].any() and not alpha[:,-24:].any()
        labels,count=ndimage.label(alpha>32,structure=np.ones((3,3)))
        sizes=np.bincount(labels.ravel())[1:]
        assert sum(sizes>1500)==1,(name,'foreign dragon component')
        assert sizes.max()>60000,(name,'incomplete main figure')
assert len(seen)==48
print('Devorapalabras: 48 complete isolated figures, 512×512, >=24px transparent border, no neighboring dragon.')
