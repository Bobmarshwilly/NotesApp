from notes_app.api.providers import get_note_repo, get_tx_manager
from notes_app.infrastructure.database.main import async_session


async def delete_old_notes_task():
    async with async_session() as session:
        tx_manager = get_tx_manager(session=session)
        try:
            note_repo = get_note_repo(session=session)
            await note_repo.delete_all_notes()
            await tx_manager.commit()
        except Exception as e:
            print(f"Scheduler error: {e}")
            await tx_manager.rollback()
            raise
