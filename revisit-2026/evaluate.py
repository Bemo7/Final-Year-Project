"""2026 re-evaluation of the final-year illness-diagnosis model.

De-duplicates the data, runs stratified k-fold cross-validation, and compares
the original neural-network architecture with simple baselines.

Run from the repository root:  python revisit-2026/evaluate.py
Requires: pandas, numpy, scikit-learn, tensorflow
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

SEED = 42
N_SPLITS = 5
OUT = Path("revisit-2026")

# 1. Load both files and report duplication -----------------------------------
train = pd.read_csv("datasets/training.csv", header=None)
test = pd.read_csv("datasets/testing.csv", header=None)
# If the CSVs have a header row, change header=None to header=0 above.

n_train, n_test = len(train), len(test)
data = pd.concat([train, test], ignore_index=True)
unique = data.drop_duplicates()

X = unique.iloc[:, :-1].astype(float).to_numpy()
labels = unique.iloc[:, -1].astype(str).str.strip()

test_in_train = test.merge(train.drop_duplicates(), how="inner").shape[0]
print(f"Training rows: {n_train}, test rows: {n_test}")
print(f"Unique rows after de-duplication: {len(unique)}")
print(f"Test rows that also appear in training data: {test_in_train}/{n_test}")

# 2. Encode labels ONCE --------------------------------------------------------
encoder = LabelEncoder().fit(labels)
y = encoder.transform(labels)
n_classes = len(encoder.classes_)
min_count = np.bincount(y).min()
n_splits = min(N_SPLITS, min_count)
print(f"Classes: {n_classes}, smallest class size: {min_count}, folds: {n_splits}")


# 3. Models -------------------------------------------------------------------
def neural_net(X_tr, y_tr, X_te):
    import tensorflow as tf

    tf.random.set_seed(SEED)
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(X_tr.shape[1],)),
        tf.keras.layers.Dense(254, activation="relu"),
        tf.keras.layers.Dense(n_classes, activation="softmax"),
    ])
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy")
    model.fit(X_tr, y_tr, epochs=50, batch_size=32, verbose=0)
    return model.predict(X_te, verbose=0).argmax(axis=1)


def sklearn_model(make):
    def run(X_tr, y_tr, X_te):
        return make().fit(X_tr, y_tr).predict(X_te)
    return run


MODELS = {
    "Neural network": neural_net,
    "Logistic regression": sklearn_model(lambda: LogisticRegression(max_iter=2000)),
    "Decision tree": sklearn_model(lambda: DecisionTreeClassifier(random_state=SEED)),
    "Naive Bayes": sklearn_model(MultinomialNB),
}

# 4. Cross-validate ------------------------------------------------------------
skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=SEED)
rows = []
for name, fit_predict in MODELS.items():
    scores, all_true, all_pred = [], [], []
    for tr, te in skf.split(X, y):
        pred = fit_predict(X[tr], y[tr], X[te])
        p, r, f, _ = precision_recall_fscore_support(y[te], pred, average="macro", zero_division=0)
        scores.append((accuracy_score(y[te], pred), p, r, f))
        all_true.extend(y[te])
        all_pred.extend(pred)
    s = np.array(scores)
    rows.append({
        "Model": name,
        **{f"{m} (mean)": s[:, i].mean() for i, m in enumerate(["Accuracy", "Macro P", "Macro R", "Macro F1"])},
        "Macro F1 (std)": s[:, 3].std(),
    })
    cm = pd.DataFrame(confusion_matrix(all_true, all_pred), index=encoder.classes_, columns=encoder.classes_)
    cm.to_csv(OUT / f"confusion_{name.lower().replace(' ', '_')}.csv")

results = pd.DataFrame(rows).round(3)
results.to_csv(OUT / "results.csv", index=False)
print()
print(results.to_string(index=False))
