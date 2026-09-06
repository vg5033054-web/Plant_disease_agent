from typing import List, Optional, Literal
from pydantic import BaseModel, Field

DiseaseType = Literal[
    "Fungal",
    "Bacterial",
    "Viral",
    "Nematode",
    "Abiotic",
    "Other"
]

SeverityLevel = Literal[
    "Low",
    "Moderate",
    "High",
    "Low to Moderate",
    "Moderate to High",
    "Very High"
]

class DiseaseRequest(BaseModel):
    disease: str = Field(..., min_length=1, max_length=200, description="Plant disease name or query")

class DiseaseInfo(BaseModel):
    disease: str = Field(..., description="Standardized name of the disease")
    plant: str = Field(..., description="Common host plant name")
    type: DiseaseType = Field(..., description="Pathogen category")
    description: str = Field(..., description="Overview and biological context")
    symptoms: List[str] = Field(default_factory=list, description="Observable physical symptoms")
    cause: str = Field(..., description="Causal organism/pathogen species")
    spread: str = Field(..., description="Vectors and transmission mechanisms")
    conditions: List[str] = Field(default_factory=list, description="Favorable environmental conditions")
    affected_parts: List[str] = Field(default_factory=list, description="Foliage, stem, fruit, root, etc.")
    severity: str = Field(..., description="Disease severity level")
    treatment: List[str] = Field(default_factory=list, description="Active interventions and cultural controls")
    prevention: List[str] = Field(default_factory=list, description="Preventative agronomic measures")
    organic_management: List[str] = Field(default_factory=list, description="Biological and organic options")
    chemical_management: List[str] = Field(default_factory=list, description="Chemical options with safety warnings")
    when_to_seek_help: str = Field(..., description="Criteria for consulting local extension agents")
    sources: List[str] = Field(default_factory=list, description="Authoritative agricultural sources")
    disclaimer: str = Field(
        default="Note: This information is for educational purposes. For accurate diagnosis and pesticide recommendations, consult a local agricultural expert and always follow the product label.",
        description="Agricultural and pesticide safety disclaimer"
    )
    formatted_text: Optional[str] = Field(default=None, description="Pre-formatted clean markdown representation")

class DiseaseResponse(BaseModel):
    status: Literal["success", "ambiguous", "unknown", "error"]
    query: str
    normalized_query: Optional[str] = None
    data: Optional[DiseaseInfo] = None
    matches: Optional[List[str]] = None
    message: Optional[str] = None
    formatted_output: Optional[str] = None

class AutocompleteSuggestion(BaseModel):
    name: str
    plant: str
    type: str

class ImageDiagnoseResponse(BaseModel):
    status: Literal["success", "error"]
    predicted_disease: str
    confidence: float
    message: str
    disease_details: Optional[DiseaseResponse] = None
