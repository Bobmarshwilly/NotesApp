from aiokafka import AIOKafkaProducer
from dotenv import load_dotenv


load_dotenv()


from notes_app.infrastructure.config import config  # noqa: E402


class KafkaProducer:
    _instance = None

    def __init__(self):
        self.producer = AIOKafkaProducer(**config.KAFKA_PRODUCER_CONFIG)

    async def start(self):
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
