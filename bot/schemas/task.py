from typing import Optional

from config import settings
from pydantic import BaseModel


class LoadData(BaseModel):
    telegram_id: int
    audio_path: str
    translate: Optional[bool] = settings.need_translate
