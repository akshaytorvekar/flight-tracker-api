# ✈️ Flight Tracker API

This is a FastAPI-based middleware service that scrapes flight data from [FlightStats](https://www.flightstats.com/v2/flight-tracker/search), stores it in a database, and returns the result via a RESTful API endpoint.

---

## 🚀 Features

- REST API endpoint to fetch flight data
- Web scraping using `requests` and `BeautifulSoup`
- Flight data persistence using SQLite and SQLAlchemy
- Caching of repeated requests via database check
- Basic test cases with `TestClient`

---

## 🔧 Tech Stack

- **FastAPI** (for the API)
- **SQLAlchemy** (for ORM/database)
- **SQLite** (for local DB)
- **BeautifulSoup4** (for scraping)
- **Uvicorn** (for running the app)
- **Pytest** (for testing)

---

## 🛠️ Installation

```bash
# Clone the repo
git clone https://github.com/your-username/flight-tracker-api.git
cd flight-tracker-api

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt