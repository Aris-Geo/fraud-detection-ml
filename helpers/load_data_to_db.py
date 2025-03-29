import asyncio
import asyncpg
import pandas as pd
import os
from pathlib import Path
import time
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('data_loader')

async def load_data_to_postgres():
    load_dotenv()
    data_file = Path("data/creditcard.csv")
    
    if not data_file.exists():
        logger.error(f"Error: Dataset file not found at {data_file}")
        return
    
    file_size_mb = data_file.stat().st_size / (1024 * 1024)
    logger.info(f"Loading data from {data_file}...")
    logger.info(f"File size: {file_size_mb:.2f} MB")
    
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD')
    }
    
    logger.info("Creating database connection pool")
    
    batch_size = 5000
    
    start_time = time.time()
    total_rows = 0
    
    pool = await asyncpg.create_pool(**db_config, min_size=3, max_size=10)
    
    try:
        reader = pd.read_csv(data_file, batch_size=batch_size)
        
        for chunk_num, chunk in enumerate(reader):
            logger.info(f"Processing chunk {chunk_num+1} with {len(chunk)} rows")
            
            if 'Class' in chunk.columns:
                chunk = chunk.rename(columns={'Class': 'is_fraud'})
            
            batch_data = []
            for _, row in chunk.iterrows():
                batch_data.append((
                    float(row['Time']),
                    float(row['V1']), float(row['V2']), float(row['V3']), 
                    float(row['V4']), float(row['V5']), float(row['V6']), 
                    float(row['V7']), float(row['V8']), float(row['V9']), 
                    float(row['V10']), float(row['V11']), float(row['V12']), 
                    float(row['V13']), float(row['V14']), float(row['V15']), 
                    float(row['V16']), float(row['V17']), float(row['V18']), 
                    float(row['V19']), float(row['V20']), float(row['V21']), 
                    float(row['V22']), float(row['V23']), float(row['V24']), 
                    float(row['V25']), float(row['V26']), float(row['V27']), 
                    float(row['V28']), float(row['Amount']), 
                    bool(row['is_fraud']), 'dataset'
                ))
            
            async with pool.acquire() as conn:
                async with conn.transaction():
                    await conn.executemany('''
                        INSERT INTO transactions (
                            time, 
                            v1, v2, v3, v4, v5, v6, v7, v8, v9, v10,
                            v11, v12, v13, v14, v15, v16, v17, v18, v19, v20,
                            v21, v22, v23, v24, v25, v26, v27, v28,
                            amount, is_fraud, source
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, 
                                $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, 
                                $23, $24, $25, $26, $27, $28, $29, $30, $31, $32)
                    ''', batch_data)
            
            total_rows += len(chunk)
            logger.info(f"Inserted {total_rows} rows so far")
            
        elapsed_time = time.time() - start_time
        logger.info(f"Data loading completed in {elapsed_time:.2f} seconds")
        logger.info(f"Total rows inserted: {total_rows}")
        
    except Exception as e:
        logger.error(f"Error loading data: {e}")
    finally:
        await pool.close()
        logger.info("Database connection pool closed")

if __name__ == "__main__":
    asyncio.run(load_data_to_postgres())