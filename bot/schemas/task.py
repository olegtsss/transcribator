from pydantic import BaseModel
from typing import Optional
from core.config import settings


class LoadData(BaseModel):
    telegram_id: int
    audio_path: str
    translate: Optional[bool] = settings.need_translate
