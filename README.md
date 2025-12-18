# Event Management Backend with API Rate Limiting

## 📌 Project Overview

This project is a backend service built using **FastAPI** for managing events and seat bookings.  
It includes **API rate limiting** on critical endpoints to prevent abuse and ensure system stability.

The system allows:
- Creating events with a fixed number of seats
- Booking seats while preventing overbooking
- Limiting excessive booking requests using a token bucket–based rate limiter

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


- The rate limiting middleware intercepts requests before they reach the booking logic.
- Business rules and validations are handled within the API layer.
- Data is persisted using SQLite via SQLAlchemy ORM.

---

## ⏱️ Rate Limiting Strategy

The booking endpoint is protected using a **Token Bucket** rate limiting algorithm.

- Each client is assigned a bucket with a fixed number of tokens.
- Tokens refill over time at a defined rate.
- Each booking request consumes one token.
- Requests exceeding the limit receive an **HTTP 429 (Too Many Requests)** response.

Rate limiting is applied **only to critical endpoints** to avoid unnecessary restrictions.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|------|--------|------------|
| POST | `/events` | Create a new event |
| GET | `/events` | Fetch all available events |
| POST | `/bookings` | Book seats for an event (**rate limited**) |
| GET | `/events/{id}/bookings` | View bookings for a specific event |

---

## ▶️ How to Run

### Install dependencies
```bash
pip install -r requirements.txt
