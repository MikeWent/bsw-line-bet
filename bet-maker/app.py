import logging
from os import getenv
from typing import List

import aiohttp
from asyncache import cached
from cachetools import TTLCache
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
import datetime

import models
from common import dto
from db import get_session, init_db, AsyncSession

LINE_PROVIDER_URL = getenv("LINE_PROVIDER_URL")
app = FastAPI(title="bet-maker")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/events")
@cached(TTLCache(1, 5))
async def get_events() -> List[dto.Event]:
    async with aiohttp.ClientSession() as session:
        async with session.get(LINE_PROVIDER_URL + "/events") as response:
            logging.info("fetched new line-provider /events")
            return [dto.Event(**e) for e in await response.json()]


@app.post("/bet", responses={202: {"model": dto.Bet}, 403: {}})
async def create_bet(bet: dto.Bet, db_session: AsyncSession = Depends(get_session)):
    if await db_session.get(models.Bet, bet.id):
        raise HTTPException(403, detail="Bet already exists")

    async with aiohttp.ClientSession() as session:
        async with session.get(LINE_PROVIDER_URL + f"/event/{bet.id}") as response:
            if response.status == 404:
                raise HTTPException(status_code=404, detail="Event not found")

            event = dto.Event(**(await response.json()))
            if (
                event.deadline < datetime.datetime.now()
                or event.status != dto.EventStatus.NEW
            ):
                raise HTTPException(status_code=403, detail="Event is past deadline")

    new_bet = models.Bet(**bet.dict(exclude_unset=True), status=event.status)
    db_session.add(new_bet)
    await db_session.commit()
    print(new_bet)
    return new_bet


@app.get("/bet/{bet_id}", responses={200: {"model": dto.Bet}, 404: {}})
async def get_bet(bet_id: str, db_session: AsyncSession = Depends(get_session)):
    bet = await db_session.get(models.Bet, bet_id)
    if not bet:
        raise HTTPException(status_code=404, detail="Bet not found")
    return bet


@app.get("/bets")
async def get_bets(db_session: AsyncSession = Depends(get_session)) -> List[dto.Bet]:
    return (await db_session.execute(select(models.Bet))).scalars().all()


@app.post("/callback", include_in_schema=False)
async def callback(
    event: dto.Event, db_session: AsyncSession = Depends(get_session)
) -> None:
    bet: models.Bet = await db_session.get(models.Bet, event.id)
    if not bet:
        return
    bet.status = event.status
    await db_session.merge(bet)
    await db_session.commit()
