Fraud Detection System
A comprehensive financial transaction fraud detection system with real-time prediction capabilities.
Features

Real-time fraud detection using Random Forest
REST API for transaction processing
Data storage in PostgreSQL and MinIO (S3-compatible)
Message queueing with RabbitMQ
Containerized environment with Docker

System Architecture
CopyFastAPI (API) → RabbitMQ (Queue) → Consumer (Worker)
    ↓                                    ↓
PostgreSQL ↔ MinIO (S3) ↔ ML Model (Prediction)
(Database)
Setup Instructions
Prerequisites

Docker and Docker Compose
Python 3.8+
PostgreSQL client (optional)

Getting Started

Clone the repository:
git clone https://github.com/yourusername/fraud-detection-system.git
cd fraud-detection-system

Install requirements:
pip install -r requirements.txt

Create a .env file:
Copy# API Configuration
API_KEY=your_secret_api_key_here
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=frauddetection
POSTGRES_USER=frauduser
POSTGRES_PASSWORD=fraudpass

# MinIO Configuration
MINIO_ENDPOINT=http://localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=adminpass
MINIO_BUCKET=fraud-detection-data

# RabbitMQ Configuration
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_QUEUE_TRANSACTIONS=transactions
RABBITMQ_QUEUE_PROCESSED=processed_transactions

Start the infrastructure:
docker-compose up -d

Initialize the database:
python helpers/init_database.sql

Download and load the dataset:
python helpers/download_dataset.py
python helpers/load_data_to_db.py

Train the fraud detection model:
python machine_learning/train_forest.py

Upload the model to MinIO:
python scripts/upload_model_to_s3.py

Start the API:
uvicorn api.main:app --reload

Access the API documentation at http://localhost:8000/docs

ML Model
The system uses a Random Forest classifier to detect fraudulent transactions:

Trains on 300,000+ transactions with PCA-transformed features (V1-V28)
Uses SMOTE to address class imbalance (fraud transactions are only 0.2%)
Achieves 99.95% accuracy with 83.7% precision and 91.1% recall
Key predictive features: V14, V10, V12, and V4

Making API Requests
To submit a transaction for fraud analysis:
curl -X 'POST' \
  'http://localhost:8000/transactions/' \
  -H 'accept: application/json' \
  -H 'X-API-Key: your_secret_api_key_here' \
  -H 'Content-Type: application/json' \
  -d '{
  "time": 86400,
  "v1": 1.783274,
  "v2": 0.863097,
  "v3": -0.010309,
  "v4": 2.231846,
  "v5": 0.533413,
  "v6": 0.767435,
  "v7": 0.434702,
  "v8": -0.098624,
  "v9": -0.269286,
  "v10": 0.817739,
  "v11": 0.753074,
  "v12": 0.822584,
  "v13": 0.178641,
  "v14": 0.367064,
  "v15": -0.418095,
  "v16": -0.049233,
  "v17": 0.413900,
  "v18": 0.236880,
  "v19": 0.163080,
  "v20": -0.072330,
  "v21": -0.194904,
  "v22": 0.073110,
  "v23": -0.104432,
  "v24": -0.217919,
  "v25": 0.393598,
  "v26": 0.079447,
  "v27": 0.129954,
  "v28": -0.053208,
  "amount": 149.62
}'
Tech Stack

Python: Core programming language
FastAPI: API framework
Docker: Containerization
PostgreSQL: Transaction database
MinIO: S3-compatible storage
RabbitMQ: Message queue
RandomForest: ML algorithm
Scikit-learn: ML library
