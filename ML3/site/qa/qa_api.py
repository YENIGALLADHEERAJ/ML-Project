"""End-to-end API QA: live predictions must reproduce the precomputed sample outputs; robustness to odd inputs. Run with the server up on :8000."""
import json, io, sys, os, urllib.request, urllib.error
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from PIL import Image
B = "http://localhost:8000"; fails = []
def post(data, ctype):
    r = urllib.request.Request(B + "/api/predict", data=data, headers={"Content-Type": ctype}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=60) as x: return x.status, json.loads(x.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())
def chk(n, ok, e=""):
    print(("PASS " if ok else "FAIL ") + n + (f" [{e}]" if e else "")); ok or fails.append(n)
S = json.load(open("data/samples.json", encoding="utf-8")); worst = 0; agree = 0; cam = 0
for s in S:
    st, j = post(open(s["file"], "rb").read(), "image/jpeg")
    assert st == 200, (s["id"], st, j)
    for a, b in zip(j["models"], s["models"]):
        worst = max(worst, max(abs(a["probs"][c] - b["probs"][c]) for c in a["probs"]))
    agree += [m["pred"] for m in j["models"]] == [m["pred"] for m in s["models"]]; cam += j["gradcam"].startswith("data:image/") and j["stored"] is False
chk("9/9 live predictions match precomputed predicted labels", agree == 9, f"{agree}/9")
chk("max |prob difference| live vs precomputed < 0.005", worst < 0.005, f"{worst:.5f}")
chk("Grad-CAM returned for all, stored=false", cam == 9)
im = Image.open(S[0]["file"]).convert("L"); b = io.BytesIO(); im.save(b, "PNG"); st, j = post(b.getvalue(), "image/png"); chk("PNG greyscale accepted", st == 200 and len(j["models"]) == 4)
b = io.BytesIO(); Image.new("RGB", (300, 300), (200, 40, 40)).save(b, "JPEG"); st, j = post(b.getvalue(), "image/jpeg"); chk("colour photo -> still answers but warns", st == 200 and any("colour" in w for w in j["warnings"]))
b = io.BytesIO(); Image.new("L", (30, 30)).save(b, "PNG"); st, j = post(b.getvalue(), "image/png"); chk("tiny image rejected (400)", st == 400)
try:
    st, j = post(b"x" * (13 * 1024 * 1024), "image/jpeg"); chk("13 MB rejected (413)", st == 413, str(st))
except (ConnectionError, OSError): chk("13 MB rejected (server closed connection early)", True)
st, j = post(b"GIF89a", "image/gif"); chk("gif content-type rejected (415)", st == 415)
b = io.BytesIO(); Image.new("L", (4000, 3000), 90).save(b, "PNG"); st, j = post(b.getvalue(), "image/png"); chk("4000x3000 image processed", st == 200)
print("\nFAILED: " + ", ".join(fails) if fails else "\nALL API CHECKS PASSED"); sys.exit(bool(fails))
