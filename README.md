# Federated Learning Heart Disease Prediction System

Welcome to the Federated Learning (FL) Heart Disease Prediction project. This system demonstrates a privacy-preserving approach to training machine learning models across multiple independent entities (like hospitals) without requiring them to share sensitive patient data.

## Project Overview

Traditional machine learning requires centralizing data, which poses significant privacy and compliance risks in healthcare. This project uses **Federated Learning** to send the *model* to the *data*, rather than the other way around. 

The architecture consists of three main decoupled services:

1. **Frontend (`/frontend`)**: A modern React application that provides the user interface for hospitals to join the federated network, trigger training, and request heart disease risk predictions.
2. **Backend (`/Spring_Backend`)**: A Java Spring Boot application that manages users, authentication (JWT), data persistence, and acts as the orchestrator and gateway between the UI and the ML service.
3. **ML Service (`/ml-service`)**: A Python FastAPI service powered by the `Flower (flwr)` framework. It manages the federated aggregation server and client nodes to train a global `MLPClassifier` neural network model.

## Architecture & Workflow

1. **Client Interaction**: Users interact with the React **Frontend**, uploading local datasets or requesting predictions.
2. **API Gateway & Auth**: The **Spring Backend** receives these requests, validates JWT tokens, stores metadata, and forwards machine learning specific tasks to the Python ML Service.
3. **Federated Training**: 
    - The **ML Service** starts a background Flower Server.
    - It provisions background Flower Clients, assigning them the uploaded datasets.
    - The clients train a neural network locally and send only the learned weights back to the server.
    - The server aggregates these weights (FedProx strategy) into a global model.
4. **Inference**: Once the global model is trained, the ML Service can accept new patient features from the frontend and return a "High Risk" or "Low Risk" prediction.

## Getting Started

To run the full stack locally, you will need to start all three services.

### 1. Start the ML Service
Navigate to `ml-service/`:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python api.py
```
*(Runs on `http://localhost:8000`)*

### 2. Start the Spring Backend
Navigate to `Spring_Backend/`:
```bash
./mvnw clean install
./mvnw spring-boot:run
```
*(Runs on `http://localhost:8080`)*

### 3. Start the Frontend
Navigate to `frontend/`:
```bash
npm install
npm run dev
```
*(Runs on `http://localhost:5173`)*

## Documentation
For more detailed information on each component, refer to the individual `README.md` files located in their respective directories:
- [ML Service README](./ml-service/README.md)
- [Spring Backend README](./Spring_Backend/README.md)
- [Frontend README](./frontend/README.md)
