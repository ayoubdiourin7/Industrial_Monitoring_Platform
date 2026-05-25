from datetime import datetime

from pydantic import BaseModel


class ReadingOut(BaseModel):
    id: int
    machine_id: str
    vibration: float
    acoustic: float
    power_draw: float
    is_anomaly: bool
    timestamp: datetime

    model_config = {"from_attributes": True}
