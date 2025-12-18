# Event Management Backend with API Rate Limiting

## 📌 Project Overview
A backend service built with **FastAPI** to manage events and seat bookings, with **API rate limiting** applied to critical endpoints to prevent abuse and ensure system stability.

The system supports:
- Creating events with a fixed number of seats
- Booking seats with validation to prevent overbooking
- Protecting booking APIs using a **Token Bucket–based rate limiter**

---

## 🛠️ Tech Stack
- **Backend:** FastAPI (Python)
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Middleware:** Custom rate limiting middleware
- **API Docs:** Swagger (OpenAPI)

---

## 🏗️ Architecture


Client
   ↓
Rate Limiting Middleware
   ↓
FastAPI Routes
   ↓
Business Logic
   ↓
SQLite Database


- Rate limiting middleware intercepts requests before booking logic
- Business rules and validations are handled at the API layer
- Data is persisted using SQLAlchemy ORM

---

## ⏱️ Rate Limiting Strategy
The booking endpoint is protected using a **Token Bucket algorithm**.

- Each client is assigned a bucket with limited tokens
- Tokens refill at a fixed rate over time
- Each booking request consumes one token
- Requests exceeding the limit receive **HTTP 429 – Too Many Requests**
- Rate limiting is applied only to critical endpoints to avoid unnecessary restrictions

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|------|---------|-------------|
| POST | `/events` | Create a new event |
| GET | `/events` | Fetch all available events |
| POST | `/bookings` | Book seats for an event (rate limited) |
| GET | `/events/{id}/bookings` | View bookings for a specific event |

---

## ▶️ How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt

### 2. Start the server
```bash
uvicorn main:app --reload

### 3. Access the API
 ```bash
API Base URL: http://127.0.0.1:8000
Swagger Docs: http://127.0.0.1:8000/docs
