"""Create a demo image that contains NO anatomy, only a gradient and speckle, saved as a 640x640 RGB JPEG of about
the size of an AV-DDH (hip) file. Upload it to the workbench to show what the shortcut probe does: it reads only
file properties, so it confidently names a joint for a picture with no bones in it.

Usage (repo root):  .venv\\Scripts\\python.exe ML3/scripts/make_noanatomy_demo.py demo_noanatomy.jpg
"""
import io
import sys

import numpy as np
from PIL import Image

out = sys.argv[1] if len(sys.argv) > 1 else "demo_noanatomy.jpg"
rng = np.random.default_rng(1)
y, x = np.mgrid[0:640, 0:640]
base = (30 + 150 * (x + y) / 1280.0)[..., None] * np.ones(3)
img = np.clip(base + rng.normal(0, 18, (640, 640, 1)), 0, 255).astype(np.uint8)

best = None  # choose the JPEG quality whose file size is closest to a typical AV-DDH file (36 kB)
for quality in range(10, 96, 5):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, "JPEG", quality=quality)
    kb = len(buf.getvalue()) / 1024
    if best is None or abs(kb - 36.3) < abs(best[0] - 36.3):
        best = (kb, quality, buf.getvalue())
kb, quality, raw = best
with open(out, "wb") as fh:
    fh.write(raw)
print(f"saved {out}: 640x640 RGB JPEG, quality {quality}, {kb:.1f} kB (no anatomy in this image)")
