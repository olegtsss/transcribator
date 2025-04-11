import uuid
from datetime import datetime

from core.constants import Descriptions
from pydantic import BaseModel, Field


class LoadData(BaseModel):
    entity_id: uuid.UUID = uuid.uuid4()
    created_at: datetime = datetime.now()
    telegram_id: int = Field(title=Descriptions.TELEGRAM_ID.value)
    audio_path: str = Field(title=Descriptions.PATH.value)
