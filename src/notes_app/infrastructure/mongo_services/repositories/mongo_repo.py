from typing import Optional, List
from beanie import PydanticObjectId
from notes_app.infrastructure.mongo_services.models.note_model import NoteMongo
from notes_app.infrastructure.database.models.note_table import Note


class MongoNoteRepo:
    async def create_note(
        self, note_data: Note, parent_id: Optional[PydanticObjectId] = None
    ) -> NoteMongo:
        note = NoteMongo(
            note_id=note_data.id,
            content=note_data.content,
            owner_id=note_data.owner_id,
            parent_id=parent_id,
        )
        await note.insert()
        return note

    async def get_note_by_id(self, note_id: int) -> Optional[NoteMongo]:
        return await NoteMongo.find_one(NoteMongo.note_id == note_id)

    async def update_note(
        self, current_note_data: dict, new_note_data: Note
    ) -> NoteMongo:
        current_note = await NoteMongo.find_one(
            NoteMongo.note_id == current_note_data["id"],
            NoteMongo.content == current_note_data["content"],
        )

        if not current_note:
            return await self.create_note(new_note_data)

        # Создаем новую версию с parent_id, ссылающимся на текущую
        return await self.create_note(new_note_data, parent_id=current_note.id)

    async def get_history_of_update(self, note_data: Note) -> Optional[List[NoteMongo]]:
        current_note = await NoteMongo.find_one(
            NoteMongo.note_id == note_data.id, NoteMongo.content == note_data.content
        )
        if not current_note:
            return None
        print(f"current_note={current_note}")

        history = []
        while current_note:
            history.append(current_note)
            if current_note.parent_id is None:
                break
            current_note = await NoteMongo.find_one(
                NoteMongo.id == current_note.parent_id
            )

        # Вернем историю от первой к последней версии
        return list(reversed(history))

    async def delete_history_of_update(self, note_data: Note) -> bool:
        current_note = await self.get_note_by_id(note_data.id)
        if not current_note:
            return False
        await NoteMongo.find(NoteMongo.note_id == current_note.note_id).delete()
        return True
