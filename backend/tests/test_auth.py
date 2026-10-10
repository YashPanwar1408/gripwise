"""GripWise Backend Tests — Auth endpoints."""
import pytest


@pytest.mark.asyncio
async def test_register_rider_success(client):
    resp = await client.post("/api/auth/register", json={
        "display_name": "Test Rider",
        "email": "rider1@test.com",
        "password": "password123",
        "role": "RIDER",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["role"] == "RIDER"


@pytest.mark.asyncio
async def test_register_mechanic_success(client):
    resp = await client.post("/api/auth/register", json={
        "display_name": "Test Mechanic",
        "email": "mech1@test.com",
        "password": "password123",
        "role": "MECHANIC",
        "workshop_name": "Super Tyres",
        "workshop_city": "Pune",
    })
    assert resp.status_code == 201
    assert resp.json()["data"]["role"] == "MECHANIC"


@pytest.mark.asyncio
async def test_register_mechanic_missing_workshop(client):
    resp = await client.post("/api/auth/register", json={
        "display_name": "Bad Mechanic",
        "email": "badmech@test.com",
        "password": "password123",
        "role": "MECHANIC",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_requires_email_or_mobile(client):
    resp = await client.post("/api/auth/register", json={
        "display_name": "No Contact",
        "password": "password123",
        "role": "RIDER",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    resp = await client.post("/api/auth/register", json={
        "display_name": "Short Pass",
        "email": "short@test.com",
        "password": "abc",
        "role": "RIDER",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/api/auth/register", json={
        "display_name": "First",
        "email": "dup@test.com",
        "password": "password123",
        "role": "RIDER",
    })
    resp = await client.post("/api/auth/register", json={
        "display_name": "Second",
        "email": "dup@test.com",
        "password": "password123",
        "role": "RIDER",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/api/auth/register", json={
        "display_name": "Login User",
        "email": "loginuser@test.com",
        "password": "password123",
        "role": "RIDER",
    })
    resp = await client.post("/api/auth/login", json={
        "credential": "loginuser@test.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()["data"]


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/api/auth/register", json={
        "display_name": "User WP",
        "email": "wrongpass@test.com",
        "password": "password123",
        "role": "RIDER",
    })
    resp = await client.post("/api/auth/login", json={
        "credential": "wrongpass@test.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    resp = await client.get("/api/vehicles")
    assert resp.status_code == 403  # HTTPBearer returns 403 when no credentials


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "ok"
