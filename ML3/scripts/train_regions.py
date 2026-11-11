from __future__ import annotations

import argparse
import csv
import hashlib
import json
import time
from collections import Counter
from pathlib import Path, PurePosixPath, PureWindowsPath
from zipfile import ZipFile

import cv2
import numpy as np
import torch
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from torchvision.models import EfficientNet_B3_Weights, efficientnet_b3

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ["Hip", "Knee", "Shoulder", "Hand", "Leg", "Elbow"]
SIZE = 160
REGION_TAGS = {0: "hip", 2: "shoulder", 3: "hand", 4: "leg"}
FOLDER = ROOT / "data/fracatlas/FracAtlas"
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def collect_records(elbow_archive, review, elbowlat_index):
    manifest = read_csv(ROOT / "artifacts/benchmark/manifest_v2.csv")
    tags = {r["image_id"]: r for r in read_csv(FOLDER / "dataset.csv")}
    frac_paths = {path.name: path for path in (FOLDER / "images").rglob("*.jpg")}
    original_splits = {}
    for row in manifest:
        if row["split"] in {"train", "val", "test"}:
            original_splits.setdefault(row["group"], set()).add(row["split"])

    records = []
    seen_frac = set()
    for row in manifest:
        path = ROOT.joinpath(*PureWindowsPath(row["path"]).parts[2:])
        if row["source"] == "O" and path.parent.parent.name == "auto_test":
            continue
        if row["role"] == "excluded":
            if row["source"] == "F":
                seen_frac.add(path.name)
            continue
        if row["source"] == "F":
            seen_frac.add(path.name)
            labels = frac_labels(tags[path.name], row)
            if path.name in review:
                regions = review[path.name]
                labels[1] = int("knee" in regions)
                labels[4] = labels[1]
                labels[5] = int("elbow" in regions)
        else:
            labels = [0] * len(CLASSES)
            labels[CLASSES.index(row["label"])] = 1
            labels[4] = int(row["label"] == "Knee")
        records.append((path, row["source"], row["group"], labels))
    oai = ROOT / "data/oai_knee"
    for folder in ("train", "val", "test"):
        for path in sorted((oai / folder).rglob("*.png")):
            group = "O_" + path.stem.rstrip("LR")
            original_splits.setdefault(group, set()).add(folder)
            records.append((path, "O", group, [0, 1, 0, 0, 1, 0]))
    for name in sorted(tags.keys() - seen_frac):
        records.append((frac_paths[name], "F", "F-mixed-" + str(int(Path(name).stem[3:]) // 10),
                        frac_labels(tags[name])))

    assignments = {}
    for path, source, group, labels in records:
        if group in original_splits:
            splits = original_splits[group]
            split = next(value for value in ("test", "val", "train") if value in splits)
        else:
            bucket = int(hashlib.sha256(group.encode()).hexdigest()[:8], 16) % 100
            split = "train" if bucket < 70 else "val" if bucket < 85 else "test"
        assignments[path] = (source, group, split, labels)
    with ZipFile(elbow_archive) as archive:
        partitions = {"01.train": "train", "03.validation": "test"}
        for member in archive.namelist():
            parts = PurePosixPath(member).parts
            if len(parts) != 3 or parts[0] != "PediaSHF-DX" or parts[1] not in partitions:
                continue
            if PurePosixPath(parts[2]).suffix.lower() != ".jpg":
                continue
            assignments[member] = ("PediaSHF-DX", parts[2], partitions[parts[1]], [0, 0, 0, 0, 0, 1])
    if elbowlat_index:
        for row in read_csv(elbowlat_index):
            path = elbowlat_index.resolve().parent / row["image"]
            assignments[path] = ("ElbowLat", row["subject_id"], row["split"], [0, 0, 0, 0, 0, 1])
    return assignments


def frac_labels(tags, row=None):
    labels = [0] * len(CLASSES)
    for index, tag in REGION_TAGS.items():
        labels[index] = int(tags[tag])
    # A broad leg tag supplies no knee annotation. The project knee labels are
    # provisional, so keep them unknown and learn Knee from the knee datasets.
    if labels[4] or (row and row["label"] == "Knee"):
        labels[1] = -1
    # FracAtlas does not annotate elbows as a distinct region.
    labels[5] = -1
    return labels


def prepare(records, out, archive):
    images = np.empty((len(records), SIZE, SIZE), dtype=np.uint8)
    labels = np.empty((len(records), len(CLASSES)), dtype=np.int8)
    splits = []
    skipped = []
    details = []
    index = 0
    for path, (source, group, split, target) in records.items():
        if isinstance(path, str):
            file_name = path
            image = cv2.imdecode(np.frombuffer(archive.read(path), dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
        else:
            file_name = str(path.relative_to(ROOT))
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if image is None:
            skipped.append(file_name)
            continue
        method = cv2.INTER_AREA if min(image.shape) > SIZE else cv2.INTER_LINEAR
        images[index] = cv2.resize(image, (SIZE, SIZE), interpolation=method)
        labels[index] = target
        splits.append(split)
        details.append([file_name, source, group, split, *target])
        index += 1
    with (out / "splits.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "source", "group", "split", *CLASSES])
        writer.writerows(details)
    return images[:index], labels[:index], np.array(splits), skipped


def batches(images, labels, indices, batch_size, shuffle):
    data = TensorDataset(torch.from_numpy(images[indices]), torch.from_numpy(labels[indices]))
    return DataLoader(data, batch_size=batch_size, shuffle=shuffle, pin_memory=True)


def probabilities(net, loader, preprocess):
    net.eval()
    scores = []
    with torch.inference_mode():
        for images, _ in loader:
            with torch.autocast("cuda"):
                scores.append(net(preprocess(images)).float().sigmoid().cpu().numpy())
    return np.concatenate(scores)


def evaluate(labels, ix, val, test):
    report = {}
    thresholds = []
    for i, name in enumerate(CLASSES):
        yval, ytest = labels[ix["val"], i], labels[ix["test"], i]
        v, t = yval >= 0, ytest >= 0
        threshold = .5 if not yval[v].any() else max(np.arange(.1, .91, .05),
                        key=lambda cutoff: (f1_score(yval[v], val[v, i] >= cutoff, zero_division=0),
                                            -abs(cutoff - .5)))
        thresholds.append(round(float(threshold), 2))
        pred = test[t, i] >= threshold
        report[name] = dict(positives=int(ytest[t].sum()), evaluated=int(t.sum()),
                            precision=precision_score(ytest[t], pred, zero_division=0),
                            recall=recall_score(ytest[t], pred, zero_division=0),
                            f1=f1_score(ytest[t], pred, zero_division=0),
                            average_precision=average_precision_score(ytest[t], test[t, i]))
    return thresholds, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--elbow-archive", type=Path, required=True)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--elbowlat-index", type=Path)
    parser.add_argument("--initialize", type=Path)
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1:
        parser.error("epochs and batch size must be positive")
    if not torch.cuda.is_available():
        parser.error("CUDA is required")
    args.output.mkdir(parents=True, exist_ok=False)
    torch.manual_seed(0)
    start = time.perf_counter()

    review = {r["image_id"]: r["visual_regions"].split("+") for r in read_csv(args.review)} if args.review else {}
    records = collect_records(args.elbow_archive, review, args.elbowlat_index)
    assert all(split == "test" for path, (_, _, split, _) in records.items()
               if isinstance(path, Path) and path.name == "IMG0000335.jpg")
    with ZipFile(args.elbow_archive) as archive:
        images, labels, splits, skipped = prepare(records, args.output, archive)
    ix = {split: np.flatnonzero(splits == split) for split in ("train", "val", "test")}
    print("Split sizes", dict(Counter(splits)), "unreadable", len(skipped), flush=True)
    loaders = {split: batches(images, labels, idx, args.batch_size, split == "train")
               for split, idx in ix.items()}
    if review:
        reviewed_train = [i for i, row in enumerate(read_csv(args.output / "splits.csv"))
                          if row["source"] == "F" and row["split"] == "train" and Path(row["path"]).name in review]
        train_indices = np.concatenate((ix["train"], np.repeat(reviewed_train, 15).astype(int)))
        loaders["train"] = batches(images, labels, train_indices, args.batch_size, True)
    counts = (labels[ix["train"]] == 1).sum(axis=0)
    print("Training positives", dict(zip(CLASSES, counts.tolist())), flush=True)
    if (counts == 0).any():
        raise ValueError("Training data is missing at least one class")
    mean = torch.tensor(MEAN, device="cuda").view(1, 3, 1, 1)
    std = torch.tensor(STD, device="cuda").view(1, 3, 1, 1)

    def preprocess(x):
        return (x.to("cuda", non_blocking=True).float().unsqueeze(1).div(255) - mean) / std

    net = efficientnet_b3(weights=None if args.initialize else EfficientNet_B3_Weights.IMAGENET1K_V1)
    net.classifier[-1] = nn.Linear(net.classifier[-1].in_features, len(CLASSES))
    if args.initialize:
        net.load_state_dict(torch.load(args.initialize, map_location="cpu", weights_only=True))
    net.cuda()
    optimizer = torch.optim.AdamW(net.parameters(), lr=1e-4 if args.initialize else 3e-4, weight_decay=1e-2)
    scaler = torch.amp.GradScaler()
    weight = torch.tensor(np.sqrt((labels[ix["train"]] == 0).sum(axis=0) / counts),
                          dtype=torch.float32, device="cuda")
    loss_fn = nn.BCEWithLogitsLoss(reduction="none", pos_weight=weight)
    for epoch in range(args.epochs):
        net.train()
        total = torch.zeros((), device="cuda")
        for inputs, target in loaders["train"]:
            x = preprocess(inputs)
            flip = torch.rand(len(x), device="cuda") < 0.5
            x[flip] = x[flip].flip(-1)
            y = target.to("cuda", non_blocking=True)
            valid = y >= 0
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast("cuda"):
                loss = (loss_fn(net(x), y.clamp_min(0).float()) * valid).sum() / valid.sum()
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total += loss.detach()
        print(f"Epoch {epoch + 1}/{args.epochs} loss {total.item() / len(loaders['train']):.4f}", flush=True)

    val = probabilities(net, loaders["val"], preprocess)
    test = probabilities(net, loaders["test"], preprocess)
    thresholds, report = evaluate(labels, ix, val, test)
    torch.save(net.cpu().state_dict(), args.output / "region_model.pt")
    metadata = dict(classes=CLASSES, thresholds=thresholds, size=SIZE, mean=MEAN, std=STD,
                    epochs=args.epochs, reviewed_fracatlas=len(review), elbowlat=bool(args.elbowlat_index), split_counts=dict(Counter(splits)), skipped=skipped,
                    training_positives=dict(zip(CLASSES, counts.tolist())), test=report,
                    elapsed_seconds=round(time.perf_counter() - start, 2))
    (args.output / "metrics.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
