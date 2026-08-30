from fastapi import FastAPI, BackgroundTasks, HTTPException
import subprocess
import joblib
import os
import pandas as pd
from pydantic import BaseModel
import sys

app = FastAPI(title="FL ML Service")

class PatientFeatures(BaseModel):
    age: float
    sex: float
    cp: float
    trestbps: float
    chol: float
    fbs: float
    restecg: float
    thalach: float
    exang: float
    oldpeak: float
    slope: float
    ca: float
    thal: float

class ClientStartRequest(BaseModel):
    client_id: int
    csv_data: str

server_process = None

def run_fl_server():
    global server_process
    try:
        if server_process is not None:
            server_process.terminate()
            server_process.wait()
    except Exception:
        pass

    try:
        base_dir = os.path.dirname(__file__)
        script_path = os.path.join(base_dir, "fl", "server.py")
        python_exec = sys.executable
        server_process = subprocess.Popen([python_exec, script_path])
    except Exception as e:
        print(f"Error running server: {e}")

def run_fl_client(client_id: int, data_path: str):
    try:
        base_dir = os.path.dirname(__file__)
        script_path = os.path.join(base_dir, "fl", "client.py")
        python_exec = sys.executable
        subprocess.Popen([python_exec, script_path, "--client-id", str(client_id), "--data-path", data_path])
    except Exception as e:
        print(f"Error running client {client_id}: {e}")

@app.post("/server/start")
async def start_server(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_fl_server)
    return {"message": "Flower server started."}

@app.post("/client/start")
async def start_client(request: ClientStartRequest, background_tasks: BackgroundTasks):
    # Save CSV data to a temporary file
    import tempfile
    
    # We create a persistent temp file since background task needs it
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    temp_path = os.path.join(data_dir, f"temp_hospital_{request.client_id}.csv")
    
    with open(temp_path, 'w') as f:
        f.write(request.csv_data)
        
    background_tasks.add_task(run_fl_client, request.client_id, temp_path)
    return {"message": f"Client {request.client_id} started."}

@app.post("/predict")
async def predict(features: PatientFeatures):
    base_dir = os.path.dirname(__file__)
    model_path = os.path.join(base_dir, "results", "global_model.joblib")
    preprocessor_path = os.path.join(base_dir, "model", "preprocessor.joblib")
    
    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise HTTPException(status_code=503, detail="Model or preprocessor not available.")
    
    try:
        model = joblib.load(model_path)
        preprocessor = joblib.load(preprocessor_path)
        
        feature_dict = features.dict()
        df = pd.DataFrame([feature_dict])
        
        # Apply the preprocessor to transform raw features into one-hot-encoded 28 features
        X_processed = preprocessor.transform(df)
        
        prediction = model.predict(X_processed)
        result = "High Risk" if prediction[0] == 1 else "Low Risk"
        
        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
