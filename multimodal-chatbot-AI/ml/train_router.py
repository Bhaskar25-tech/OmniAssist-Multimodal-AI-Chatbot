"""Trains your own router (TF-IDF + Logistic Regression).
Run from project root:  python -m ml.train_router
Add more rows to ml/router_data.csv (100+ per label) for better accuracy."""
import os

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

HERE = os.path.dirname(os.path.abspath(__file__))

df = pd.read_csv(os.path.join(HERE, "router_data.csv"))
Xtr, Xte, ytr, yte = train_test_split(df.text, df.label, test_size=0.25,
                                      random_state=42, stratify=df.label)
model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=1000))
model.fit(Xtr, ytr)
print(classification_report(yte, model.predict(Xte), zero_division=0))

model.fit(df.text, df.label)  # final model on all data
joblib.dump(model, os.path.join(HERE, "router_model.joblib"))
print("Saved ml/router_model.joblib")
