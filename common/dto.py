from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, condecimal


class EventStatus(str, Enum):
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


class Event(BaseModel):
    id: str
    coefficient: condecimal(decimal_places=2, gt=Decimal(0)) | None
    deadline: datetime | None
    status: EventStatus | None


class Bet(BaseModel):
    id: str
    amount: condecimal(decimal_places=2, gt=Decimal(0))
    status: EventStatus | None

    class Config:
        orm_mode = True
