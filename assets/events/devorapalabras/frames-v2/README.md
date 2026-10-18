# Fotogramas aislados v2

48 imágenes individuales de 512×512 (12 por fase), con >=24 píxeles de margen totalmente transparente y apoyo alineado a y=464. El portal dibuja la imagen completa; no usa regiones de una cuadrícula.

Extraídas por componentes alfa de las figuras completas, conservando colas y alas que cruzaban los límites nominales de los atlas v1. Las conexiones débiles del alfa entre figuras se separan por proximidad al contorno principal. No se reutilizan recortes rectangulares de celdas.

Regenerar: `python scripts/extract-devorapalabras.py`.
Validar: `python scripts/check-devorapalabras-frames.py`.
Dependencias: Pillow, numpy y scipy. Los atlas originales se conservan sin cambios.
