from aiokafka import AIOKafkaProducer
from fastapi import HTTPException, status
from notes_app.api.models.note_schema import NoteAdded
from notes_app.infrastructure.kafka_services.config import TOPIC_NAMES


class Notifier:
    def __init__(self, producer: AIOKafkaProducer):
        self.producer = producer

    async def publish(self, event: NoteAdded):
        try:
            msg = event.message
            await self.producer.send_and_wait(
                topic=TOPIC_NAMES["notes_events"], value=msg.encode("utf-8")
            )
        except Exception as e:
            print(f"Kafka publish error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Message not delivered",
            )
