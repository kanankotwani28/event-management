from fastapi import FastAPI
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from fastapi.params import Depends
from model import Event
from schemas import EventCreate

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from main"}

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/events")
def create_event(event: EventCreate, db: Session = Depends(get_db)):
    new_event = Event(
        name=event.name,
        total_seats=event.total_seats,
        available_seats=event.total_seats
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event