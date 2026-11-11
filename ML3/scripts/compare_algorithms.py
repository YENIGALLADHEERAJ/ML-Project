"""Compare supervised classifiers and unsupervised clustering on development data."""
from pathlib import Path, PureWindowsPath
import csv
import json

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, balanced_accuracy_score, f1_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "artifacts/benchmark/v2"
REVIEW = ROOT / "artifacts/retraining/fracatlas-anatomy-review.csv"
OUT = ROOT / "artifacts/retraining/algorithm-comparison.json"


def algorithms():
    logistic = LogisticRegression(C=1, class_weight="balanced", max_iter=1000)
    svm = SVC(C=5, class_weight="balanced")
    forest = RandomForestClassifier(n_estimators=150, class_weight="balanced_subsample",
                                    min_samples_leaf=2, random_state=0, n_jobs=4)
    return {
        "Logistic regression": logistic,
        "CART decision tree": DecisionTreeClassifier(max_depth=10, min_samples_leaf=5,
                                                      class_weight="balanced", random_state=0),
        "Random forest": forest,
        "RBF SVM": svm,
        "Gradient boosting": HistGradientBoostingClassifier(max_iter=100, max_leaf_nodes=15,
                                                             class_weight="balanced", random_state=0),
        "Voting ensemble": VotingClassifier([("lr", logistic), ("svm", svm), ("rf", forest)]),
    }


def main():
    rows = pd.read_csv(DEV / "rows.csv")
    with REVIEW.open(newline="", encoding="utf-8") as handle:
        elbows = {row["image_id"] for row in csv.DictReader(handle) if "elbow" in row["visual_regions"]}
    keep = ~rows.path.map(lambda path: PureWindowsPath(path).name in elbows)
    target = rows[rows.role.eq("target") & keep]
    training = target[target.split.eq("train")]
    validation = target[target.split.eq("val")]
    fracatlas = validation[validation.source.eq("F")]
    embedding = np.load(DEV / "emb_effnet_full.npy", mmap_mode="r")
    assert len(rows) == len(embedding) and not rows.split.eq("test").any()
    assert not set(zip(training.source, training.group)) & set(zip(validation.source, validation.group))
    result = {"features": "Frozen EfficientNet-B3 embeddings, standardization, and 64-component PCA",
              "reviewed_elbow_rows_removed": int((~keep & rows.role.eq("target")).sum()),
              "protocols": {}, "clustering": []}

    for name, train, val in [
        ("pooled", training, validation),
        ("without_fracatlas", training[training.source.ne("F")], fracatlas),
    ]:
        scaler = StandardScaler()
        train_scaled = scaler.fit_transform(embedding[train.index])
        pca = PCA(n_components=64, svd_solver="randomized", random_state=0)
        x = pca.fit_transform(train_scaled)
        z = pca.transform(scaler.transform(embedding[val.index]))
        scores = []
        for label, model in algorithms().items():
            pred = model.fit(x, train.label).predict(z)
            scores.append(dict(model=label,
                               balanced_accuracy=float(balanced_accuracy_score(val.label, pred)),
                               macro_f1=float(f1_score(val.label, pred, average="macro"))))
            print(name, scores[-1], flush=True)
        result["protocols"][name] = dict(n_train=len(train), n_val=len(val),
                                         scores=scores,
                                         best=max(scores, key=lambda r: (r["balanced_accuracy"], r["macro_f1"]))["model"])

        if name == "pooled":
            for label, model in [
                ("K-means", KMeans(n_clusters=3, n_init=20, random_state=0)),
                ("Gaussian mixture (EM)", GaussianMixture(n_components=3, covariance_type="diag", random_state=0)),
                ("Hierarchical clustering", AgglomerativeClustering(n_clusters=3)),
            ]:
                # Hierarchical clustering has no prediction method; describe the same validation cohort.
                if label == "Hierarchical clustering":
                    clusters = model.fit_predict(z)
                else:
                    clusters = model.fit(x).predict(z)
                result["clustering"].append(dict(method=label,
                    anatomy_ari=float(adjusted_rand_score(val.label, clusters)),
                    source_ari=float(adjusted_rand_score(val.source, clusters)),
                    silhouette=float(silhouette_score(z, clusters))))
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result["clustering"], indent=2), flush=True)


if __name__ == "__main__":
    with threadpool_limits(limits=4):
        main()
