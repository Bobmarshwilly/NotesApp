from kafka import KafkaProducer
from notes_app.kafka_services.config import PRODUCER_CONFIG


kafka_producer = KafkaProducer(**PRODUCER_CONFIG)
