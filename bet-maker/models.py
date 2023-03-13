from sqlalchemy import Boolean, DECIMAL, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base

from common import dto

Base = declarative_base()


class Bet(Base):
    __tablename__ = "bets"

    id = Column(String, primary_key=True)
    amount = Column(DECIMAL)
    status = Column(Enum(dto.EventStatus))
