"""GripWise Backend Tests — Vehicle and tyre position endpoints."""
import pytest


async def _register_and_login(client, email="v_rider@test.com"):
    await client.post("/api/auth/register", json={
        "display_name": "Vehicle Rider",
        "email": email,
        "password": "password123",
        "role": "RIDER",
    })
    resp = await client.post("/api/auth/login", json={"credential": email, "password": "password123"})
    return resp.json()["data"]["access_token"]


@pytest.mark.asyncio
async def test_create_vehicle(client):
    token = await _register_and_login(client, "vcreate@test.com")
    resp = await client.post(
        "/api/vehicles",
        json={"make": "Honda", "model": "Activa 6G", "year": 2022, "vehicle_type": "SCOOTER"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["make"] == "Honda"
    assert data["tyre_positions"] == []


@pytest.mark.asyncio
async def test_list_vehicles_own_only(client):
    t1 = await _register_and_login(client, "vlist1@test.com")
    t2 = await _register_and_login(client, "vlist2@test.com")

    await client.post("/api/vehicles", json={"make": "Yamaha", "model": "FZ-S", "vehicle_type": "MOTORCYCLE"}, headers={"Authorization": f"Bearer {t1}"})
    resp = await client.get("/api/vehicles", headers={"Authorization": f"Bearer {t2}"})
    assert resp.status_code == 200
    # Rider 2 should NOT see rider 1's vehicle
    vehicles = resp.json()["data"]["vehicles"]
    assert all(v["make"] != "Yamaha" for v in vehicles)


@pytest.mark.asyncio
async def test_add_tyre_position(client):
    token = await _register_and_login(client, "vtp@test.com")
    vresp = await client.post("/api/vehicles", json={"make": "TVS", "model": "Apache", "vehicle_type": "MOTORCYCLE"}, headers={"Authorization": f"Bearer {token}"})
    vid = vresp.json()["data"]["vehicle_id"]

    resp = await client.post(
        f"/api/vehicles/{vid}/tyre-positions",
        json={"position": "FRONT", "brand": "MRF", "size_spec": "90/90-17"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["data"]["position"] == "FRONT"


@pytest.mark.asyncio
async def test_add_duplicate_tyre_position(client):
    token = await _register_and_login(client, "vdup@test.com")
    vresp = await client.post("/api/vehicles", json={"make": "TVS", "model": "Star", "vehicle_type": "MOTORCYCLE"}, headers={"Authorization": f"Bearer {token}"})
    vid = vresp.json()["data"]["vehicle_id"]

    await client.post(f"/api/vehicles/{vid}/tyre-positions", json={"position": "REAR"}, headers={"Authorization": f"Bearer {token}"})
    resp = await client.post(f"/api/vehicles/{vid}/tyre-positions", json={"position": "REAR"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_cannot_access_other_riders_vehicle(client):
    t1 = await _register_and_login(client, "vother1@test.com")
    t2 = await _register_and_login(client, "vother2@test.com")

    vresp = await client.post("/api/vehicles", json={"make": "Bajaj", "model": "Pulsar", "vehicle_type": "MOTORCYCLE"}, headers={"Authorization": f"Bearer {t1}"})
    vid = vresp.json()["data"]["vehicle_id"]

    resp = await client.get(f"/api/vehicles/{vid}", headers={"Authorization": f"Bearer {t2}"})
    assert resp.status_code == 404
