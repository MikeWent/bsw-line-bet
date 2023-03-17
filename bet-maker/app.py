from datetime import datetime
from os import getenv

from asyncache import cached
from cachetools import TTLCache
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import models
from common import dto
from db import AsyncSession, get_session, init_db

LINE_PROVIDER_URL = getenv("LINE_PROVIDER_URL")
app = FastAPI(title="bet-maker")


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/events")
@cached(TTLCache(1, 5))
async def get_events(
    db_session: AsyncSession = Depends(get_session),
) -> list[dto.Event]:
    """
    Get all Events available for placing a Bet.
    """
    statement = (
        select(models.Event)
        .where(models.Event.status == models.Event.EventStatus.NEW)
        .where(models.Event.deadline > datetime.now())
    )
    return (await db_session.execute(statement)).scalars().all()


@app.post("/bet", responses={202: {"model": dto.Bet}, 403: {}, 404: {}})
async def create_bet(
    bet_create: dto.BetCreate,
    db_session: AsyncSession = Depends(get_session),
) -> dto.Bet:
    """
    Place a new Bet for an Event.
    """
    event: models.Event = await db_session.get(models.Event, bet_create.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    if event.status != models.Event.EventStatus.NEW or datetime.now() > event.deadline:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Event is past deadline"
        )

    new_bet = models.Bet(**bet_create.dict(exclude_unset=True))
    db_session.add(new_bet)
    await db_session.commit()
    return new_bet


@app.get("/bet/{bet_id}", responses={200: {"model": dto.Bet}, 404: {}})
async def get_bet(
    bet_id: str,
    db_session: AsyncSession = Depends(get_session),
) -> dto.Bet:
    """
    Get a Bet by id.
    """
    bet = await db_session.get(models.Bet, bet_id)
    if not bet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Bet not found"
        )
    return bet


@app.get("/bets")
async def get_bets(
    db_session: AsyncSession = Depends(get_session),
) -> list[dto.Bet]:
    """
    Get all Bets.
    """
    statement = select(models.Bet).options(joinedload(models.Bet.event))
    return (await db_session.execute(statement)).scalars().all()


@app.post("/callback", include_in_schema=False)
async def callback(
    event: dto.Event,
    db_session: AsyncSession = Depends(get_session),
) -> dto.Event:
    """
    BetMaker's callback used to create and update Events externally. Used by LineProvider.
    """
    existing_event: models.Event = await db_session.get(models.Event, event.id)

    if not existing_event:
        new_event = models.Event(**event.dict())
        db_session.add(new_event)
        await db_session.commit()
        return new_event

    for p_name, p_value in event.dict(exclude_unset=True).items():
        setattr(existing_event, p_name, p_value)
    db_session.merge(existing_event)
    await db_session.commit()
    return existing_event
