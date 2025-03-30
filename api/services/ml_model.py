# app/services/ml_model.py
import io
import pickle
import os
from minio import Minio
from api.core.config import settings
import logging

logger = logging.getLogger(__name__)

class ModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.minio_client = None
        self._initialize_minio()
        self.load_model()
    
    def _initialize_minio(self):
        try:
            self.minio_client = Minio(
                endpoint=settings.MINIO_ENDPOINT.replace("http://", "").replace("https://", ""),
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_ENDPOINT.startswith("https")
            )
            logger.info("MinIO client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing MinIO client: {e}")
            self.minio_client = None
    
    def load_model(self):
        if self.minio_client:
            try:
                logger.info("Attempting to load model from MinIO")
                model_obj = self.minio_client.get_object(
                    settings.MINIO_BUCKET, 
                    "models/fraud_model.pkl"
                )
                model_data = model_obj.read()
                self.model = pickle.loads(model_data)
                model_obj.close()
                
                # Load scaler from MinIO
                scaler_obj = self.minio_client.get_object(
                    settings.MINIO_BUCKET, 
                    "models/scaler.pkl"
                )
                scaler_data = scaler_obj.read()
                self.scaler = pickle.loads(scaler_data)
                scaler_obj.close()
                
                logger.info("Model and scaler loaded successfully from MinIO")
                return
            except Exception as e:
                logger.error(f"Error loading model from MinIO: {e}")
        
        try:
            logger.info("Attempting to load model from local storage")
            model_path = os.path.join("app", "ml_models", "fraud_model.pkl")
            scaler_path = os.path.join("app", "ml_models", "scaler.pkl")
            
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
                logger.info("Model and scaler loaded successfully from local storage")
            else:
                logger.error("Model or scaler file not found in local storage")
        except Exception as e:
            logger.error(f"Error loading model from local storage: {e}")
    
    def predict(self, features):
        """
        Make a fraud prediction on the provided features.
        
        Args:
            features: Dictionary containing transaction features
            
        Returns:
            Dictionary with prediction results
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model or scaler not loaded")
        
        feature_array = []
        for col in ["time", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10",
                   "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20",
                   "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "amount"]:
            feature_array.append(features.get(col, 0.0))
        
        scaled_features = self.scaler.transform([feature_array])
        
        fraud_prob = self.model.predict_proba(scaled_features)[0, 1]
        is_fraud = fraud_prob > 0.5
        
        confidence = 2 * abs(fraud_prob - 0.5)
        
        return {
            "fraud_probability": float(fraud_prob),
            "is_fraud": bool(is_fraud),
            "confidence": float(confidence)
        }

model_service = ModelService()