import pandas as pd
import json
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def train_and_evaluate_centralized():
    print("Training centralized baseline model...")
    
    # Load data
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed_data.csv")
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found.")
        return
        
    df = pd.read_csv(data_path)
    X = df.drop("target", axis=1).values
    y = df["target"].values
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train model
    # We use a relatively high max_iter and a standard solver
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    print("--- Centralized Baseline Metrics ---")
    print(f"Accuracy:  {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1 Score:  {f1:.4f}")
    
    metrics = {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix": cm
    }
    
    # Save model and metrics
    base_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    joblib.dump(model, os.path.join(results_dir, "centralized_model.joblib"))
    with open(os.path.join(results_dir, "centralized_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)
        
    print(f"Saved centralized model and metrics to {results_dir}")

if __name__ == "__main__":
    train_and_evaluate_centralized()
