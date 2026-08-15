import pandas as pd
import numpy as np
import joblib
import os
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def fetch_and_preprocess_data():
    print("Downloading and reading UCI Heart Disease dataset (Cleveland)...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    
    # Define columns
    columns = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", 
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
    ]
    
    # Modify the dataset
    df = pd.read_csv(url, header=None, names=columns, na_values="?")
    
    print(f"Dataset shape before cleaning: {df.shape}")
    
    # Target Binarization
    df['target'] = (df['target'] > 0).astype(int)
    
    # features and targets splitting
    X = df.drop("target", axis=1)
    y = df["target"]
    
    # defining features
    categorical_cols = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
    numerical_cols = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    
    # preprocessing pipelines
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
    
    # Fit and transform the data
    X_processed = preprocessor.fit_transform(X)
    
    
    # saving the preprocessor
    model_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(preprocessor, os.path.join(model_dir, "preprocessor.joblib"))
    print(f"Saved preprocessor to {model_dir}/preprocessor.joblib")
    
    # Save processed data for centralized and federated simulations
    if hasattr(X_processed, "toarray"):
        X_processed = X_processed.toarray()
        
    processed_df = pd.DataFrame(X_processed)
    processed_df["target"] = y.values
    
    data_dir = os.path.dirname(__file__)
    processed_csv_path = os.path.join(data_dir, "processed_data.csv")
    processed_df.to_csv(processed_csv_path, index=False)
    print(f"Saved processed dataset to {processed_csv_path} with shape {processed_df.shape}")

if __name__ == "__main__":
    fetch_and_preprocess_data()
