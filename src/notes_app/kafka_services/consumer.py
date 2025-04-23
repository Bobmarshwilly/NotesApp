from kafka import KafkaConsumer
from notes_app.kafka_services.config import CONSUMER_CONFIG, TOPIC_NAMES


consumer = KafkaConsumer(TOPIC_NAMES["notes_events"], **CONSUMER_CONFIG)

for message in consumer:
    print(message.value.decode())