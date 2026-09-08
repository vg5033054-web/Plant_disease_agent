import pytest
from backend.agents.disease_agent import PlantDiseaseAgent
from backend.utils.normalization import normalize_disease_name
from backend.utils.validation import validate_disease_input

@pytest.fixture
def agent():
    return PlantDiseaseAgent()

def test_validation():
    # Empty query
    is_valid, _, err = validate_disease_input("")
    assert not is_valid
    assert "empty" in err.lower()

    # Whitespace only
    is_valid, _, err = validate_disease_input("    ")
    assert not is_valid

    # Pure special characters
    is_valid, _, err = validate_disease_input("???!!!")
    assert not is_valid

    # Valid string
    is_valid, cleaned, err = validate_disease_input("  Tomato Early Blight  ")
    assert is_valid
    assert cleaned == "Tomato Early Blight"
    assert err is None

def test_normalization():
    # Test case: "early blight tomato"
    norm, plant, disease = normalize_disease_name("early blight tomato")
    assert "Tomato" in norm
    assert "Early Blight" in norm

    # Test case: "tomato early blight disease"
    norm, plant, disease = normalize_disease_name("tomato early blight disease")
    assert "Tomato" in norm
    assert "Early Blight" in norm

    # Test case: "Early-Blight"
    norm, plant, disease = normalize_disease_name("Early-Blight")
    assert "Early Blight" in norm

    # Test case: "Apple-Scab"
    norm, plant, disease = normalize_disease_name("Apple-Scab")
    assert "Apple Scab" in norm

@pytest.mark.asyncio
async def test_required_disease_tomato_early_blight(agent):
    res = await agent.run("Tomato Early Blight")
    assert res.status == "success"
    assert res.data is not None
    assert res.data.disease == "Early Blight"
    assert res.data.plant == "Tomato"
    assert res.data.type == "Fungal"
    assert "Alternaria solani" in res.data.cause
    assert len(res.data.symptoms) > 0
    assert len(res.data.treatment) > 0
    assert len(res.data.prevention) > 0
    assert len(res.data.sources) > 0
    assert "🌱 Plant Disease Information" in res.formatted_output

@pytest.mark.asyncio
async def test_required_disease_tomato_late_blight(agent):
    res = await agent.run("Tomato Late Blight")
    assert res.status == "success"
    assert res.data is not None
    assert res.data.disease == "Late Blight"
    assert res.data.plant == "Tomato"
    assert res.data.type == "Fungal"
    assert "Phytophthora infestans" in res.data.cause

@pytest.mark.asyncio
async def test_required_disease_potato_late_blight(agent):
    res = await agent.run("Potato Late Blight")
    assert res.status == "success"
    assert res.data is not None
    assert res.data.disease == "Late Blight"
    assert res.data.plant == "Potato"
    assert res.data.type == "Fungal"
    assert "Phytophthora infestans" in res.data.cause

@pytest.mark.asyncio
async def test_required_disease_apple_scab(agent):
    res = await agent.run("Apple Scab")
    assert res.status == "success"
    assert res.data is not None
    assert res.data.disease == "Apple Scab"
    assert res.data.plant == "Apple"
    assert res.data.type == "Fungal"
    assert "Venturia inaequalis" in res.data.cause

@pytest.mark.asyncio
async def test_required_disease_powdery_mildew(agent):
    res = await agent.run("Powdery Mildew")
    # Powdery mildew can affect multiple plants, our agent returns the broad host entry or options
    assert res.status in ["success", "ambiguous"]
    if res.status == "success":
        assert "Powdery Mildew" in res.data.disease
        assert res.data.type == "Fungal"
    elif res.status == "ambiguous":
        assert len(res.matches) > 0

@pytest.mark.asyncio
async def test_required_disease_unknown_xyz(agent):
    res = await agent.run("Unknown Disease XYZ")
    assert res.status == "unknown"
    assert "couldn't confidently identify" in res.message or "could not verify" in res.message
    assert "Example:" in res.message

@pytest.mark.asyncio
async def test_messy_input_normalization(agent):
    res = await agent.run("early blight tomato")
    assert res.status == "success"
    assert res.data.disease == "Early Blight"
    assert res.data.plant == "Tomato"

@pytest.mark.asyncio
async def test_ambiguity_handling(agent):
    # Querying just "Late Blight" without specifying host should prompt disambiguation
    res = await agent.run("Late Blight")
    assert res.status == "ambiguous"
    assert "Tomato Late Blight" in res.matches
    assert "Potato Late Blight" in res.matches
