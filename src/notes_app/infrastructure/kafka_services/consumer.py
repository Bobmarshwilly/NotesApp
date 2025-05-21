import asyncio
from aiokafka import AIOKafkaConsumer
from notes_app.infrastructure.kafka_services.config import CONSUMER_CONFIG, TOPIC_NAMES


async def consume():
    consumer = AIOKafkaConsumer(TOPIC_NAMES["notes_events"], **CONSUMER_CONFIG)
    await consumer.start()
    try:
        async for message in consumer:
            print(message.value.decode())
    except Exception as e:
        print(f"Consumer error: {e}")
        raise Exception
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume())
