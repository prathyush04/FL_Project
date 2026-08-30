import argparse
import warnings
import flwr as fl
import numpy as np
import pandas as pd
import os
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import log_loss, accuracy_score

warnings.filterwarnings("ignore")

class HeartDiseaseClient(fl.client.NumPyClient):
    def __init__(self, model, X_train, y_train, X_test, y_test):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def get_parameters(self, config):
        if hasattr(self.model, "coefs_"):
            # Return weights and biases as a single list of numpy arrays
            return [val for val in self.model.coefs_] + [val for val in self.model.intercepts_]
        else:
            # If model is not initialized, return empty arrays based on expected shape
            # 1 hidden layer with 16 units
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
        # We expect 4 parameters: W1, W2, b1, b2
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
    X = df.drop("target", axis=1).values
    y = df["target"].values
    
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
