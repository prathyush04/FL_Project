import pandas as pd
import numpy as np
import os
from preprocess import fetch_and_preprocess_data

def split_data(num_clients=4):
    print(f"Executing full data preprocessing and splitting for {num_clients} hospitals...")
    fetch_and_preprocess_data(num_clients=num_clients)

if __name__ == "__main__":
    split_data()
