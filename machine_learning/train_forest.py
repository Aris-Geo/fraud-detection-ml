import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from dotenv import load_dotenv
import pickle
import time
from datetime import datetime
import json

# ML imports
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, 
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, average_precision_score, roc_curve
)
from imblearn.over_sampling import SMOTE

load_dotenv()

db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(db_url)

os.makedirs("models", exist_ok=True)
os.makedirs("machine_learning/evaluation", exist_ok=True)

print("Loading data from PostgreSQL...")
query = "SELECT * FROM transactions"
df = pd.read_sql(query, engine)
print(f"Loaded {len(df)} transactions")

fraud_count = df['is_fraud'].sum()
print(f"Number of fraudulent transactions: {fraud_count} ({fraud_count/len(df)*100:.3f}%)")
print(f"Number of legitimate transactions: {len(df)-fraud_count}")

X = df.drop(['transaction_id', 'is_fraud', 'processed_at', 'source'], axis=1)
y = df['is_fraud']

feature_cols = X.columns.tolist()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Training set: {X_train.shape[0]} samples ({y_train.sum()} frauds)")
print(f"Test set: {X_test.shape[0]} samples ({y_test.sum()} frauds)")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Save the scaler for future use
with open("models/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print("Feature scaler saved to models/scaler.pkl")

print("Applying SMOTE to handle class imbalance.")
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train_scaled, y_train)

print(f"Original training set shape: {np.bincount(y_train.astype(int))}")
print(f"Resampled training set shape: {np.bincount(y_train_resampled.astype(int))}")

# Train Random Forest model
print("\nTraining Random Forest model")
start_time = time.time()

rf_model = RandomForestClassifier(
    n_estimators=100,        # Number of trees
    max_depth=15,            # Maximum depth of trees
    min_samples_split=10,    # Minimum samples required to split node
    min_samples_leaf=4,      # Minimum samples required at leaf node
    max_features='sqrt',     # Number of features to consider for best split
    bootstrap=True,          # Use bootstrap samples
    class_weight='balanced', # Handle class imbalance
    random_state=42          # For reproducibility
)

rf_model.fit(X_train_resampled, y_train_resampled)

training_time = time.time() - start_time
print(f"Model trained in {training_time:.2f} seconds")

y_pred = rf_model.predict(X_test_scaled)
y_prob = rf_model.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
auc = roc_auc_score(y_test, y_prob)
avg_precision = average_precision_score(y_test, y_prob)

print("\n=== Model Performance ===")
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
print(f"ROC AUC: {auc:.4f}")
print(f"Average Precision: {avg_precision:.4f}")

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix - Random Forest')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.savefig("machine_learning/evaluation/rf_confusion_matrix.png")
print("Confusion matrix saved to machine_learning/evaluation/rf_confusion_matrix.png")

plt.figure(figsize=(10, 8))
fpr, tpr, _ = roc_curve(y_test, y_prob)
plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc:.4f})')
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve - Random Forest')
plt.legend()
plt.savefig("machine_learning/evaluation/rf_roc_curve.png")
print("ROC curve saved to machine_learning/evaluation/rf_roc_curve.png")

plt.figure(figsize=(10, 8))
precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_prob)
plt.plot(recall_curve, precision_curve, label=f'PR Curve (AP = {avg_precision:.4f})')
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.title('Precision-Recall Curve - Random Forest')
plt.legend()
plt.savefig("machine_learning/evaluation/rf_pr_curve.png")
print("Precision-Recall curve saved to machine_learning/evaluation/rf_pr_curve.png")

feature_importance = pd.DataFrame({
    'feature': feature_cols,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n=== Top 10 Most Important Features ===")
print(feature_importance.head(10))

plt.figure(figsize=(12, 10))
sns.barplot(x='importance', y='feature', data=feature_importance.head(15))
plt.title('Feature Importance - Random Forest')
plt.tight_layout()
plt.savefig("machine_learning/evaluation/rf_feature_importance.png")
print("Feature importance plot saved to machine_learning/evaluation/rf_feature_importance.png")

print("\n=== Classification Report ===")
print(classification_report(y_test, y_pred))

results = {
    "model_type": "Random Forest",
    "training_time": training_time,
    "performance_metrics": {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "avg_precision": float(avg_precision)
    },
    "confusion_matrix": cm.tolist(),
    "feature_importance": {
        feature: float(importance) 
        for feature, importance in zip(feature_cols, rf_model.feature_importances_)
    },
    "model_parameters": rf_model.get_params()
}

with open("machine_learning/evaluation/rf_model_results.json", "w") as f:
    json.dump(results, f, indent=4)

with open("models/random_forest_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)
print("Model saved to models/random_forest_model.pkl")

app_model_dir = "machine_learning/ml_models"
os.makedirs(app_model_dir, exist_ok=True)
with open(f"{app_model_dir}/fraud_model.pkl", "wb") as f:
    pickle.dump(rf_model, f)
print(f"Model saved to {app_model_dir}/fraud_model.pkl for API use")

model_metadata = {
    "model_name": "Random Forest",
    "description": f"Fraud detection Random Forest model trained on {len(X_train)} samples with SMOTE resampling",
    "performance_metrics": {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "avg_precision": float(avg_precision)
    }
}

with engine.connect() as conn:
    from sqlalchemy import text
    
    conn.execute(text("UPDATE ml_models SET active = FALSE"))
    
    insert_query = text("""
    INSERT INTO ml_models (model_name, description, performance_metrics, active)
    VALUES (:model_name, :description, :metrics, TRUE)
    """)
    
    conn.execute(insert_query, {
        "model_name": model_metadata["model_name"],
        "description": model_metadata["description"],
        "metrics": json.dumps(model_metadata["performance_metrics"])
    })
    
    conn.commit()
print("Model metadata saved to database")

def test_prediction(transaction_data):

    sample = pd.DataFrame([transaction_data])
    
    sample_scaled = scaler.transform(sample)
    
    prob = rf_model.predict_proba(sample_scaled)[0, 1]
    prediction = prob > 0.5
    
    return {
        "fraud_probability": float(prob),
        "is_fraud": bool(prediction),
        "confidence": float(2 * abs(prob - 0.5))
    }

legitimate_sample = X[y == 0].iloc[0].to_dict()
print("\n=== Sample Prediction (Legitimate Transaction) ===")
print(test_prediction(legitimate_sample))

if len(X[y == 1]) > 0:
    fraud_sample = X[y == 1].iloc[0].to_dict()
    print("\n=== Sample Prediction (Fraudulent Transaction) ===")
    print(test_prediction(fraud_sample))

print("\nRandom Forest model training and evaluation complete!")