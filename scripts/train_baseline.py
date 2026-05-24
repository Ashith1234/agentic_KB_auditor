import os
import pandas as pd

from src.evaluation.baseline_model import BaselineRiskModel


def main():
    os.makedirs("data/models", exist_ok=True)

    df = pd.read_csv("data/training/baseline_training.csv")

    texts = df["text"].tolist()
    labels = df["label"].tolist()

    model = BaselineRiskModel()
    model.train(texts, labels)

    print("Baseline Logistic Regression model trained successfully.")


if __name__ == "__main__":
    main()
