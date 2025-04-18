import uuid
from datetime import datetime

from pydantic import BaseModel


class LoadData(BaseModel):
    entity_id: uuid.UUID
    created_at: datetime
    telegram_id: int
    audio_path: str
    translate: bool
