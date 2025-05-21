BOOTSTRAP_SERVERS = ["localhost:9092"]

TOPIC_NAMES = {
    "notes_events": "notes_events_topic",
}

PRODUCER_CONFIG = {
    "bootstrap_servers": BOOTSTRAP_SERVERS,
    "client_id": "notes-app-producer",
    "acks": "all",
    "request_timeout_ms": 5000,
}

CONSUMER_CONFIG = {
    "bootstrap_servers": BOOTSTRAP_SERVERS,
    "group_id": "my_consumer_group",
    "auto_offset_reset": "earliest",
}
