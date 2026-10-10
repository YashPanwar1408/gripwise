import pytest
from httpx import AsyncClient
from backend.models import User, Vehicle, TyrePosition, Inspection, ConsentRecord, MechanicFinding, ServiceRecord

async def _register_and_login(client, email="m_rider@test.com"):
    await client.post("/api/auth/register", json={
        "display_name": "Test Rider",
        "email": email,
        "password": "password123",
        "role": "RIDER",
    })
    resp = await client.post("/api/auth/login", json={"credential": email, "password": "password123"})
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_mechanic_flow(client: AsyncClient, db_session):
    rider_token = await _register_and_login(client)
    rider_token_headers = {"Authorization": f"Bearer {rider_token}"}

    # 1. Register a mechanic
    res = await client.post("/api/auth/register", json={
        "display_name": "Mike Mechanic",
        "email": "mike@workshop.com",
        "password": "Password123",
        "role": "MECHANIC",
        "workshop_name": "Mike's Tyres"
    })
    assert res.status_code == 201
    mechanic_id = res.json()["data"]["user_id"]
    mechanic_token = res.json()["data"]["access_token"]
    mechanic_headers = {"Authorization": f"Bearer {mechanic_token}"}

    # 2. Rider registers a vehicle and tyre
    res = await client.post("/api/vehicles", json={
        "make": "Honda", "model": "Activa", "vehicle_type": "SCOOTER"
    }, headers=rider_token_headers)
    vehicle_id = res.json()["data"]["vehicle_id"]
    
    res = await client.post(f"/api/vehicles/{vehicle_id}/tyre-positions", json={
        "position": "FRONT"
    }, headers=rider_token_headers)
    tp_id = res.json()["data"]["tyre_position_id"]

    # 3. Rider grants consent to mechanic
    res = await client.post("/api/consent", json={"mechanic_id": mechanic_id}, headers=rider_token_headers)
    assert res.status_code == 201

    # 4. Mechanic checks consented inspections
    res = await client.get("/api/mechanic/inspections", headers=mechanic_headers)
    assert res.status_code == 200
    assert "inspections" in res.json()["data"]

    # 5. Mechanic adds a service record
    res = await client.post("/api/mechanic/service-records", json={
        "tyre_position_id": tp_id,
        "service_type": "TYRE_REPLACED"
    }, headers=mechanic_headers)
    assert res.status_code == 200

    # 6. Rider revokes consent
    consents_res = await client.get("/api/consent", headers=rider_token_headers)
    consent_id = consents_res.json()["data"][0]["id"]
    
    res = await client.delete(f"/api/consent/{consent_id}", headers=rider_token_headers)
    assert res.status_code == 200

    # 7. Mechanic tries to add another service record (should fail)
    res = await client.post("/api/mechanic/service-records", json={
        "tyre_position_id": tp_id,
        "service_type": "PRESSURE_ADJUSTED"
    }, headers=mechanic_headers)
    assert res.status_code == 403
