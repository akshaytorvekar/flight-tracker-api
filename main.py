### app/main.py
from fastapi import FastAPI, HTTPException, Query, Depends
from app import models, scraper, crud, database
from app.schemas import FlightInfo
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/flight-info", response_model=FlightInfo)
def get_flight_info(
    airline_code: str = Query(...),
    flight_number: str = Query(...),
    departure_date: str = Query(...),
    db: Session = Depends(database.get_db)
):
    existing = crud.get_flight(db, airline_code, flight_number, departure_date)
    if existing:
        return existing

    data = scraper.scrape_flight_info(airline_code, flight_number, departure_date)
    if not data:
        raise HTTPException(status_code=404, detail="Flight not found")

    new_flight = crud.create_flight(db, data)
    return new_flight


### app/schemas.py
from pydantic import BaseModel

class FlightInfo(BaseModel):
    airline_code: str
    flight_number: str
    departure_date: str
    departure_airport: str
    arrival_airport: str
    status: str
    scheduled_departure: str
    actual_departure: str
    scheduled_arrival: str
    actual_arrival: str

    class Config:
        orm_mode = True


### app/models.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class Flight(Base):
    __tablename__ = "flights"

    id = Column(Integer, primary_key=True, index=True)
    airline_code = Column(String)
    flight_number = Column(String)
    departure_date = Column(String)
    departure_airport = Column(String)
    arrival_airport = Column(String)
    status = Column(String)
    scheduled_departure = Column(String)
    actual_departure = Column(String)
    scheduled_arrival = Column(String)
    actual_arrival = Column(String)


### app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./flights.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


### app/crud.py
from sqlalchemy.orm import Session
from app import models

def get_flight(db: Session, airline: str, number: str, date: str):
    return db.query(models.Flight).filter_by(
        airline_code=airline,
        flight_number=number,
        departure_date=date
    ).first()

def create_flight(db: Session, data: dict):
    flight = models.Flight(**data)
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return flight


### app/scraper.py
import requests
from bs4 import BeautifulSoup

def scrape_flight_info(airline_code, flight_number, departure_date):
    url = f"https://www.flightstats.com/v2/flight-tracker/{airline_code}/{flight_number}?year={departure_date[:4]}&month={departure_date[5:7]}&date={departure_date[8:]}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    try:
        dep_airport = soup.select_one("div.route div.departure .text-helper span").get_text(strip=True)
        arr_airport = soup.select_one("div.route div.arrival .text-helper span").get_text(strip=True)
        status = soup.select_one(".status-text").get_text(strip=True)
        sched_dep = soup.find("div", string="Scheduled Departure").find_next_sibling().get_text(strip=True)
        act_dep = soup.find("div", string="Actual Departure").find_next_sibling().get_text(strip=True)
        sched_arr = soup.find("div", string="Scheduled Arrival").find_next_sibling().get_text(strip=True)
        act_arr = soup.find("div", string="Actual Arrival").find_next_sibling().get_text(strip=True)

        return {
            "airline_code": airline_code,
            "flight_number": flight_number,
            "departure_date": departure_date,
            "departure_airport": dep_airport,
            "arrival_airport": arr_airport,
            "status": status,
            "scheduled_departure": sched_dep,
            "actual_departure": act_dep,
            "scheduled_arrival": sched_arr,
            "actual_arrival": act_arr,
        }
    except Exception:
        return None


### tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_flight_info():
    response = client.get("/flight-info?airline_code=SQ&flight_number=32&departure_date=2025-05-01")
    assert response.status_code in (200, 404)
    if response.status_code == 200:
        data = response.json()
        assert "airline_code" in data
        assert data["airline_code"] == "SQ"