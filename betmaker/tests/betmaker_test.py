from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime, timedelta

from app import app

client = TestClient(app)


def test_create_bet():
    response = client.post("/bet", json={"event_id": 1, "amount": 1})
    bet = response.json()
    assert bet["event_id"] == 1
    assert bet["amount"] == "1.00"


def test_get_events():
    response = client.get("/events")
    assert isinstance(response.json(), list)
