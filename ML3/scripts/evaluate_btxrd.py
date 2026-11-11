"""Run the frozen expanded anatomy model on BTXRD joint-tagged radiographs."""
import argparse
import csv
import hashlib
import io
import json
import sys
import struct
import zlib
from pathlib import Path, PurePosixPath
from zipfile import ZipFile

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site/api"))
import infer

JOINTS = {"Elbow": "elbow-joint", "Knee": "knee-joint", "Shoulder": "shoulder-joint"}
CHECKPOINT = "8a5f41fd621e6a4f032040d2e0a44fd8d73c21da1df21205c1bd62527d2505cd"
CONFIG = "e46e7929a3a77d6485d4eb5e698a2f65f336cab1d71342c882aa18306da848f8"
ARCHIVE_MD5 = "59132a5036d030580ccade8add8f13df"


def digest(path, algorithm):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def read_cohort(archive):
    manifest, = [name for name in archive.namelist() if PurePosixPath(name).name == "dataset.csv"]
    with archive.open(manifest) as raw:
        rows = list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig")))
    image_members = {PurePosixPath(name).name: name for name in archive.namelist()
                     if PurePosixPath(name).suffix.lower() in {".jpeg", ".jpg", ".png"}}
    cohort = []
    for row in rows:
        tags = [joint for joint, column in JOINTS.items() if int(row[column]) == 1]
        if len(tags) == 1:
            cohort.append((row["image_id"], tags[0], image_members[row["image_id"]]))
    assert len(cohort) == len({image_id for image_id, _, _ in cohort})
    return cohort


def read_mirror_members(plan_path):
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    images = {}
    cohort = []
    for row in plan:
        image_id = row["image_id"]
        path = plan_path.parent / "audit-members" / (image_id + ".part")
        raw = path.read_bytes()
        if len(raw) != row["end"] - row["start"] + 1 or raw[:4] != b"PK\x03\x04":
            raise ValueError(f"Incomplete ZIP range for {image_id}")
        name_size, extra_size = struct.unpack_from("<HH", raw, 26)
        start = 30 + name_size + extra_size
        if PurePosixPath(raw[30:30 + name_size].decode()).name != image_id:
            raise ValueError(f"Unexpected member name for {image_id}")
        payload = raw[start:start + row["compressed_size"]]
        if row["compression"] == 8:
            payload = zlib.decompress(payload, -15)
        elif row["compression"] != 0:
            raise ValueError(f"Unsupported ZIP compression for {image_id}")
        if zlib.crc32(payload) != row["crc"]:
            raise ValueError(f"CRC check failed for {image_id}")
        images[image_id] = payload
        cohort.append((image_id, row["reference"], image_id))
    if len(cohort) != len(images):
        raise ValueError("Duplicate image IDs in the audit plan")
    return cohort, images


def evaluate(read_image, cohort, model, config, device):
    torch = infer.torch
    predictions = []
    for start in range(0, len(cohort), 12):
        batch = cohort[start:start + 12]
        tensors = []
        for _, _, member in batch:
            with Image.open(io.BytesIO(read_image(member))) as image:
                tensors.append(infer.preprocess(image))
        with torch.inference_mode():
            scores = infer.region_view_scores(model, torch.cat(tensors).to(device)).cpu().tolist()
        for (image_id, joint, _), values in zip(batch, scores, strict=True):
            flagged = [name for name, score, threshold in zip(config["classes"], values, config["thresholds"], strict=True)
                       if score >= threshold]
            predictions.append({"image_id": image_id, "reference": joint, "flagged": flagged,
                                "scores": dict(zip(config["classes"], values, strict=True))})
        if start % 240 == 0:
            print(f"Scored {len(predictions)}/{len(cohort)}", flush=True)
    return predictions


def summarize(predictions):
    summary = {}
    for joint in JOINTS:
        positives = [r for r in predictions if r["reference"] == joint]
        negatives = [r for r in predictions if r["reference"] != joint]
        summary[joint] = {
            "positives": len(positives),
            "true_positives": sum(joint in r["flagged"] for r in positives),
            "other_joint_images": len(negatives),
            "false_flags_on_other_joints": sum(joint in r["flagged"] for r in negatives),
        }
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--config", type=Path, help="Path to the archived frozen baseline configuration")
    parser.add_argument("--mirror-subset", action="store_true", help="Use a preselected JSON range plan")
    args = parser.parse_args()
    checkpoint = infer.MODEL_DIR / "region_model.pt"
    config_path = args.config or infer.MODEL_DIR / "region_model.json"
    if (digest(checkpoint, "sha256"), digest(config_path, "sha256")) != (CHECKPOINT, CONFIG):
        raise RuntimeError("The model or cutoffs differ from the frozen evaluation inputs.")
    if not args.mirror_subset and digest(args.archive, "md5") != ARCHIVE_MD5:
        raise RuntimeError("The official archive checksum differs from the published value.")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    torch = infer.torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = infer.models.efficientnet_b3(weights=None)
    model.classifier[1] = infer.nn.Linear(model.classifier[1].in_features, len(config["classes"]))
    model.load_state_dict(torch.load(checkpoint, map_location="cpu", weights_only=True))
    model.to(device).eval()
    if args.mirror_subset:
        cohort, images = read_mirror_members(args.archive)
        print(f"BTXRD mirror cohort {len(cohort)} images on {device}", flush=True)
        predictions = evaluate(images.__getitem__, cohort, model, config, device)
    else:
        with ZipFile(args.archive) as archive:
            cohort = read_cohort(archive)
            print(f"BTXRD cohort {len(cohort)} images on {device}", flush=True)
            predictions = evaluate(archive.read, cohort, model, config, device)
    summary = summarize(predictions)
    args.output.write_text(json.dumps({
        "dataset": "BTXRD", "source": "https://doi.org/10.6084/m9.figshare.27865398",
        "cohort": ("All mirror spreadsheet rows with exactly one of the Elbow, Knee and Shoulder tags"
                   if args.mirror_subset else "All images with exactly one of the Elbow, Knee and Shoulder dataset tags"),
        "checkpoint_sha256": CHECKPOINT, "config_sha256": CONFIG,
        "archive_md5": None if args.mirror_subset else ARCHIVE_MD5,
        "mirror": "https://www.kaggle.com/datasets/thanhngan123/btxrd-data" if args.mirror_subset else None,
        "plan_sha256": digest(args.archive, "sha256") if args.mirror_subset else None,
        "config": config, "summary": summary, "predictions": predictions,
    }, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
