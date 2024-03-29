import json
import logging
from datetime import datetime, timedelta
from os import getenv

import aiohttp
from fastapi import FastAPI, HTTPException

from common.dto import Event, EventStatus

BET_MAKER_CALLBACK_URL = getenv(
    "BET_MAKER_CALLBACK_URL", "http://localhost:9090/callback"
)
app = FastAPI(title="lineprovider")


events: dict[int, Event] = {}


@app.on_event("startup")
async def startup():
    await upsert_event(
        Event(
            id=1,
            coefficient=1.20,
            deadline=datetime.now() + timedelta(minutes=10),
            status=EventStatus.NEW,
        )
    )
    await upsert_event(
        Event(
            id=2,
            coefficient=1.15,
            deadline=datetime.now() + timedelta(minutes=5),
            status=EventStatus.NEW,
        )
    )
    await upsert_event(
        Event(
            id=3,
            coefficient=1.67,
            deadline=datetime.now() + timedelta(minutes=1),
            status=EventStatus.NEW,
        )
    )


@app.get("/events")
async def get_events() -> list[Event]:
    """
    Get all available Events.
    """
    return [e for e in events.values() if datetime.now() < e.deadline]


@app.get("/event/{event_id}", responses={200: {"model": Event}, 404: {}})
async def get_event(event_id: str):
    """
    Get an Event by id.
    """
    try:
        return events[event_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Event not found") from exc


@app.put("/event")
async def upsert_event(event: Event) -> Event:
    """
    Create or update an Event. This also sends a callback to BetMaker.
    """
    if event.id not in events:
        events[event.id] = event
    else:
        for p_name, p_value in event.dict(exclude_unset=True).items():
            setattr(events[event.id], p_name, p_value)

    try:
        async with aiohttp.ClientSession(
            # serialize Decimal as str
            json_serialize=lambda j: json.dumps(j, default=str)
        ) as session:
            await session.post(
                url=BET_MAKER_CALLBACK_URL, json=events[event.id].dict(), timeout=5
            )
            logging.info("callback for %s sent to betmaker", event.id)
    except aiohttp.ClientError as exc:
        logging.warning("unable to send callback for %s to betmaker: %s", event.id, exc)

    return events[event.id]
