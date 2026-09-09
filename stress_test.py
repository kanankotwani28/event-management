import os, gc, time
os.environ["DATABASE_URL"] = "sqlite:///./stress.db"

from concurrent.futures import ThreadPoolExecutor, as_completed
from database import SessionLocal, engine, Base
from model import Event, Booking

Base.metadata.create_all(bind=engine)

def test_scenario(capacity, requests, per_request, workers):
    db = SessionLocal()
    ev = Event(name="S", total_seats=capacity, available_seats=capacity)
    db.add(ev)
    db.commit()
    eid = ev.id
    db.close()

    def book():
        db = SessionLocal()
        try:
            evt = db.query(Event).filter(Event.id == eid).with_for_update().first()
            if not evt or evt.available_seats < per_request:
                return False
            evt.available_seats -= per_request
            db.add(Booking(event_id=eid, seat_count=per_request))
            db.commit()
            return True
        except:
            db.rollback()
            return False
        finally:
            db.close()

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(book) for _ in range(requests)]
        succ = sum(1 for f in as_completed(futs) if f.result())
    dur = time.perf_counter() - t0

    db = SessionLocal()
    ev = db.query(Event).get(eid)
    total_b = sum(b.seat_count for b in db.query(Booking).filter(Booking.event_id == eid).all())
    db.close()
    return capacity, requests, succ, total_b, dur

scenarios = [
    (50, 200, 1, 50),
    (100, 500, 1, 50),
    (100, 1000, 1, 100),
    (20, 200, 2, 30),
    (30, 150, 3, 40),
]

header = f"{'Capacity':>8} {'Requests':>10} {'PerReq':>6} {'Workers':>8} {'Succeeded':>10} {'Oversell':>9} {'Duration':>9} {'TPS':>8}"
print(header)
print("-" * len(header))
for cap, req, p, w in scenarios:
    c, r, succ, total, dur = test_scenario(cap, req, p, w)
    oversell = max(0, total - c)
    tps = r / dur
    status = f"{c:>8} {r:>10} {p:>6} {w:>8} {succ:>10} {oversell:>9} {dur:>8.2f}s {tps:>7.0f}"
    print(status)
    assert oversell == 0, f"FAIL: {oversell} oversold!"

gc.collect()
engine.dispose()
time.sleep(0.5)
for f in ["stress.db", "stress.db-wal", "stress.db-shm"]:
    try: os.remove(f)
    except: pass
print("-" * len(header))
print("All scenarios: ZERO oversells. No race conditions detected.")
