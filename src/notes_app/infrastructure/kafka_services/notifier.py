import logging
from aiokafka import AIOKafkaProducer
from notes_app.api.models.user_schema import UserCreatedEvent
from notes_app.api.models.note_schema import NoteAddedEvent
from notes_app.infrastructure.config import config


logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def publish(self, event: UserCreatedEvent | NoteAddedEvent):
        try:
            topic_name: str
            if isinstance(event, UserCreatedEvent):
                topic_name = config.KAFKA_TOPIC_NAMES["users_events"]
            elif isinstance(event, NoteAddedEvent):
                topic_name = config.KAFKA_TOPIC_NAMES["notes_events"]
            msg = event.message
            await self.producer.send_and_wait(
                topic=topic_name,
                value=msg.encode("utf-8"),
            )
        except Exception as e:
            logger.error(f"Kafka producer error: {e}")
