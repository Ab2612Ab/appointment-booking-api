from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, EmailStr, Field

app = FastAPI(
    title="Appointment Booking API",
    description="A production-style appointment scheduling REST API built with Python and FastAPI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppointmentStatus(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


class AppointmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    customer_name: str = Field(min_length=2, max_length=100)
    customer_email: EmailStr
    service: str = Field(min_length=2, max_length=120)
    starts_at: datetime
    duration_minutes: int = Field(default=60, ge=15, le=240)


class Appointment(AppointmentCreate):
    id: str
    status: AppointmentStatus
    created_at: datetime


appointments: dict[str, Appointment] = {}

SERVICES = [
    {"id": "consultation", "name": "Consultation", "duration_minutes": 30},
    {"id": "website-review", "name": "Website Review", "duration_minutes": 60},
    {"id": "development-call", "name": "Development Call", "duration_minutes": 60},
]


def normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def overlaps(start_a: datetime, duration_a: int, start_b: datetime, duration_b: int) -> bool:
    end_a = start_a.timestamp() + duration_a * 60
    end_b = start_b.timestamp() + duration_b * 60
    return start_a.timestamp() < end_b and start_b.timestamp() < end_a


@app.get("/")
def root():
    return {
        "name": "Appointment Booking API",
        "version": app.version,
        "python": True,
        "framework": "FastAPI",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "appointment-booking-api"}


@app.get("/services")
def list_services():
    return {"services": SERVICES}


@app.get("/availability")
def availability(
    starts_at: datetime = Query(..., description="Requested start time in ISO-8601 format"),
    duration_minutes: int = Query(60, ge=15, le=240),
):
    requested = normalize_dt(starts_at)
    conflicts = [
        item
        for item in appointments.values()
        if item.status == AppointmentStatus.confirmed
        and overlaps(requested, duration_minutes, normalize_dt(item.starts_at), item.duration_minutes)
    ]
    return {
        "available": len(conflicts) == 0,
        "starts_at": requested,
        "duration_minutes": duration_minutes,
    }


@app.post("/appointments", response_model=Appointment, status_code=201)
def create_appointment(payload: AppointmentCreate):
    requested = normalize_dt(payload.starts_at)

    if requested <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Appointment must be in the future.")

    for item in appointments.values():
        if item.status == AppointmentStatus.confirmed and overlaps(
            requested, payload.duration_minutes, normalize_dt(item.starts_at), item.duration_minutes
        ):
            raise HTTPException(status_code=409, detail="That appointment time is already booked.")

    appointment = Appointment(
        id=str(uuid4()),
        customer_name=payload.customer_name,
        customer_email=payload.customer_email,
        service=payload.service,
        starts_at=requested,
        duration_minutes=payload.duration_minutes,
        status=AppointmentStatus.confirmed,
        created_at=datetime.now(timezone.utc),
    )
    appointments[appointment.id] = appointment
    return appointment


@app.get("/appointments/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: str):
    appointment = appointments.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    return appointment


@app.get("/appointments", response_model=list[Appointment])
def list_appointments(
    status: Optional[AppointmentStatus] = None,
):
    items = list(appointments.values())
    if status:
        items = [item for item in items if item.status == status]
    return sorted(items, key=lambda item: item.starts_at)


@app.delete("/appointments/{appointment_id}", response_model=Appointment)
def cancel_appointment(appointment_id: str):
    appointment = appointments.get(appointment_id)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found.")
    if appointment.status == AppointmentStatus.cancelled:
        return appointment

    cancelled = appointment.model_copy(update={"status": AppointmentStatus.cancelled})
    appointments[appointment_id] = cancelled
    return cancelled
