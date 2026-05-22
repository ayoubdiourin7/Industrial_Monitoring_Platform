from datetime import datetime

from pydantic import BaseModel


class ReadingOut(BaseModel):
    id: int
    machine_id: str
    temperature: float
    vibration: float
    pressure: float
    is_anomaly: bool
    timestamp: datetime

    model_config = {"from_attributes": True}
