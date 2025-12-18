from pydantic import BaseModel

class EventCreate(BaseModel):
    name: str
    total_seats: int