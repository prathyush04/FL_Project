import argparse
import warnings
import flwr as fl
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import log_loss, accuracy_score

warnings.filterwarnings("ignore")

# Expected UCI Cleveland Heart Disease columns
UCI_FEATURE_COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

# Framingham → UCI column mapping (best-effort approximation)
FRAMINGHAM_TO_UCI = {
    "TenYearCHD": "target",
    "age": "age",
    "male": "sex",
    "totChol": "chol",
    "sysBP": "trestbps",
    "heartRate": "thalach",
    "diabetes": "fbs",
    "glucose": "oldpeak",        # rough approximation
    "BMI": None,                  # no UCI equivalent — dropped
    "education": None,
    "currentSmoker": None,
    "cigsPerDay": None,
    "BPMeds": None,
    "prevalentStroke": None,
    "prevalentHyp": None,
    "diaBP": None,
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes uploaded CSVs to match UCI Heart Disease format with a 'target' column.
    Supports:
      - UCI Cleveland format (columns: age, sex, cp, ..., target)
      - Framingham format (columns: male, age, TenYearCHD, ...)
      - Already-processed format (numeric column names 0..27 + target)
    """
    cols = set(df.columns)

    # Already has 'target' and UCI features → use as-is
    if "target" in cols and "age" in cols and "sex" in cols:
        # Keep only UCI feature cols + target, drop anything else
        keep = [c for c in UCI_FEATURE_COLUMNS if c in df.columns] + ["target"]
        return df[keep].dropna()

    # Framingham dataset
    if "TenYearCHD" in cols:
        renamed = {}
        for fk, uci_k in FRAMINGHAM_TO_UCI.items():
            if uci_k and fk in df.columns:
                renamed[fk] = uci_k
        df = df.rename(columns=renamed)
        # Fill missing UCI columns with median/mode
        for col in UCI_FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0
        return df[UCI_FEATURE_COLUMNS + ["target"]].dropna()

    # Already numeric (processed_data.csv format: 0..27 + target)
    if "target" in cols:
        return df.dropna()

    raise ValueError(
        f"Unrecognized CSV format. Expected columns with 'target' label. Got: {list(df.columns)}"
    )


class HeartDiseaseClient(fl.client.NumPyClient):
    def __init__(self, model, X_train, y_train, X_test, y_test):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def get_parameters(self, config):
        if hasattr(self.model, "coefs_"):
            return [val for val in self.model.coefs_] + [val for val in self.model.intercepts_]
        else:
            input_size = self.X_train.shape[1]
            hidden_size = 16
            output_size = 1
            return [
                np.zeros((input_size, hidden_size)),
                np.zeros((hidden_size, output_size)),
                np.zeros(hidden_size),
                np.zeros(output_size)
            ]

    def set_parameters(self, parameters):
        self.model.coefs_ = [parameters[0], parameters[1]]
        self.model.intercepts_ = [parameters[2], parameters[3]]

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        self.model.fit(self.X_train, self.y_train)
        print(f"Training finished for this round.")
        return self.get_parameters(config={}), len(self.X_train), {}

    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        y_pred = self.model.predict(self.X_test)
        y_prob = self.model.predict_proba(self.X_test)

        loss = log_loss(self.y_test, y_prob)
        accuracy = accuracy_score(self.y_test, y_pred)

        return float(loss), len(self.X_test), {"accuracy": float(accuracy)}


def load_data(data_path):
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found at {data_path}")

    df = pd.read_csv(data_path)
    print(f"Loaded CSV with columns: {list(df.columns)}")

    # Normalize to UCI format
    df = normalize_columns(df)
    print(f"After normalization — shape: {df.shape}, columns: {list(df.columns)}")

    # Load preprocessor
    preprocessor_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "model", "preprocessor.joblib"
    )

    if os.path.exists(preprocessor_path) and set(UCI_FEATURE_COLUMNS).issubset(set(df.columns)):
        # Apply the same preprocessor used during centralized training
        preprocessor = joblib.load(preprocessor_path)
        X = preprocessor.transform(df[UCI_FEATURE_COLUMNS])
        if hasattr(X, "toarray"):
            X = X.toarray()
        y = df["target"].values
        print(f"Applied preprocessor → X shape: {X.shape}")
    else:
        # Fallback: use raw numeric values
        y = df["target"].values
        X = df.drop("target", axis=1).values
        print(f"Using raw features → X shape: {X.shape}")

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description="Flower Client")
    parser.add_argument("--client-id", type=int, required=True, help="ID of the client (1-4)")
    parser.add_argument("--data-path", type=str, required=True, help="Path to the training CSV file")
    parser.add_argument("--server-address", type=str, default="127.0.0.1:8081", help="Address of the server")
    args = parser.parse_args()

    X_train, y_train, X_test, y_test = load_data(args.data_path)

    model = MLPClassifier(hidden_layer_sizes=(16,), max_iter=1, warm_start=True, random_state=42)

    # Initialize the model's internal state properly using partial_fit
    model.partial_fit(X_train[:2], y_train[:2], classes=np.array([0, 1]))

    client = HeartDiseaseClient(model, X_train, y_train, X_test, y_test)
    fl.client.start_client(server_address=args.server_address, client=client.to_client())


if __name__ == "__main__":
    main()
