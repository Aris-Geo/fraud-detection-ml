import pika
import json
from api.core.config import settings

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.connect()
    
    def connect(self):
        try:
            credentials = pika.PlainCredentials(
                settings.RABBITMQ_USER, 
                settings.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=int(settings.RABBITMQ_PORT),
                credentials=credentials,
                heartbeat=30,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_TRANSACTIONS)
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_PROCESSED)
            
            print("Connected to RabbitMQ")
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
    
    def publish_transaction(self, transaction_data):
        try:
            if self.connection is None or self.connection.is_closed:
                self.connect()
                
            if self.connection is None or self.channel is None:
                print("RabbitMQ connection unavailable, skipping message publish")
                return False
            
            self.channel.basic_publish(
                exchange='',
                routing_key=settings.RABBITMQ_QUEUE_TRANSACTIONS,
                body=json.dumps(transaction_data),
                properties=pika.BasicProperties(
                    delivery_mode=2, 
                )
            )
            return True
        except Exception as e:
            print(f"Error publishing to RabbitMQ: {e}")
            try:
                if self.connection and self.connection.is_open:
                    self.connection.close()
            except:
                pass
            self.connection = None
            self.channel = None
            return False
    
    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

rabbitmq_client = RabbitMQClient()