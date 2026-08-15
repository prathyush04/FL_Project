import argparse
import warnings
import flwr as fl
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, accuracy_score

warnings.filterwarnings("ignore")

# Define Flower client
class HeartDiseaseClient(fl.client.NumPyClient):
    def __init__(self, model, X_train, y_train, X_test, y_test):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def get_parameters(self, config):
        if hasattr(self.model, "coef_"):
            return [self.model.coef_, self.model.intercept_]
        else:
            # Return zeros if not initialized
            return [np.zeros((1, self.X_train.shape[1])), np.zeros(1)]

    def set_parameters(self, parameters):
        self.model.coef_ = parameters[0]
        self.model.intercept_ = parameters[1]
        # To avoid sklearn exceptions if classes_ is missing
        if not hasattr(self.model, "classes_"):
            self.model.classes_ = np.array([0, 1])

    def fit(self, parameters, config):
        self.set_parameters(parameters)
        # Use warm_start=True to continue training from global parameters
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


def load_data(client_id):
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", f"hospital_{client_id}")
    data_path = os.path.join(data_dir, "train.csv")
    
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data not found for hospital_{client_id} at {data_path}")
        
    df = pd.read_csv(data_path)
    X = df.drop("target", axis=1).values
    y = df["target"].values
    
    # We do a simple 80/20 split on the client side for local evaluation
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, y_train, X_test, y_test


def main():
    parser = argparse.ArgumentParser(description="Flower Client")
    parser.add_argument("--client-id", type=int, required=True, help="ID of the client (1-4)")
    parser.add_argument("--server-address", type=str, default="127.0.0.1:8080", help="Address of the server")
    args = parser.parse_args()

    # Load local dataset
    X_train, y_train, X_test, y_test = load_data(args.client_id)

    # Initialize model
    # warm_start=True allows iterative fitting without resetting parameters
    model = LogisticRegression(max_iter=1, warm_start=True, solver="saga", random_state=42)
    
    # We need to initialize the model with the correct shape before receiving parameters
    # Alternatively, the server sets them first. But sklearn requires classes_ to be set.
    model.classes_ = np.array([0, 1])
    # Give it a dummy shape for parameters
    model.coef_ = np.zeros((1, X_train.shape[1]))
    model.intercept_ = np.zeros(1)

    # Start client
    client = HeartDiseaseClient(model, X_train, y_train, X_test, y_test)
    
    # Note: flwr < 1.0 vs flwr >= 1.0 syntax. Assuming modern flwr
    fl.client.start_client(server_address=args.server_address, client=client.to_client())

if __name__ == "__main__":
    main()
