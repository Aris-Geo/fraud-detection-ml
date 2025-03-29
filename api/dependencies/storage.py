from minio import Minio
from minio.error import S3Error
import io
import json
from datetime import datetime
from api.core.config import settings

class MinioClient:
    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_ENDPOINT.startswith("https")
        )
        
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
        except S3Error as e:
            print(f"Error creating bucket: {e}")
    
    def store_transaction(self, transaction_data):
        transaction_id = transaction_data.get("transaction_id")
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        key = f"raw/transactions/date={timestamp}/{transaction_id}.json"
        
        data_bytes = json.dumps(transaction_data).encode('utf-8')
        data_stream = io.BytesIO(data_bytes)
        data_size = len(data_bytes)
        
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=key,
            data=data_stream,
            length=data_size,
            content_type="application/json"
        )
        
        return key
    
    def get_transaction(self, key):
        try:
            response = self.client.get_object(settings.MINIO_BUCKET, key)
            data = json.loads(response.read().decode('utf-8'))
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"Error retrieving object: {e}")
            return None

minio_client = MinioClient()