import os
import boto3
from minio import Minio
from dotenv import load_dotenv
import io

load_dotenv()

def upload_model_to_minio():
    print("Uploading model to MinIO.")
    
    minio_client = Minio(
        endpoint=os.getenv('MINIO_ENDPOINT').replace('http://', ''),
        access_key=os.getenv('MINIO_ACCESS_KEY'),
        secret_key=os.getenv('MINIO_SECRET_KEY'),
        secure=False
    )
    
    bucket_name = os.getenv('MINIO_BUCKET')
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
    
    model_path = "machine_learning/random_forest_model.pkl"
    scaler_path = "machine_learning/scaler.pkl"
    
    with open(model_path, 'rb') as model_file:
        model_data = model_file.read()
        model_size = len(model_data)
        model_stream = io.BytesIO(model_data)
        
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name="models/fraud_model.pkl",
            data=model_stream,
            length=model_size,
            content_type='application/octet-stream'
        )
    
    with open(scaler_path, 'rb') as scaler_file:
        scaler_data = scaler_file.read()
        scaler_size = len(scaler_data)
        scaler_stream = io.BytesIO(scaler_data)
        
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name="models/scaler.pkl",
            data=scaler_stream,
            length=scaler_size,
            content_type='application/octet-stream'
        )
    
    print(f"Model and scaler uploaded to MinIO bucket: {bucket_name}")

if __name__ == "__main__":
    upload_model_to_minio()