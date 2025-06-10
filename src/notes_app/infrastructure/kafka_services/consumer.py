import asyncio
from aiokafka import AIOKafkaConsumer
from dotenv import load_dotenv


load_dotenv()


from notes_app.infrastructure.config import config  # noqa: E402


async def consume():
    consumer = AIOKafkaConsumer(
        config.KAFKA_TOPIC_NAMES["notes_events"], **config.KAFKA_CONSUMER_CONFIG
    )
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
