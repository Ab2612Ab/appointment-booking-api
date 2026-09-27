# Appointment Booking API

A production-style appointment scheduling REST API built with **Python + FastAPI**.

## Features

- Create and validate appointments
- Service catalog
- Real-time availability checks
- Appointment conflict detection
- Appointment lookup and listing
- Filter appointments by status
- Cancel appointments
- UTC-aware datetime handling
- Email validation with Pydantic
- CORS configuration
- Interactive Swagger and ReDoc documentation
- Automated API tests
- Vercel deployment configuration

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | / | API information |
| GET | /health | Health check |
| GET | /services | List services |
| GET | /availability | Check a requested time |
| POST | /appointments | Create an appointment |
| GET | /appointments | List appointments |
| GET | /appointments/{id} | Get one appointment |
| DELETE | /appointments/{id} | Cancel an appointment |
| GET | /docs | Swagger UI |
| GET | /redoc | ReDoc |

## Tech Stack

Python, FastAPI, Pydantic, Uvicorn, Pytest.

## Production upgrade

The current demo uses in-memory storage. A production deployment should add PostgreSQL/Supabase, authentication and role-based access, persistent availability rules, background notifications, rate limiting, audit logging, and calendar integrations.
