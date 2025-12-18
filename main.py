from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from fastapi.params import Depends
from model import Event, Booking
from schemas import EventCreate, BookingCreate

app = FastAPI()

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/events")
def get_all_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events


# event endpoint 
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

#booking endpoint
@app.post("/bookings")
def book_event(booking: BookingCreate, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == booking.event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if booking.seat_count <= 0:
        raise HTTPException(status_code=400, detail="Seat count must be positive")
    
    if event.available_seats < booking.seat_count:
        raise HTTPException(status_code=400, detail="Sorry! Not enough seats available")
    
    event.available_seats -= booking.seat_count
    new_booking = Booking(
        event_id=booking.event_id,
        seat_count=booking.seat_count
    )
    db.add(new_booking)
    db.commit()
    return {"message":"Booking_successful"}

@app.get("/events/{event_id}/bookings")
def get_event_bookings(event_id: int, db: Session = Depends(get_db)):
    return db.query(Booking).filter(Booking.event_id == event_id).all()