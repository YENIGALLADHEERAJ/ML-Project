"""Inference + Grad-CAM for the research demo. Uses the SAME preprocessing as the study ('full' variant: grey, stretched to 160 px, ImageNet normalisation)
and the four fine-tuned EfficientNet-B3 checkpoints (seed 0) saved in the frozen evaluation. Nothing is stored; all processing is in memory."""
import io, json, base64, hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image
try:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
    from lzma_stub import install; install()          # only needed in the local environment where _lzma is missing
except Exception:
    pass
import torch, torch.nn as nn
from torchvision import models
import cv2

HERE = Path(__file__).parent; MODEL_DIR = HERE / "models"; CL = ["Hip", "Knee", "Shoulder"]
SPEC = [("pooled", "Pooled model", "Trained on all six sources (the conventional setup)", "effnet_full_E0_pooled_s0.pt"),
        ("no_fracatlas", "Trained without FracAtlas", "Never saw the multi-joint source it is tested on", "effnet_full_E2_hold_F_s0.pt"),
        ("no_hip_implants", "Trained without the hip-implant source (K)", "Never saw Kaggle hip implant radiographs", "effnet_full_E3_hold_K_s0.pt"),
        ("no_shoulder_implants", "Trained without the shoulder-implant source (U)", "Never saw UCI shoulder implant radiographs", "effnet_full_E3_hold_U_s0.pt")]
MEAN = np.array([0.485, 0.456, 0.406], np.float32).reshape(1, 3, 1, 1); STD = np.array([0.229, 0.224, 0.225], np.float32).reshape(1, 3, 1, 1)
torch.set_num_threads(2); Image.MAX_IMAGE_PIXELS = 60_000_000
_cache = {}
_region_cache = None


def _load(file):
    net = models.efficientnet_b3(weights=None); net.classifier[1] = nn.Linear(net.classifier[1].in_features, 3)
    net.load_state_dict(torch.load(MODEL_DIR / file, map_location="cpu", weights_only=True)); return net.eval()


def available():
    return all((MODEL_DIR / s[3]).exists() for s in SPEC)


def get_models():
    if not _cache:
        for k, name, desc, f in SPEC: _cache[k] = _load(f)
    return _cache


def preprocess(img: Image.Image):
    """identical to scripts/final_eval.py make_variants()['full']"""
    g = np.asarray(img.convert("L"), dtype=np.float32) / 255.0; S = 160
    r = cv2.resize(g, (S, S), interpolation=cv2.INTER_AREA if min(g.shape) > S else cv2.INTER_LINEAR)
    u8 = np.clip(r * 255, 0, 255).astype(np.uint8)
    x = (u8.astype(np.float32) / 255.0)[None, None].repeat(3, 1); return torch.from_numpy((x - MEAN) / STD)


def _lut():
    stops = np.array([[0, 0, 0, 0], [0.25, 40, 70, 160], [0.5, 40, 200, 190], [0.75, 245, 200, 60], [1.0, 235, 60, 50]], np.float32); xs = np.linspace(0, 1, 256)
    return np.stack([np.interp(xs, stops[:, 0], stops[:, k]) for k in (1, 2, 3)], 1).astype(np.uint8)


def gradcam(net, x, cls):
    feats, grads = [], []
    h1 = net.features[-1].register_forward_hook(lambda m, i, o: feats.append(o)); h2 = net.features[-1].register_full_backward_hook(lambda m, gi, go: grads.append(go[0]))
    net.zero_grad(); out = net(x); out[0, cls].backward(); h1.remove(); h2.remove()
    w = grads[0].mean((2, 3), keepdim=True); cam = torch.relu((w * feats[0]).sum(1))[0].detach().numpy(); cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8); return cam


def overlay(img: Image.Image, cam):
    base = img.convert("L"); base.thumbnail((640, 640)); W, H = base.size; c = cv2.resize(cam, (W, H), interpolation=cv2.INTER_CUBIC); c = np.clip(c, 0, 1)
    rgb = np.stack([np.asarray(base)] * 3, -1).astype(np.float32); heat = _lut()[(c * 255).astype(np.uint8)].astype(np.float32); a = (0.15 + 0.55 * c)[..., None]
    mix = np.clip(rgb * (1 - a) + heat * a, 0, 255).astype(np.uint8); buf = io.BytesIO(); Image.fromarray(mix).save(buf, "JPEG", quality=85); return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def region_available():
    return all((MODEL_DIR / f"region_model.{suffix}").is_file() for suffix in ("pt", "json"))


