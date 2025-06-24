import logging
import asyncio
from aiokafka import AIOKafkaConsumer
from notes_app.infrastructure.config import config


logger = logging.getLogger(__name__)


async def notes_consume():
    consumer = AIOKafkaConsumer(
        config.KAFKA_TOPIC_NAMES["notes_events"], **config.KAFKA_CONSUMER_CONFIG
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(message.value.decode())
    except Exception as e:
        logger.error(f"Notes consumer error: {e}")
        raise Exception
    finally:
        await consumer.stop()


async def users_consume():
    consumer = AIOKafkaConsumer(
        config.KAFKA_TOPIC_NAMES["users_events"], **config.KAFKA_CONSUMER_CONFIG
    )
    await consumer.start()
    try:
        async for message in consumer:
            print(message.value.decode())
    except Exception as e:
        logger.error(f"User consumer error: {e}")
        raise Exception
    finally:
        await consumer.stop()


async def main():
    try:
        await asyncio.gather(notes_consume(), users_consume())
    except asyncio.CancelledError:
        logger.info("Приложение остановлено по запросу")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
    finally:
        logger.info("Завершение работы")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Принудительное завершение работы")
