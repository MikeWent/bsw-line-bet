import logging
from datetime import datetime, timedelta
from os import getenv
from typing import List

from fastapi import FastAPI, HTTPException
import aiohttp

from common.dto import Event, EventStatus

BET_MAKER_CALLBACK_URL = getenv("BET_MAKER_CALLBACK_URL")
app = FastAPI(title="line-provider")


events: dict[str, Event] = {
    "1": Event(
        id=1,
        coefficient=1.20,
        deadline=datetime.now() + timedelta(minutes=10),
        status=EventStatus.NEW,
    ),
    "2": Event(
        id=2,
        coefficient=1.15,
        deadline=datetime.now() + timedelta(minutes=5),
        status=EventStatus.NEW,
    ),
    "3": Event(
        id=3,
        coefficient=1.67,
        deadline=datetime.now() + timedelta(minutes=1),
        status=EventStatus.NEW,
    ),
}


@app.get("/events")
async def get_events() -> List[Event]:
    return [e for e in events.values() if datetime.now() < e.deadline]


@app.get("/event/{event_id}", responses={200: {"model": Event}, 404: {}})
async def get_event(event_id: str):
    try:
        return events[event_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Event not found")


@app.put("/event")
async def upsert_event(event: Event) -> Event:
    if event.id not in events:
        events[event.id] = event
        return event

    for p_name, p_value in event.dict(exclude_unset=True).items():
        setattr(events[event.id], p_name, p_value)
    logging.info("event upserted: {event}")

    if event.status in (EventStatus.FINISHED_WIN, EventStatus.FINISHED_LOSE):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=BET_MAKER_CALLBACK_URL, json=event.dict(), timeout=5
                ) as resp:
                    logging.info(
                        f"callback {event.id}={event.status} sent to bet-maker, got {resp.status}."
                    )
        except Exception as e:
            logging.warn(
                f"unable to send {event.id}={event.status} callback to bet-maker: {e}"
            )

    return events[event.id]
