from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, condecimal


class EventStatus(str, Enum):
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


class Event(BaseModel):
    id: int
    coefficient: condecimal(decimal_places=2, gt=Decimal(0)) | None
    deadline: datetime | None
    status: EventStatus | None

    class Config:
        orm_mode = True


class Bet(BaseModel):
    id: int
    amount: Decimal
    status: EventStatus

    class Config:
        orm_mode = True


class BetCreate(BaseModel):
    event_id: int
    amount: condecimal(decimal_places=2, gt=Decimal(0))
