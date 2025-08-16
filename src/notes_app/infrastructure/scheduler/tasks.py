from celery.utils.log import get_task_logger
from notes_app.infrastructure.scheduler.celery_app import celery_app
from notes_app.infrastructure.database.main import sync_session
from notes_app.infrastructure.database.repositories.celery_repo import CeleryRepo
from notes_app.infrastructure.redis_services.cache_manager import CacheManager
from notes_app.infrastructure.redis_services.redis_client import sync_redis_client

logger = get_task_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def delete_old_notes_task(self):
    logger.info("Start daily clean up task")
    with sync_session() as session:
        try:
            celery_repo = CeleryRepo(session=session)
            celery_repo.delete_all_notes()
            session.commit()
            logger.info("All notes deleted")

            cache_manager = CacheManager(redis_client=sync_redis_client)
            cache_manager.sync_delete_pattern(pattern="notes:*")
        except Exception as e:
            logger.error(f"Task error: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()
