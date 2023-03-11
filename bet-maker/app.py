import logging
from datetime import datetime
from os import getenv
from typing import List

import aiohttp
from asyncache import cached
from cachetools import TTLCache
from fastapi import Depends, FastAPI, HTTPException

from common.dto import Event, EventStatus, Bet
from db import async_sessionmaker

LINE_PROVIDER_EVENTS_URL = getenv("LINE_PROVIDER_EVENTS_URL")
app = FastAPI(title="bet-maker")


@app.get("/events")
@cached(TTLCache(1, 30))
async def get_events() -> List[Event]:
    async with aiohttp.ClientSession() as session:
        async with session.get(LINE_PROVIDER_EVENTS_URL) as response:
            logging.info("fetched line-provider /events")
            return [Event(**e) for e in await response.json()]


@app.post("/bet")
async def create_bet(bet: Bet) -> Bet:
    pass


@app.get("/bet/{bet_id}", responses={200: {"model": Event}, 404: {}})
async def get_bet(bet_id: str):
    try:
        pass
    except KeyError:
        raise HTTPException(status_code=404, detail="Bet not found")


@app.post("/callback")
async def callback(event: Event) -> Event:
    pass
