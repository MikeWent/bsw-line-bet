from sqlalchemy import Boolean, DECIMAL, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class BetStatus(str, enum.Enum):
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


class Bet(Base):
    __tablename__ = "bets"

    id = Column(String, primary_key=True)
    amount = Column(DECIMAL)
    status = Column(Enum(BetStatus))
