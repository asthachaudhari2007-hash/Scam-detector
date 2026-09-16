# -*- coding: utf-8 -*-
import csv
import json
import os
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.pkl")
KEYWORDS_PATH = os.path.join(BASE_DIR, "top_keywords.json")

# ---- Load data ----
texts, labels = [], []
with open(DATA_PATH, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        texts.append(row["text"])
        labels.append(row["label"])

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# ---- Vectorize ----
vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    min_df=1,
    max_df=0.9,
)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# ---- Train ----
clf = LogisticRegression(max_iter=1000, class_weight="balanced")
clf.fit(X_train_vec, y_train)

# ---- Evaluate ----
y_pred = clf.predict(X_test_vec)
print(classification_report(y_test, y_pred, digits=3))
print(f"F1 (scam class): {f1_score(y_test, y_pred, pos_label='scam'):.3f}")

# ---- Extract top scam-indicating keywords (for explainability) ----
feature_names = vectorizer.get_feature_names_out()
coefs = clf.coef_[0]
positive_class = clf.classes_[1]
if positive_class != "scam":
    coefs = -coefs

top_n = 40
top_idx = coefs.argsort()[::-1][:top_n]
top_keywords = [feature_names[i] for i in top_idx]

with open(KEYWORDS_PATH, "w", encoding="utf-8") as f:
    json.dump(top_keywords, f, indent=2)

# ---- Save model + vectorizer ----
with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)
with open(VECTORIZER_PATH, "wb") as f:
    pickle.dump(vectorizer, f)

print(f"\nSaved model to {MODEL_PATH}")
print(f"Saved vectorizer to {VECTORIZER_PATH}")
print(f"Saved top {top_n} scam keywords to {KEYWORDS_PATH}")
print("\nSample top scam-indicating terms:", top_keywords[:15])