import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_api_disease_tomato_early_blight():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/disease", json={"disease": "Tomato Early Blight"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["disease"] == "Early Blight"
    assert data["plant"] == "Tomato"
    assert data["type"] == "Fungal"
    assert "description" in data
    assert isinstance(data["symptoms"], list)
    assert len(data["symptoms"]) > 0
    assert "Alternaria" in data["cause"]
    assert isinstance(data["treatment"], list)
    assert isinstance(data["prevention"], list)
    assert isinstance(data["sources"], list)
    assert "🌱 Plant Disease Information" in data["formatted_output"]

@pytest.mark.asyncio
async def test_api_disease_unknown():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/disease", json={"disease": "xyz disease"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "unknown"
    assert "couldn't confidently identify" in data["message"]
    assert "Example:" in data["message"]

@pytest.mark.asyncio
async def test_api_disease_ambiguous():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/disease", json={"disease": "Early Blight"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ambiguous"
    assert len(data["matches"]) >= 2
    assert "Tomato Early Blight" in data["matches"]
    assert "Potato Early Blight" in data["matches"]

@pytest.mark.asyncio
async def test_api_autocomplete_suggest():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/diseases/suggest?q=Tomato")
    assert response.status_code == 200
    data = response.json()
    assert "suggestions" in data
    assert any("Tomato Early Blight" in s["name"] for s in data["suggestions"])

@pytest.mark.asyncio
async def test_api_diagnose_image():
    # Create fake jpeg bytes
    fake_img = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb"
    files = {"file": ("sample_leaf_early_blight.jpg", fake_img, "image/jpeg")}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/disease/diagnose-image", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "predicted_disease" in data
    assert "confidence" in data
