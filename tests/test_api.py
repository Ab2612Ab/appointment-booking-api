from fastapi.testclient import TestClient

from api.index import app, appointments

client = TestClient(app)


def setup_function():
    appointments.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_create_and_read_appointment():
    payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "service": "Website Review",
        "starts_at": "2030-06-20T14:00:00Z",
        "duration_minutes": 60,
    }
    response = client.post("/appointments", json=payload)
    assert response.status_code == 201

    appointment_id = response.json()["id"]
    fetched = client.get(f"/appointments/{appointment_id}")
    assert fetched.status_code == 200
    assert fetched.json()["customer_email"] == "jane@example.com"


def test_conflicting_appointments_are_rejected():
    payload = {
        "customer_name": "Jane Doe",
        "customer_email": "jane@example.com",
        "service": "Consultation",
        "starts_at": "2030-06-20T14:00:00Z",
        "duration_minutes": 60,
    }
    assert client.post("/appointments", json=payload).status_code == 201
    assert client.post("/appointments", json=payload).status_code == 409
