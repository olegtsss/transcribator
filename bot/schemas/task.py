from pydantic import BaseModel


class LoadData(BaseModel):
    telegram_id: int
    audio_path: str
    translate: bool
