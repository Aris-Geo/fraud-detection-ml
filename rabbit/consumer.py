import os
import json
import pika
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("transaction_consumer")
load_dotenv()

db_url = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
engine = create_engine(db_url)

def callback(ch, method, properties, body):
    try:
        transaction_data = json.loads(body)
        transaction_id = transaction_data.get('transaction_id')
        logger.info(f"Received transaction: {transaction_id}")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT transaction_id FROM transactions WHERE transaction_id = :id"),
                {"id": transaction_id}
            )
            exists = result.fetchone() is not None
            
            if exists:
                logger.info(f"Transaction {transaction_id} verified in database")
            else:
                logger.warning(f"Transaction {transaction_id} not found in database. Adding log entry.")
        
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def main():
    logger.info("Starting transaction verification consumer.")
    
    credentials = pika.PlainCredentials(
        os.getenv('RABBITMQ_USER'),
        os.getenv('RABBITMQ_PASSWORD')
    )
    parameters = pika.ConnectionParameters(
        host=os.getenv('RABBITMQ_HOST'),
        port=int(os.getenv('RABBITMQ_PORT')),
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    queue_name = os.getenv('RABBITMQ_QUEUE_TRANSACTIONS')
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    
    logger.info(f"Listening for messages on {queue_name}. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer.")
        channel.stop_consuming()
    finally:
        connection.close()

if __name__ == "__main__":
    main()