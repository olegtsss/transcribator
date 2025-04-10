from pydantic import BaseModel, Field
from uuid import UUID
from core.constants import Descriptions
from datetime import datetime


class LoadData(BaseModel):
    # entity_id: UUID
    created_at: datetime = datetime.now()
    telegram_id: int = Field(title=Descriptions.TELEGRAM_ID.value)
    audio_path: str = Field(title=Descriptions.PATH.value)