def region_view_scores(model, x):
    views = [x, x.flip(-1)]
    height, width = x.shape[-2:]
    for fraction in (0.05, 0.10, 0.15):
        dy, dx = round(height * fraction), round(width * fraction)
        for cropped in (x[:, :, dy:-dy, :-2 * dx], x[:, :, dy:-dy, 2 * dx:]):
            views.append(nn.functional.interpolate(cropped, size=(height, width), mode="bilinear", align_corners=False))
    scores = model(torch.cat(views)).sigmoid()
    return scores.reshape(len(views), len(x), -1).mean(dim=0)


def expanded_scores(model, img, x, config):
    score = region_view_scores if config.get("average_views") else lambda m, z: m(z).sigmoid()
    weight = config.get("center_crop_weight", 0)
    if weight == 0:
        return score(model, x)
    width, height = img.size
    center = img.crop((int(.15 * width), int(.15 * height),
                       int(.85 * width), int(.85 * height)))
    centered = score(model, preprocess(center))
    return centered if weight == 1 else torch.lerp(score(model, x), centered, weight)


def predict_regions(img, x):
    if not region_available():
        return None
    global _region_cache
    if _region_cache is None:
        config = json.loads((MODEL_DIR / "region_model.json").read_text(encoding="utf-8"))
        model = models.efficientnet_b3(weights=None)
        model.classifier[1] = nn.Linear(model.classifier[1].in_features, len(config["classes"]))
        model.load_state_dict(torch.load(MODEL_DIR / "region_model.pt", map_location="cpu", weights_only=True))
        _region_cache = model.eval(), config
    model, config = _region_cache
    with torch.inference_mode():
        scores = expanded_scores(model, img, x, config)[0].tolist()
    return {"classes": [
        {"name": name, "score": round(score, 4), "threshold": threshold, "selected": score >= threshold}
        for name, score, threshold in zip(config["classes"], scores, config["thresholds"], strict=True)
    ]}


def predict(img: Image.Image, with_cam=True):
    mods = get_models(); x = preprocess(img); res = []; cam_png = None
    for k, name, desc, f in SPEC:
        net = mods[k]
        with torch.no_grad(): p = torch.softmax(net(x), 1)[0].numpy()
        ent = float(-(p * np.log(p + 1e-12)).sum() / np.log(3)); res.append(dict(id=k, name=name, description=desc, probs={c: round(float(p[i]), 4) for i, c in enumerate(CL)}, pred=CL[int(p.argmax())], confidence=round(float(p.max()), 4), entropy=round(ent, 4)))
        if k == "pooled" and with_cam:
            cam_png = overlay(img, gradcam(net, x.clone().requires_grad_(False), int(p.argmax())))
    preds = {r["pred"] for r in res}
    return dict(models=res, all_agree=len(preds) == 1, gradcam=cam_png, gradcam_model="pooled", gradcam_class=res[0]["pred"], expanded=predict_regions(img, x))


def image_facts(raw: bytes, img: Image.Image):
    rgb = img.convert("RGB").resize((64, 64)); a = np.asarray(rgb, np.float32); sat = float((a.max(2) - a.min(2)).mean() / 255.0)
    g = np.asarray(img.convert("L"), np.float32) / 255.0; h, w = g.shape; bw = max(2, int(0.1 * min(h, w)))
    border = float(np.mean([g[:bw].mean(), g[-bw:].mean(), g[:, :bw].mean(), g[:, -bw:].mean()]))
    return dict(width=int(img.size[0]), height=int(img.size[1]), aspect=round(img.size[0] / img.size[1], 3), format=img.format or "unknown", file_kb=round(len(raw) / 1024, 1), mode=img.mode, colour_saturation=round(sat, 3), border_mean=round(border, 3))


def model_hashes():
    return {s[0]: dict(file=s[3], sha256=hashlib.sha256((MODEL_DIR / s[3]).read_bytes()).hexdigest()[:16]) for s in SPEC if (MODEL_DIR / s[3]).exists()}
