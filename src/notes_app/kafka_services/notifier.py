from notes_app.database.models import NoteAdded
from notes_app.kafka_services.config import TOPIC_NAMES


class Notifier:
    def __init__(self, producer):
        self.producer = producer

    def publish(self, event: NoteAdded) -> None:
        msg = event.message
        self.producer.send(topic=TOPIC_NAMES["notes_events"], value=msg.encode("utf-8"))
