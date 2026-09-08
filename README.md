# Plant Disease Information Agent 🌱

A production-quality, modular AI agent and web application engineered to accept plant disease names (or messy/informal queries), normalize the input, query verified agricultural pathology sources (USDA, FAO, UC Davis IPM, Cornell AgriLife, Extension services), reason via an LLM/Expert System with strict grounding, and deliver comprehensive, structured management protocols.

---

## 🌟 Key Features

1. **Intelligent Normalization & Robust Input Handling**:
   - Accepts standard names: `Tomato Early Blight`, `Apple Scab`, `Rice Blast`.
   - Normalizes non-standard, messy syntax: `early blight tomato`, `tomato early blight disease`, `Early-Blight`.
   - Protects against invalid inputs, excessive length, and prompt injection attempts.

2. **Accurate Agricultural Pathology Profiles (No Hallucination)**:
   - **Disease Name & Affected Host Plant**
   - **Disease Type**: Fungal, Bacterial, Viral, Nematode, Abiotic, or Other.
   - **Short Biological Description**
   - **Observable Physical Symptoms**
   - **Causal Pathogen & Transmission/Vectors**
   - **Favorable Environmental Conditions**
   - **Affected Plant Parts**
   - **Disease Severity Level**
   - **Treatment & Active Interventions**
   - **Agronomic Prevention Protocols**
   - **Organic / Biological Controls** (OMRI-approved, biofungicides, cultural methods)
   - **Chemical Controls & Safety Notices** (FRAC rotation, label compliance)
   - **When to Seek Expert Agricultural Advice**
   - **Authoritative Source Citations** (USDA ARS, FAO, UC IPM, Cornell, Extension)
   - **Safety Disclaimer**

3. **Ambiguity & Unknown Disease Handling**:
   - **Unknown Disease**: If a query like `xyz disease` is entered, the agent gracefully responds with a structured prompt requesting Plant name, Disease name, and symptoms.
   - **Ambiguous Queries**: If a general disease is queried without a host plant (e.g. `Late Blight`), the agent provides clickable disambiguation options (`Tomato Late Blight`, `Potato Late Blight`).

4. **Dual Engine Operation**:
   - **LLM Grounded Mode**: Powered by Gemini or OpenAI with structured system instructions when API keys are configured in `.env`.
   - **Verified Expert System Mode**: Runs completely offline out of the box with zero external dependencies or API keys required, using curated agricultural pathology databases.

5. **Future ML Vision Classifier Integration**:
   - Built-in architecture and endpoint (`POST /api/disease/diagnose-image`) allowing computer vision models (e.g. MobileNetV3 / ResNet50 trained on PlantVillage) to classify leaf images and seamlessly hand off predicted labels to the information agent.

6. **Premium Modern Botanical Web UI**:
   - Sleek glassmorphism theme with dark slate and emerald accents.
   - Micro-animations, responsive layout, and autocomplete suggestions.
   - Copy-to-clipboard for clean emoji reports (Requirement 6) and plain text export.
   - Interactive ambiguity resolution buttons and sample image test hooks.

---

## 🏛️ Architecture

```text
User Input ("early blight tomato", "Apple Scab", "xyz disease")
                        │
                        ▼
          ┌───────────────────────────┐
          │  1. Input Validation      │ (backend/utils/validation.py)
          └─────────────┬─────────────┘
                        │
                        ▼
          ┌───────────────────────────┐
          │  2. Disease Normalization │ (backend/utils/normalization.py)
          └─────────────┬─────────────┘
                        │
                        ▼
          ┌───────────────────────────┐
          │  3. Retrieval & Matching  │ (backend/services/disease_search.py & knowledge_base.py)
          └──────┬─────────────┬──────┘
                 │             │
       [Ambiguous / Unknown]   [Verified Record]
                 │             │
                 ▼             ▼
       ┌───────────────────┐ ┌───────────────────────────┐
       │ Structured Clarif.│ │  4. LLM Grounded Reasoner │ (backend/services/llm_service.py)
       │ / Disambiguation  │ └─────────────┬─────────────┘
       └─────────┬─────────┘               │
                 │                         ▼
                 │           ┌───────────────────────────┐
                 │           │  5. Response Formatter    │ (Section 6 format & safety notice)
                 │           └─────────────┬─────────────┘
                 │                         │
                 └───────────┬─────────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │  Client Presentation  │ (FastAPI REST API & Botanical UI)
                 └───────────────────────┘
```

---

## 📁 Project Structure

