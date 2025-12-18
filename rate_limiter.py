import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self,app):
        super().__init__(app)
        self.tokens = {}
        self.capacity = 5
        self.refill_rate = 1 # token refill per sec
        self.buckets={}

    async def dispatch(self, request: Request, call_next):
            # Apply only to booking endpoint
            if request.url.path != "/bookings":
                return await call_next(request)

            client_ip = request.client.host
            current_time = time.time()

            if client_ip not in self.buckets:
                self.buckets[client_ip] = {
                    "tokens": self.capacity,
                    "last_time": current_time
                }

            bucket = self.buckets[client_ip]

            # Refill tokens
            elapsed = current_time - bucket["last_time"]
            bucket["tokens"] = min(
                self.capacity,
                bucket["tokens"] + elapsed * self.refill_rate
            )
            bucket["last_time"] = current_time

            if bucket["tokens"] < 1:
                return Response(
                    content="Too Many Requests",
                    status_code=429
                )

            bucket["tokens"] -= 1
            return await call_next(request)