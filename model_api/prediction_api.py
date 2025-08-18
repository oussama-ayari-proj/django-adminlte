
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import pickle
import mlflow
from sm1chut.predictions.pred import predict, mae_for_uf
import uvicorn
import os
from typing import Optional

app = FastAPI(title="CHU Prediction API", version="1.0.0")

# Global variables for models
forecaster = None
forecaster_mae = None

class PredictionRequest(BaseModel):
    code_uf: int
    steps: int = 30
    interval: bool = True

class MAERequest(BaseModel):
    code_uf: int
    data_test: Optional[dict] = None

def load_model(artifact_path, run_id, baseurl):
    """Load model from MLflow"""
    mlflow.set_tracking_uri(baseurl)
    mlflow.set_experiment("Default")
    model_uri = f"runs:/{run_id}/{artifact_path}"

    local_path = mlflow.artifacts.download_artifacts(model_uri)

    with open(local_path, "rb") as f:
        forecaster = pickle.load(f)

    return forecaster

@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global forecaster, forecaster_mae

    print("🚀 Loading models...")
    baseurl = "http://mlflow:5000"
    # Load main forecaster
    artifact_path = "pickle_folder/champion_v2.pkl"
    run_id = "b36d4eba7e294105a362aecd7f734101"
    forecaster = load_model(artifact_path, run_id, baseurl)
    print("✅ Main forecaster loaded")

    # Load MAE forecaster
    artifact_path_mae = "pickle_folder/test_mae_v2.pkl"
    run_id_mae = "bd80bab38253485987fe35491525d269"
    forecaster_mae = load_model(artifact_path_mae, run_id_mae, baseurl)
    print("✅ MAE forecaster loaded")

    print("🎉 API ready!")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "CHU Prediction API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "forecaster_loaded": forecaster is not None,
        "mae_forecaster_loaded": forecaster_mae is not None
    }

@app.post("/predict")
async def get_prediction(request: PredictionRequest):
    """Get prediction for a given UF code"""
    try:
        if forecaster is None:
            raise HTTPException(status_code=500, detail="Forecaster model not loaded")

        print(f"🔮 Making prediction for UF {request.code_uf} with steps {request.steps} and interval {request.interval}")
        result = predict(str(request.code_uf), forecaster, request.steps, interval=request.interval)
        dates = result.index.tolist()
        # add date as a field in the result
        formatted_dates = [date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date).split('T')[0] for date in dates]
        result['dates'] = formatted_dates
        # Convert numpy arrays to lists for JSON serialization
        if isinstance(result, pd.DataFrame):
            result_dict = result.to_dict(orient='records')
        elif isinstance(result, np.ndarray):
            result_dict = result.tolist()
        else:
            result_dict = result

        return {
            
            "prediction": result_dict,
            
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/mae")
async def get_mae(request: MAERequest):
    """Get MAE for a given UF code"""
    try:
        if forecaster_mae is None:
            raise HTTPException(status_code=500, detail="MAE forecaster model not loaded")

        # Convert data_test dict back to DataFrame if provided
        data_test_df = None
        if request.data_test is not None:
            try:
                # If data_test is in the format {'data': [...], 'columns': [...]}
                if isinstance(request.data_test, dict) and 'data' in request.data_test:
                    data_test_df = pd.DataFrame(
                        request.data_test['data'],
                        columns=request.data_test.get('columns', None)
                    )
                else:
                    # If data_test is a simple dict, convert directly
                    data_test_df = pd.DataFrame(request.data_test)
                
                print(f"📊 Converted data_test to DataFrame with shape: {data_test_df.shape}")
                
            except Exception as conv_error:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error converting data_test to DataFrame: {str(conv_error)}"
                )

        # Calculate MAE
        data_test_df['date'] = pd.to_datetime(data_test_df['date'])
        
        result = mae_for_uf(str(request.code_uf), forecaster_mae, data_test_df)

        mae_keys = []
        mae_values = []
        
        for key, value in result.items():
            # Convert numpy types to Python types for JSON serialization
            if isinstance(value, (np.ndarray, pd.Series)):
                converted_value = value.tolist()
            elif isinstance(value, np.number):
                converted_value = float(value)
            elif isinstance(value, (int, float, str, bool, type(None))):
                converted_value = value
            else:
                converted_value = str(value)
            
            mae_keys.append(str(key))
            mae_values.append(converted_value)
        
        return {
            "mae_keys": mae_keys,
            "mae_values": mae_values,
        }


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MAE calculation error: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
