# Federated Learning ML Service

This directory contains the Machine Learning service for the Federated Learning Heart Disease Prediction project. 
It uses **FastAPI** to expose REST endpoints and the **Flower (flwr)** framework to orchestrate the federated learning process.

## Technologies Used
- **Python 3**
- **FastAPI**: For providing REST API endpoints to trigger training and make predictions.
- **Flower (`flwr`)**: A federated learning framework used for training models collaboratively without sharing sensitive data.
- **scikit-learn**: Used for the underlying machine learning models (specifically `MLPClassifier`).
- **pandas & numpy**: For data manipulation and processing.

## Project Structure
- `api.py`: The FastAPI application acting as the entry point to interact with the ML models.
- `fl/`: Contains the federated learning logic.
  - `server.py`: The FL aggregation server using `FedProx` strategy.
  - `client.py`: The FL client that trains a local model on hospital-specific data.
  - `config.py`: Configuration parameters for FL (number of rounds, clients).
- `model/centralized.py`: A script to train a centralized baseline model for comparison.
- `run_simulation.py`: A local simulation script to run the server and multiple clients sequentially for testing.
- `results/`: Directory where the trained global model (`global_model.joblib`) and metrics are saved.

## Setup & Running

1. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the local simulation (Test FL):**
   ```bash
   python run_simulation.py
   ```

4. **Start the FastAPI Server:**
   ```bash
   python api.py
   ```
   The API will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

## API Endpoints
- `POST /server/start`: Starts the FL aggregation server in the background.
- `POST /client/start`: Starts an FL client using provided CSV data.
- `POST /predict`: Takes patient features and returns a heart disease risk prediction ("High Risk" or "Low Risk") using the globally trained model.
