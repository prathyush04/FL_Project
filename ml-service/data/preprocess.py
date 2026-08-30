import pandas as pd
import numpy as np
import os
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def get_framingham_path():
    data_dir = os.path.dirname(__file__)
    possible_paths = [
        os.path.join(data_dir, "framingham.csv"),
        os.path.join(os.path.dirname(data_dir), "data", "framingham.csv"),
        os.path.join(os.path.dirname(os.path.dirname(data_dir)), "data", "framingham.csv"),
        "framingham.csv"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def fetch_and_preprocess_data(num_clients=4):
    print("Locating Framingham Heart Disease dataset...")
    csv_path = get_framingham_path()
    
    if not csv_path or not os.path.exists(csv_path):
        print("Error: framingham.csv not found in data directories.")
        return

    print(f"Reading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Dataset shape before cleaning: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    # Ensure label column is 'TenYearCHD' or 'target'
    if "TenYearCHD" in df.columns:
        df["target"] = df["TenYearCHD"].astype(int)
    elif "target" not in df.columns:
        raise ValueError("Could not find TenYearCHD or target column in dataset.")

    # Drop any null targets if present
    df = df.dropna(subset=["target"]).reset_index(drop=True)

    # 1. Split RAW Framingham dataset across 4 hospitals (for UI upload and FL simulation)
    # Shuffle first with fixed seed for reproducibility (IID partition)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    data_dir = os.path.dirname(__file__)
    
    chunks = [df_shuffled.iloc[idx] for idx in np.array_split(range(len(df_shuffled)), num_clients)]
    
    print(f"\n--- Generating 4 Hospital Datasets (Framingham) ---")
    for i, chunk in enumerate(chunks, 1):
        client_dir = os.path.join(data_dir, f"hospital_{i}")
        os.makedirs(client_dir, exist_ok=True)
        chunk_path = os.path.join(client_dir, "train.csv")
        chunk.to_csv(chunk_path, index=False)
        print(f"Saved hospital_{i} train.csv: {chunk.shape[0]} rows -> {chunk_path}")

    # 2. Build Preprocessor for Framingham / UCI compatible pipeline
    # Map Framingham features to the model schema
    framingham_to_uci = {
        "male": "sex",
        "totChol": "chol",
        "sysBP": "trestbps",
        "heartRate": "thalach",
        "diabetes": "fbs",
        "glucose": "oldpeak"
    }
    
    df_mapped = df_shuffled.rename(columns=framingham_to_uci).copy()
    
    uci_cols = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
                "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    
    for c in uci_cols:
        if c not in df_mapped.columns:
            df_mapped[c] = 0.0

    X = df_mapped[uci_cols]
    y = df_mapped["target"]

    categorical_cols = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
    numerical_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]

    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_cols),
            ("cat", categorical_transformer, categorical_cols)
        ]
    )

    X_processed = preprocessor.fit_transform(X)
    if hasattr(X_processed, "toarray"):
        X_processed = X_processed.toarray()

    # Save fitted preprocessor
    model_dir = os.path.join(os.path.dirname(data_dir), "model")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(preprocessor, os.path.join(model_dir, "preprocessor.joblib"))
    print(f"\nSaved updated preprocessor to {model_dir}/preprocessor.joblib")

    # Save processed dataset for centralized baseline
    processed_df = pd.DataFrame(X_processed)
    processed_df["target"] = y.values
    processed_csv_path = os.path.join(data_dir, "processed_data.csv")
    processed_df.to_csv(processed_csv_path, index=False)
    print(f"Saved processed_data.csv with shape {processed_df.shape} to {processed_csv_path}")
    print("\nPreprocess & 4-hospital generation completed successfully!")

if __name__ == "__main__":
    fetch_and_preprocess_data()
