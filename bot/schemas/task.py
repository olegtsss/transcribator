from pydantic import BaseModel
from typing import Optional


class LoadData(BaseModel):
    telegram_id: int
    audio_path: str
    translate: Optional[bool] = True
