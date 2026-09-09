import os, gc, time, sys
os.environ["DATABASE_URL"] = "sqlite:///./test_events.db"

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from database import SessionLocal, engine, Base
from model import Event, Booking

TOTAL_SEATS = 100
NUM_REQUESTS = 500
SEATS_PER_REQUEST = 1
MAX_WORKERS = 50

def setup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    event = Event(name="Concert", total_seats=TOTAL_SEATS, available_seats=TOTAL_SEATS)
    db.add(event)
    db.commit()
    eid = event.id
    db.close()
    return eid

def attempt_booking(event_id, seat_count):
    db = SessionLocal()
    try:
        event = db.query(Event).filter(Event.id == event_id).with_for_update().first()
        if not event or event.available_seats < seat_count:
            db.rollback()
            return False
        event.available_seats -= seat_count
        booking = Booking(event_id=event_id, seat_count=seat_count)
        db.add(booking)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()

def verify(event_id):
    db = SessionLocal()
    event = db.query(Event).filter(Event.id == event_id).with_for_update().first()
    bookings = db.query(Booking).filter(Booking.event_id == event_id).all()
    total_booked = sum(b.seat_count for b in bookings)
    db.close()
    return event, total_booked, len(bookings)

def run():
    event_id = setup()
    start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(attempt_booking, event_id, SEATS_PER_REQUEST) for _ in range(NUM_REQUESTS)]
        success = 0
        failure = 0
        for f in as_completed(futures):
            if f.result():
                success += 1
            else:
                failure += 1

    elapsed = time.perf_counter() - start
    event, total_booked, booking_count = verify(event_id)

    print("=" * 60)
    print("  CONCURRENT SEAT ALLOCATION — LOAD TEST REPORT")
    print("=" * 60)
    print(f"  Database:           {os.environ['DATABASE_URL']}")
    print(f"  Isolation:          {'BEGIN IMMEDIATE (SQLite)' if 'sqlite' in os.environ['DATABASE_URL'] else 'SERIALIZABLE (PostgreSQL)'}")
    print(f"  Row locking:        SELECT ... FOR UPDATE")
    print(f"  Workers:            {MAX_WORKERS}")
    print()
    print(f"  Event capacity:     {event.total_seats} seats")
    print(f"  Requests fired:     {NUM_REQUESTS}")
    print(f"  Seats per request:  {SEATS_PER_REQUEST}")
    print(f"  Duration:           {elapsed:.2f}s")
    print(f"  Throughput:         {NUM_REQUESTS/elapsed:.0f} req/s")
    print()
    print(f"  Succeeded:          {success}/{NUM_REQUESTS}")
    print(f"  Rejected:           {failure}/{NUM_REQUESTS}")
    print(f"  Acceptance rate:    {success/NUM_REQUESTS*100:.1f}%")
    print()
    print(f"  Seats sold:         {total_booked}")
    print(f"  Seats remaining:    {event.available_seats}")
    print(f"  Total capacity:     {event.total_seats}")
    print(f"  Integrity check:    {event.available_seats} + {total_booked} = {event.available_seats + total_booked} == {event.total_seats}")
    print()
    oversell = total_booked - event.total_seats
    if oversell > 0:
        print(f"  OVERSELLS:          {oversell} seats - FAILED")
        return False
    else:
        print(f"  OVERSELLS:          0 (ZERO overbooking across {NUM_REQUESTS} concurrent requests)")
    print("=" * 60)

    assert event.available_seats + total_booked == event.total_seats, "Integrity violation!"
    assert event.available_seats >= 0
    assert success == total_booked
    print("  All assertions PASSED.")
    return True

if __name__ == "__main__":
    try:
        if not run():
            sys.exit(1)
    finally:
        gc.collect()
        engine.dispose()
        time.sleep(0.5)
        for f in ["test_events.db", "test_events.db-wal", "test_events.db-shm"]:
            try:
                os.remove(f)
            except (PermissionError, FileNotFoundError):
                pass
