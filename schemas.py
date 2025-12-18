from pydantic import BaseModel

class EventCreate(BaseModel):
    name: str
    total_seats: int

class BookingCreate(BaseModel):
    event_id: int
    seat_count : int