import flwr as fl
import joblib
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from flwr.common import Metrics
from sklearn.neural_network import MLPClassifier

import config

def evaluate_metrics_aggregation_fn(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    return {"accuracy": sum(accuracies) / sum(examples)}

def save_global_model_and_metrics(history):
    print("Saving global model and metrics...")
    results_dir = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "results"))
    os.makedirs(results_dir, exist_ok=True)

    if not history.losses_distributed or not history.metrics_distributed:
        print("No metrics to save.")
        return

    rounds, losses = zip(*history.losses_distributed)
    _, accuracies = zip(*history.metrics_distributed["accuracy"])

    df_metrics = pd.DataFrame({"round": rounds, "loss": losses, "accuracy": accuracies})
    metrics_path = os.path.join(results_dir, "federated_metrics.csv")
    df_metrics.to_csv(metrics_path, index=False)
    print(f"Saved federated metrics to {metrics_path}")


class SaveModelStrategy(fl.server.strategy.FedProx):
    def aggregate_fit(self, server_round, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(
            server_round, results, failures
        )

        if aggregated_parameters is not None:
            params = fl.common.parameters_to_ndarrays(aggregated_parameters)

            model = MLPClassifier(hidden_layer_sizes=(16,), random_state=42)
            # Initialize with dummy data matching preprocessor output (28 features)
            dummy_X = np.zeros((2, 28))
            dummy_y = np.array([0, 1])
            model.partial_fit(dummy_X, dummy_y, classes=np.array([0, 1]))
            
            model.coefs_ = [params[0], params[1]]
            model.intercepts_ = [params[2], params[3]]

            results_dir = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "results"))
            model_path = os.path.join(results_dir, "global_model.joblib")
            joblib.dump(model, model_path)

        return aggregated_parameters, aggregated_metrics


def main():
    # Try to load existing model for continuous training
    initial_parameters = None
    results_dir = os.environ.get("MODEL_DIR", os.path.join(os.path.dirname(os.path.dirname(__file__)), "results"))
    model_path = os.path.join(results_dir, "global_model.joblib")
    
    if os.path.exists(model_path):
        try:
            existing_model = joblib.load(model_path)
            if hasattr(existing_model, 'coefs_') and len(existing_model.coefs_) >= 2 and existing_model.coefs_[0].shape[0] == 28:
                ndarrays = [
                    existing_model.coefs_[0], 
                    existing_model.coefs_[1], 
                    existing_model.intercepts_[0], 
                    existing_model.intercepts_[1]
                ]
                initial_parameters = fl.common.ndarrays_to_parameters(ndarrays)
                print("Loaded existing global model (28 features) to distribute to hospitals!")
            else:
                print("Existing model has incompatible shape or is uninitialized, starting fresh with 28 features.")
        except Exception as e:
            print(f"Could not load existing model, starting fresh: {e}")

    # Define strategy
    strategy = SaveModelStrategy(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=config.NUM_CLIENTS,
        min_evaluate_clients=config.NUM_CLIENTS,
        min_available_clients=config.NUM_CLIENTS,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=initial_parameters,
        proximal_mu=1.0, # Adding proximal term for FedProx
    )

    print(f"Starting Flower server for {config.NUM_ROUNDS} rounds...")
    history = fl.server.start_server(
        server_address="0.0.0.0:8081",
        config=fl.server.ServerConfig(num_rounds=config.NUM_ROUNDS),
        strategy=strategy,
    )

    save_global_model_and_metrics(history)

if __name__ == "__main__":
    main()
