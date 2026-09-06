import re
from typing import Dict, List, Optional, Tuple

KNOWN_PLANTS = [
    "tomato", "potato", "apple", "rice", "wheat", "corn", "maize",
    "grape", "grapevine", "cucumber", "citrus", "orange", "lemon",
    "banana", "coffee", "soybean", "cotton", "pepper", "chili",
    "strawberry", "onion", "garlic", "cabbage", "rose"
]

COMMON_DISEASE_TERMS = [
    "early blight", "late blight", "scab", "powdery mildew", "downy mildew",
    "leaf spot", "bacterial wilt", "rice blast", "blast", "fusarium wilt",
    "canker", "citrus canker", "black rot", "anthracnose", "mosaic virus",
    "yellow leaf curl", "rust", "damping off", "root rot", "bacterial spot",
    "verticillium wilt", "gray mold", "botrytis", "fire blight"
]

# Aliases and colloquial terms to canonical mapping
DISEASE_SYNONYMS: Dict[str, str] = {
    "early-blight": "early blight",
    "late-blight": "late blight",
    "leafspot": "leaf spot",
    "leaf-spot": "leaf spot",
    "apple-scab": "apple scab",
    "powdery-mildew": "powdery mildew",
    "downy-mildew": "downy mildew",
    "bacterial-wilt": "bacterial wilt",
    "rice-blast": "rice blast",
    "citrus-canker": "citrus canker",
    "black-rot": "black rot",
    "fire-blight": "fire blight",
}

STOP_WORDS = {
    "disease", "infection", "fungus", "bacteria", "virus",
    "problem", "issue", "in", "on", "of", "the", "a", "an", "plant", "plants"
}

def normalize_disease_name(raw_text: str) -> Tuple[str, Optional[str], Optional[str]]:
    """
    Normalizes messy user input into clean standard terminology.
    Returns:
        (canonical_query: str, detected_plant: Optional[str], detected_disease: Optional[str])
    """
    # 1. Clean punctuation & lowercase
    text = raw_text.strip().lower()
    
    # Replace hyphens and underscores with spaces
    text = re.sub(r"[-_]+", " ", text)
    
    # Remove special punctuation
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # 2. Check synonyms directly
    for syn, canonical in DISEASE_SYNONYMS.items():
        syn_clean = syn.replace("-", " ")
        if syn_clean in text:
            text = text.replace(syn_clean, canonical)

    # 3. Detect known plants
    detected_plant: Optional[str] = None
    for plant in KNOWN_PLANTS:
        # Match whole word
        pattern = r"\b" + re.escape(plant) + r"\b"
        if re.search(pattern, text):
            detected_plant = plant.capitalize()
            # Normalize grapevine/citrus synonyms
            if plant == "grapevine":
                detected_plant = "Grape"
            elif plant in ["orange", "lemon"]:
                detected_plant = "Citrus"
            elif plant == "maize":
                detected_plant = "Corn"
            break

    # 4. Remove plant word and stop words to extract pure disease keywords
    tokens = text.split()
    remaining_tokens = []
    for token in tokens:
        if detected_plant and token == detected_plant.lower():
            continue
        if token in STOP_WORDS:
            continue
        remaining_tokens.append(token)

    pure_disease_str = " ".join(remaining_tokens).strip()

    # 5. Check if pure disease matches common disease terms
    detected_disease: Optional[str] = None
    for dt in COMMON_DISEASE_TERMS:
        if dt in pure_disease_str or dt == pure_disease_str:
            detected_disease = dt.title()
            break
        # Also check in the whole text if not found in filtered tokens
        if dt in text:
            detected_disease = dt.title()

    # If not recognized in common terms but tokens remain, title case the remaining tokens
    if not detected_disease and pure_disease_str:
        detected_disease = pure_disease_str.title()

    # 6. Assemble canonical query
    if detected_plant and detected_disease:
        # Avoid duplicate plant name if detected_disease already contains plant
        if detected_plant.lower() in detected_disease.lower():
            canonical_query = detected_disease
        else:
            canonical_query = f"{detected_plant} {detected_disease}"
    elif detected_disease:
        canonical_query = detected_disease
    elif detected_plant:
        canonical_query = detected_plant
    else:
        canonical_query = raw_text.strip().title()

    return canonical_query, detected_plant, detected_disease
