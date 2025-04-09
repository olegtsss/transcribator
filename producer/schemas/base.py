from pydantic import BaseModel, Field

from core.constants import Descriptions


class LoadData(BaseModel):
    telegram_id: int = Field(title=Descriptions.TELEGRAM_ID.value)
    audio_path: str = Field(title=Descriptions.PATH.value)
