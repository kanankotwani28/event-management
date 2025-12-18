from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    total_seats = Column(Integer)
    available_seats = Column(Integer)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("events.id"))
    seat_count = Column(Integer)
