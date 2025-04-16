import uuid
from datetime import datetime
from typing import Optional
from core.constants import Descriptions
from pydantic import BaseModel, Field


class LoadData(BaseModel):
    entity_id: uuid.UUID = Field(default_factory=uuid.uuid4, title=Descriptions.UUID.value)
    created_at: datetime = Field(default_factory=datetime.now, title=Descriptions.CREATED.value)
    telegram_id: int = Field(title=Descriptions.TELEGRAM_ID.value)
    audio_path: str = Field(title=Descriptions.PATH.value)
    translate: Optional[bool] = Field(
        default_factory=lambda: True, title=Descriptions.TRANSLATE.value
    )
