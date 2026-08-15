import pandas as pd
import numpy as np
import os

def split_data(num_clients=4):
    print(f"Splitting data for {num_clients} simulated hospitals (clients)...")
    
    data_dir = os.path.dirname(__file__)
    processed_csv_path = os.path.join(data_dir, "processed_data.csv")
    
    if not os.path.exists(processed_csv_path):
        print(f"Error: {processed_csv_path} not found. Run preprocess.py first.")
        return
        
    df = pd.read_csv(processed_csv_path)
    print(f"Loaded dataset with shape {df.shape}")
    
    # Shuffle the dataset (IID splitting)
    df_shuffled = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split into chunks
    chunks = [df_shuffled.iloc[idx] for idx in np.array_split(range(len(df_shuffled)), num_clients)]
    
    for i, chunk in enumerate(chunks, 1):
        client_dir = os.path.join(data_dir, f"hospital_{i}")
        os.makedirs(client_dir, exist_ok=True)
        
        chunk_path = os.path.join(client_dir, "train.csv")
        chunk.to_csv(chunk_path, index=False)
        print(f"Saved hospital_{i} data with shape {chunk.shape} to {chunk_path}")

if __name__ == "__main__":
    split_data()
