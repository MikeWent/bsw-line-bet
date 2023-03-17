import enum

from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    coefficient = Column(DECIMAL)
    deadline = Column(DateTime)

    class EventStatus(str, enum.Enum):
        NEW = "new"
        FINISHED_WIN = "finished_win"
        FINISHED_LOSE = "finished_lose"

    status = Column(Enum(EventStatus))


class Bet(Base):
    __tablename__ = "bets"

    id = Column(Integer, primary_key=True)
    amount = Column(DECIMAL)
    event_id = Column(Integer, ForeignKey("events.id"))

    event = relationship("Event", lazy="joined")
