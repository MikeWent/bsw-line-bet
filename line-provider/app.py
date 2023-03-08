from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class EventStatus(Enum):
    NEW = 1
    FINISHED_WIN = 2
    FINISHED_LOSE = 3


class Event(BaseModel):
    id: str
    coefficient: Decimal | None
    deadline: datetime | None
    status: EventStatus | None


events: dict[str, Event] = {
    "1": Event(
        id="1",
        coefficient=1.2,
        deadline=datetime.now() + timedelta(minutes=1),
        status=EventStatus.NEW,
    ),
    "2": Event(
        id="2",
        coefficient=1.15,
        deadline=datetime.now() + timedelta(seconds=30),
        status=EventStatus.NEW,
    ),
    "3": Event(
        id="3",
        coefficient=1.67,
        deadline=datetime.now() + timedelta(seconds=10),
        status=EventStatus.NEW,
    ),
}


@app.get("/events")
async def get_events() -> List[Event]:
    return [e for e in events.values() if datetime.now() < e.deadline]


@app.get("/event/{event_id}")
async def get_event(event_id: str) -> Event | None:
    try:
        return events[event_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")


@app.put("/event")
async def upsert_event(event: Event) -> Event:
    if event.id not in events:
        events[event.id] = event
        return {}

    for p_name, p_value in event.dict(exclude_unset=True).items():
        setattr(events[event.id], p_name, p_value)

    return events[event.id]
