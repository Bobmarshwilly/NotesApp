from kafka import KafkaProducer
from notes_app.kafka_services.config import PRODUCER_CONFIG
import json


producer = KafkaProducer(**PRODUCER_CONFIG)