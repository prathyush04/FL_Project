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

# Expected UCI Cleveland Heart Disease columns (model was built around these)
UCI_FEATURE_COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                        "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

# Framingham column -> UCI column mapping (best-effort)
FRAMINGHAM_TO_UCI = {
    "male": "sex",
    "totChol": "chol",
    "sysBP": "trestbps",
    "heartRate": "thalach",
    "diabetes": "fbs",
    "glucose": "oldpeak",
}


def normalize_columns(df):
    """
    Normalizes an uploaded hospital CSV to UCI Heart Disease format.
    Handles three formats:
      1. UCI Cleveland  (columns: age, sex, cp, trestbps, chol, ..., target)
      2. Framingham     (columns: male, age, TenYearCHD, ...)
      3. Pre-processed  (numeric column names 0..27 + target)
    Returns a DataFrame with UCI feature columns + 'target'.
    """
    cols = set(df.columns)

    # ---- Format 1: already has proper UCI columns + target ----
    if "target" in cols and "sex" in cols and "cp" in cols:
        keep = [c for c in UCI_FEATURE_COLUMNS if c in df.columns] + ["target"]
        result = df[keep].dropna()
        print(f"Detected UCI format. Shape: {result.shape}")
        return result

    # ---- Format 2: Framingham (TenYearCHD OR already renamed to target) ----
    if "TenYearCHD" in cols or ("male" in cols and "target" in cols):
        # Rename TenYearCHD -> target if needed
        if "TenYearCHD" in cols:
            df = df.rename(columns={"TenYearCHD": "target"})

        # Rename Framingham columns to UCI equivalents
        df = df.rename(columns=FRAMINGHAM_TO_UCI)

        # Fill any missing UCI columns with zeros
        for col in UCI_FEATURE_COLUMNS:
            if col not in df.columns:
                df[col] = 0

        result = df[UCI_FEATURE_COLUMNS + ["target"]].dropna()
        print(f"Detected Framingham format. Shape: {result.shape}")
        return result

    # ---- Format 3: pre-processed numeric columns ----
    if "target" in cols:
        result = df.dropna()
        print(f"Detected pre-processed format. Shape: {result.shape}")
        return result

    raise ValueError(
        f"Unrecognized CSV format. Expected a 'target' label column. "
        f"Got columns: {sorted(cols)}"
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
        print("Training finished for this round.")
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
    print(f"Loaded CSV with {len(df)} rows and columns: {list(df.columns)}")

    # Normalize to UCI format
    df = normalize_columns(df)

    # Load preprocessor and apply it (same transform used at prediction time)
    preprocessor_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "model", "preprocessor.joblib"
    )

    uci_cols_present = all(c in df.columns for c in UCI_FEATURE_COLUMNS)

    if os.path.exists(preprocessor_path) and uci_cols_present:
        preprocessor = joblib.load(preprocessor_path)
        X = preprocessor.transform(df[UCI_FEATURE_COLUMNS])
        if hasattr(X, "toarray"):
            X = X.toarray()
        y = df["target"].values
        print(f"Preprocessor applied. Feature shape: {X.shape}")
    else:
        # Fallback: raw numeric values (pre-processed format)
        y = df["target"].values
        X = df.drop("target", axis=1).values
        print(f"Using raw features. Shape: {X.shape}")

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description="Flower Client")
    parser.add_argument("--client-id", type=int, required=True, help="ID of the client (1-4)")
    parser.add_argument("--data-path", type=str, default=None, help="Path to the training CSV file")
    parser.add_argument("--server-address", type=str, default="127.0.0.1:8081", help="Address of the server")
    args = parser.parse_args()

    data_path = args.data_path
    if not data_path:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(base_dir, "data", f"hospital_{args.client_id}", "train.csv")

    X_train, y_train, X_test, y_test = load_data(data_path)

    model = MLPClassifier(hidden_layer_sizes=(16,), max_iter=1, warm_start=True, random_state=42)
    
    # Initialize with at least one sample of each class if available
    unique_classes = np.unique(y_train)
    if len(unique_classes) > 1:
        init_indices = [np.where(y_train == c)[0][0] for c in [0, 1] if c in unique_classes]
        model.partial_fit(X_train[init_indices], y_train[init_indices], classes=np.array([0, 1]))
    else:
        # Fallback dummy sample
        dummy_X = np.zeros((2, X_train.shape[1]))
        dummy_y = np.array([0, 1])
        model.partial_fit(dummy_X, dummy_y, classes=np.array([0, 1]))

    client = HeartDiseaseClient(model, X_train, y_train, X_test, y_test)
    fl.client.start_client(server_address=args.server_address, client=client.to_client())


if __name__ == "__main__":
    main()
