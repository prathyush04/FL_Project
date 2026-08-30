from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import joblib
import os
import pandas as pd
from pydantic import BaseModel
import sys

app = FastAPI(title="FL ML Service")

# Allow CORS from Spring backend and any frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directories - MODEL_DIR env var points to Render Disk or local results/
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.environ.get("MODEL_DIR", os.path.join(BASE_DIR, "results"))
os.makedirs(MODEL_DIR, exist_ok=True)

# Local data directory for uploaded hospital CSVs
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)


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
        script_path = os.path.join(BASE_DIR, "fl", "server.py")
        python_exec = sys.executable
        env = os.environ.copy()
        env["MODEL_DIR"] = MODEL_DIR
        server_process = subprocess.Popen([python_exec, script_path], env=env)
    except Exception as e:
        print(f"Error running server: {e}")


def run_fl_client(client_id: int, data_path: str):
    try:
        script_path = os.path.join(BASE_DIR, "fl", "client.py")
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
    temp_path = os.path.join(DATA_DIR, f"temp_hospital_{request.client_id}.csv")
    with open(temp_path, 'w') as f:
        f.write(request.csv_data)
    background_tasks.add_task(run_fl_client, request.client_id, temp_path)
    return {"message": f"Client {request.client_id} started."}


@app.post("/predict")
async def predict(features: PatientFeatures):
    model_path = os.path.join(MODEL_DIR, "global_model.joblib")
    preprocessor_path = os.path.join(BASE_DIR, "model", "preprocessor.joblib")

    if not os.path.exists(model_path) or not os.path.exists(preprocessor_path):
        raise HTTPException(status_code=503, detail="Model not available. Please run federated training first.")

    try:
        model = joblib.load(model_path)
        preprocessor = joblib.load(preprocessor_path)

        feature_dict = features.dict()
        df = pd.DataFrame([feature_dict])
        X_processed = preprocessor.transform(df)

        prediction = model.predict(X_processed)
        result = "High Risk" if prediction[0] == 1 else "Low Risk"

        return {"prediction": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    model_path = os.path.join(MODEL_DIR, "global_model.joblib")
    return {
        "status": "ok",
        "model_available": os.path.exists(model_path),
        "model_dir": MODEL_DIR
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
