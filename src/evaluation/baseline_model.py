from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib


class BaselineRiskModel:
    def __init__(self, model_path="data/models/baseline_risk_model.pkl"):
        self.model_path = model_path
        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(max_features=5000)),
            ("classifier", LogisticRegression(max_iter=1000))
        ])

    def train(self, texts, labels):
        self.pipeline.fit(texts, labels)
        joblib.dump(self.pipeline, self.model_path)

    def load(self):
        self.pipeline = joblib.load(self.model_path)

    def predict_risk(self, query, answer, chunks):
        combined_chunks = " ".join(chunks)
        input_text = query + " " + answer + " " + combined_chunks

        prediction = self.pipeline.predict([input_text])[0]
        probability = self.pipeline.predict_proba([input_text])[0][1]

        return {
            "label": "RISKY" if prediction == 1 else "SAFE",
            "risk_score": float(probability)
        }
