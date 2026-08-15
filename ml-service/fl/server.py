import flwr as fl
import joblib
import json
import os
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from flwr.common import Metrics
from sklearn.linear_model import LogisticRegression

import config

def get_evaluate_fn():
    # Return a function to evaluate the global model on a central test set if we have one.
    # We can use the processed_data.csv for a centralized evaluation of the global model.
    # Alternatively, we can just rely on client evaluation metrics.
    # Let's rely on client evaluation metrics for FedAvg.
    return None

def fit_metrics_aggregation_fn(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # We don't necessarily return metrics from fit in the client, but if we do:
    return {}

def evaluate_metrics_aggregation_fn(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    # Aggregate accuracy
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    
    return {"accuracy": sum(accuracies) / sum(examples)}

def save_global_model_and_metrics(history):
    print("Saving global model and metrics...")
    
    # In Flower, the Strategy has the weights, but it's easier to extract from History or by saving in a custom strategy.
    # For a simple script, we just save the metrics here. The actual model weights can be saved by subclassing FedAvg
    # or passing a callback. Since this is an MVP, we'll save the metrics to federated_metrics.csv.
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Process history
    rounds, losses = zip(*history.losses_distributed)
    _, accuracies = zip(*history.metrics_distributed["accuracy"])
    
    df_metrics = pd.DataFrame({
        "round": rounds,
        "loss": losses,
        "accuracy": accuracies
    })
    
    metrics_path = os.path.join(results_dir, "federated_metrics.csv")
    df_metrics.to_csv(metrics_path, index=False)
    print(f"Saved federated metrics to {metrics_path}")

class SaveModelStrategy(fl.server.strategy.FedAvg):
    def aggregate_fit(self, server_round, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
        
        if aggregated_parameters is not None:
            # Convert parameters back to ndarrays
            params = fl.common.parameters_to_ndarrays(aggregated_parameters)
            
            # Save the model
            model = LogisticRegression()
            model.classes_ = np.array([0, 1])
            model.coef_ = params[0]
            model.intercept_ = params[1]
            
            base_dir = os.path.dirname(os.path.dirname(__file__))
            results_dir = os.path.join(base_dir, "results")
            model_path = os.path.join(results_dir, "global_model.joblib")
            joblib.dump(model, model_path)
            # print(f"Saved global model for round {server_round} to {model_path}")
            
        return aggregated_parameters, aggregated_metrics

def main():
    # Define strategy
    strategy = SaveModelStrategy(
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=config.NUM_CLIENTS,
        min_evaluate_clients=config.NUM_CLIENTS,
        min_available_clients=config.NUM_CLIENTS,
        evaluate_metrics_aggregation_fn=evaluate_metrics_aggregation_fn,
        initial_parameters=None,
    )
    
    # Start server
    print(f"Starting Flower server for {config.NUM_ROUNDS} rounds...")
    history = fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=config.NUM_ROUNDS),
        strategy=strategy,
    )
    
    # Save metrics
    save_global_model_and_metrics(history)

if __name__ == "__main__":
    main()
