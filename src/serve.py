from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import joblib
import os
from botocore.exceptions import ClientError

app = FastAPI()

# Đọc tên bucket từ biến môi trường
AWS_BUCKET = os.getenv("CLOUD_BUCKET")
AWS_MODEL_KEY = "models/latest/model.pkl"
MODEL_PATH = os.path.expanduser("~/models/model.pkl")


def download_model():
    """Tải file model.pkl từ S3 về máy khi server khởi động."""
    if not AWS_BUCKET:
        print("Warning: CLOUD_BUCKET environment variable not set.")
        return

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    s3 = boto3.client('s3')
    try:
        print(f"Downloading model from s3://{AWS_BUCKET}/{AWS_MODEL_KEY}...")
        s3.download_file(AWS_BUCKET, AWS_MODEL_KEY, MODEL_PATH)
        print(f"Model downloaded to {MODEL_PATH}")
    except ClientError as e:
        print(f"Error downloading model: {e}")
        # If model doesn't exist yet, we might want to skip or handle it
        if not os.path.exists(MODEL_PATH):
             print("Critical: Model file does not exist and could not be downloaded.")


# Gọi hàm này khi module được import
if os.getenv("SKIP_MODEL_DOWNLOAD") != "1":
    download_model()

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None
    print("Warning: Model not loaded because model.pkl was not found.")


class PredictRequest(BaseModel):
    features: list[float]


@app.get("/health")
def health():
    """Endpoint kiểm tra sức khỏe server."""
    return {"status": "ok"}


@app.post("/predict")
def predict(req: PredictRequest):
    """
    Endpoint suy luận.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    if len(req.features) != 12:
        raise HTTPException(status_code=400, detail="Expected 12 features (wine quality)")

    prediction = int(model.predict([req.features])[0])
    
    labels = {0: "thấp", 1: "trung_bình", 2: "cao"}
    label = labels.get(prediction, "không xác định")

    return {"prediction": prediction, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
