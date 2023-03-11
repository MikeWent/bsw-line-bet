from datetime import datetime
from decimal import Decimal

from enum import Enum

from pydantic import BaseModel, validator


class EventStatus(str, Enum):
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


class Event(BaseModel):
    id: int
    coefficient: Decimal | None
    deadline: datetime | None
    status: EventStatus | None

    @validator("coefficient")
    def positive(cls, v: Decimal):
        if not v > 0:
            raise ValueError("must be positive")
        return v

    @validator("coefficient")
    def two_digit_precise(cls, v: Decimal):
        if v.as_tuple().exponent < -2:
            raise ValueError("must be at most 2 decimal points precise")
        return v