```text
plant-disease-agent/
│
├── frontend/                     # Modern responsive web interface
│   ├── index.html                # Semantic HTML5 layout
│   ├── styles.css                # Premium botanical design system
│   └── app.js                    # Client interactivity & API handler
│
├── backend/
│   ├── main.py                   # FastAPI app entry point & static server
│   ├── api/
│   │   └── routes.py             # REST API endpoints (/api/disease, /api/diseases/suggest, etc.)
│   ├── agents/
│   │   └── disease_agent.py      # Orchestrator coordinating validation, search, and reasoning
│   ├── services/
│   │   ├── knowledge_base.py     # Verified pathology database (USDA, FAO, Cornell, UC Davis)
│   │   ├── disease_search.py     # Search, fuzzy matching & ambiguity resolution
│   │   └── llm_service.py        # Grounded LLM reasoning & response formatter
│   ├── models/
│   │   └── schemas.py            # Pydantic data schemas
│   └── utils/
│       ├── validation.py         # Input sanitization & safety checks
│       └── normalization.py      # Linguistic & canonical normalization engine
│
├── tests/
│   ├── test_agent.py             # Unit tests for validation, normalization & agent queries
│   └── test_api.py               # Integration tests for FastAPI endpoints
│
├── .env.example                  # Environment configuration template
├── pytest.ini                    # Pytest configuration
├── requirements.txt              # Python dependencies
└── README.md                     # Documentation
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Modern Web Browser

### 2. Setup Virtual Environment & Dependencies
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional)
```bash
cp .env.example .env
```
*Note: If `GEMINI_API_KEY` or `OPENAI_API_KEY` is not provided, the agent runs in **Deterministic Agricultural Expert Mode** with zero external network calls.*

### 4. Run the Application
```bash
.venv/bin/python3 backend/main.py
```
Open your browser at:
👉 **[http://localhost:8000](http://localhost:8000)**

---

## 📡 REST API Documentation

### 1. Query Disease
- **Endpoint**: `POST /api/disease`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
  ```json
  {
    "disease": "Tomato Early Blight"
  }
  ```
- **Response (Success - 200)**:
  ```json
  {
    "status": "success",
    "disease": "Early Blight",
    "plant": "Tomato",
    "type": "Fungal",
    "description": "Early blight is a common and destructive fungal disease...",
    "symptoms": [
      "Brown to dark brown circular spots with distinct concentric rings ('target board' pattern) on foliage",
      "Yellow chlorotic halos surrounding necrotic leaf spots"
    ],
    "cause": "Alternaria solani (and Alternaria linariae), necrotrophic ascomycete fungi.",
    "spread": "Spores (conidia) survive in infected plant residues...",
    "conditions": [
      "Warm temperatures ranging between 24°C to 29°C (75°F to 85°F)",
      "Prolonged leaf wetness and high relative humidity (>90%)"
    ],
    "affected_parts": ["Leaves (most prevalent)", "Stems", "Fruit"],
    "severity": "Moderate to High",
    "treatment": [
      "Prune and remove infected lower leaves promptly during dry weather",
      "Stake or cage tomato vines to keep foliage well above soil level"
    ],
    "prevention": [
      "Practice minimum 3-year crop rotation away from solanaceous species",
      "Plant certified disease-free seeds and resistant cultivars"
    ],
    "organic_management": [
      "Apply copper-based fungicides or sulfur according to OMRI guidelines",
      "Biofungicide sprays based on Bacillus subtilis"
    ],
    "chemical_management": [
      "Preventative broad-spectrum protectant fungicides: Chlorothalonil or Mancozeb",
      "Systemic fungicides: Azoxystrobin or Difenoconazole",
      "Rotate chemical fungicide FRAC groups to prevent pathogen resistance"
    ],
    "when_to_seek_help": "Contact your local agricultural extension service if defoliation exceeds 25% of canopy...",
    "sources": [
      "USDA Agricultural Research Service (ARS)",
      "University of California Statewide IPM Program (UC IPM)",
      "Cornell AgriLife Extension - Plant Disease Diagnostic Clinic",
      "FAO Crop Disease and Pest Management Manual"
    ],
    "disclaimer": "Note: This information is for educational purposes. For accurate diagnosis and pesticide recommendations, consult a local agricultural expert and always follow the product label.",
    "formatted_output": "🌱 Plant Disease Information\n\nDisease:\nEarly Blight\n..."
  }
  ```

- **Response (Ambiguous - 200)**:
  ```json
  {
    "status": "ambiguous",
    "query": "Early Blight",
    "matches": [
      "Tomato Early Blight",
      "Potato Early Blight"
    ],
    "message": "I found multiple possible matches:\n\n1. Tomato Early Blight\n2. Potato Early Blight\n\nPlease select the correct disease."
  }
  ```

- **Response (Unknown - 200)**:
  ```json
  {
    "status": "unknown",
    "query": "xyz disease",
    "message": "I couldn't confidently identify this plant disease.\n\nPlease provide:\n- Plant name\n- Disease name\n- Optional symptoms\n\nExample:\nTomato - Early Blight"
  }
  ```

---

## 🧪 Automated Testing

Run the comprehensive pytest suite covering normalization, validation, ambiguity handling, required test cases, and HTTP API routes:

```bash
.venv/bin/pytest -v
```

All 16 test cases verify:
- `Tomato Early Blight`
- `Tomato Late Blight`
- `Potato Late Blight`
- `Apple Scab`
- `Powdery Mildew`
- `Unknown Disease XYZ`
- Normalization: `early blight tomato`, `tomato early blight disease`, `Early-Blight`
- Ambiguity detection: `Late Blight` -> Tomato vs Potato
- Safety notice and source attribution inclusion

---

## 🔮 Future Image Classification Extension

The agent includes an image diagnostic endpoint (`POST /api/disease/diagnose-image`). To connect an external Vision Transformer (ViT) or Convolutional Neural Network (CNN):
1. Place your model weights in `backend/models/weights/`.
2. Update the inference adapter in `backend/api/routes.py` (`diagnose_image` function).
3. The adapter extracts predicted labels (e.g. `"Tomato Late Blight"`) and delegates directly to `PlantDiseaseAgent.run(predicted_disease)`.
