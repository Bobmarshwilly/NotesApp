from aiokafka import AIOKafkaProducer
from notes_app.infrastructure.kafka_services.config import PRODUCER_CONFIG


class KafkaProducer:
    _instance = None

    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(**PRODUCER_CONFIG)
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    @classmethod
    async def get_producer(cls) -> AIOKafkaProducer:
        if cls._instance is None:
            cls._instance = KafkaProducer()
            await cls._instance.start()
        return cls._instance.producer
