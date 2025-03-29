-- init_database.sql - Initialize Fraud Detection Database

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS fraud_predictions;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS ml_models;

-- Create transactions table
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    time FLOAT,          -- Original time from dataset
    v1 FLOAT, v2 FLOAT, v3 FLOAT, v4 FLOAT, v5 FLOAT,
    v6 FLOAT, v7 FLOAT, v8 FLOAT, v9 FLOAT, v10 FLOAT,
    v11 FLOAT, v12 FLOAT, v13 FLOAT, v14 FLOAT, v15 FLOAT,
    v16 FLOAT, v17 FLOAT, v18 FLOAT, v19 FLOAT, v20 FLOAT,
    v21 FLOAT, v22 FLOAT, v23 FLOAT, v24 FLOAT, v25 FLOAT,
    v26 FLOAT, v27 FLOAT, v28 FLOAT,
    amount FLOAT,
    is_fraud BOOLEAN,    -- Original class label
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source VARCHAR(50) DEFAULT 'dataset'
);

-- Create index on commonly queried fields
CREATE INDEX idx_transactions_fraud ON transactions(is_fraud);
CREATE INDEX idx_transactions_time ON transactions(time);
CREATE INDEX idx_transactions_amount ON transactions(amount);

-- Create table for ML models
CREATE TABLE ml_models (
    model_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    performance_metrics JSONB,
    active BOOLEAN DEFAULT FALSE
);

-- Create table for predictions
CREATE TABLE fraud_predictions (
    prediction_id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(transaction_id),
    model_id INTEGER REFERENCES ml_models(model_id),
    fraud_probability FLOAT NOT NULL,
    prediction_threshold FLOAT NOT NULL,
    predicted_class BOOLEAN NOT NULL,
    prediction_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    features_used JSONB,
    explanation JSONB
);

-- Create index on foreign keys
CREATE INDEX idx_predictions_transaction ON fraud_predictions(transaction_id);
CREATE INDEX idx_predictions_model ON fraud_predictions(model_id);

-- Create view for fraud detection performance
CREATE OR REPLACE VIEW fraud_detection_performance AS
SELECT 
    m.model_id,
    m.model_name,
    COUNT(p.prediction_id) AS total_predictions,
    SUM(CASE WHEN p.predicted_class = t.is_fraud THEN 1 ELSE 0 END) AS correct_predictions,
    SUM(CASE WHEN p.predicted_class = TRUE AND t.is_fraud = TRUE THEN 1 ELSE 0 END) AS true_positives,
    SUM(CASE WHEN p.predicted_class = FALSE AND t.is_fraud = FALSE THEN 1 ELSE 0 END) AS true_negatives,
    SUM(CASE WHEN p.predicted_class = TRUE AND t.is_fraud = FALSE THEN 1 ELSE 0 END) AS false_positives,
    SUM(CASE WHEN p.predicted_class = FALSE AND t.is_fraud = TRUE THEN 1 ELSE 0 END) AS false_negatives
FROM 
    fraud_predictions p
JOIN 
    transactions t ON p.transaction_id = t.transaction_id
JOIN 
    ml_models m ON p.model_id = m.model_id
GROUP BY 
    m.model_id, m.model_name;

-- Create function to insert a new transaction
CREATE OR REPLACE FUNCTION insert_transaction(
    p_time FLOAT,
    p_v1 FLOAT, p_v2 FLOAT, p_v3 FLOAT, p_v4 FLOAT, p_v5 FLOAT,
    p_v6 FLOAT, p_v7 FLOAT, p_v8 FLOAT, p_v9 FLOAT, p_v10 FLOAT,
    p_v11 FLOAT, p_v12 FLOAT, p_v13 FLOAT, p_v14 FLOAT, p_v15 FLOAT,
    p_v16 FLOAT, p_v17 FLOAT, p_v18 FLOAT, p_v19 FLOAT, p_v20 FLOAT,
    p_v21 FLOAT, p_v22 FLOAT, p_v23 FLOAT, p_v24 FLOAT, p_v25 FLOAT,
    p_v26 FLOAT, p_v27 FLOAT, p_v28 FLOAT,
    p_amount FLOAT,
    p_is_fraud BOOLEAN,
    p_source VARCHAR DEFAULT 'api'
) RETURNS INTEGER AS $$
DECLARE
    v_transaction_id INTEGER;
BEGIN
    INSERT INTO transactions (
        time, 
        v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
        v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
        v21, v22, v23, v24, v25, v26, v27, v28,
        amount, is_fraud, source
    ) VALUES (
        p_time,
        p_v1, p_v2, p_v3, p_v4, p_v5, p_v6, p_v7, p_v8, p_v9, p_v10,
        p_v11, p_v12, p_v13, p_v14, p_v15, p_v16, p_v17, p_v18, p_v19, p_v20,
        p_v21, p_v22, p_v23, p_v24, p_v25, p_v26, p_v27, p_v28,
        p_amount, p_is_fraud, p_source
    ) RETURNING transaction_id INTO v_transaction_id;
    
    RETURN v_transaction_id;
END;
$$ LANGUAGE plpgsql;

-- Add comments to tables
COMMENT ON TABLE transactions IS 'Stores all transactions for fraud detection';
COMMENT ON TABLE ml_models IS 'Metadata about ML models used for fraud detection';
COMMENT ON TABLE fraud_predictions IS 'Predictions made by ML models on transactions';
COMMENT ON VIEW fraud_detection_performance IS 'Performance metrics for fraud detection models';

-- Complete setup message
DO $$
BEGIN
    RAISE NOTICE 'Fraud detection database schema initialized successfully';
END $$;