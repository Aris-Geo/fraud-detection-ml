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
                credentials=credentials
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_TRANSACTIONS)
            self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE_PROCESSED)
            
            print("Connected to RabbitMQ")
        except Exception as e:
            print(f"Error connecting to RabbitMQ: {e}")
    
    def publish_transaction(self, transaction_data):
        if self.connection is None or self.connection.is_closed:
            self.connect()
        
        self.channel.basic_publish(
            exchange='',
            routing_key=settings.RABBITMQ_QUEUE_TRANSACTIONS,
            body=json.dumps(transaction_data),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
    
    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()

rabbitmq_client = RabbitMQClient()