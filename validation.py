import re
from typing import Tuple, Optional

# Minimal character length for a plausible disease query
MIN_QUERY_LENGTH = 2
MAX_QUERY_LENGTH = 150

# Regex patterns for basic sanitization
DISALLOWED_PATTERN = re.compile(r"[<>{}\\]")

def validate_disease_input(raw_input: Optional[str]) -> Tuple[bool, str, Optional[str]]:
    """
    Validates and performs preliminary sanitization on raw user input.
    Returns:
        (is_valid: bool, sanitized_input: str, error_message: Optional[str])
    """
    if raw_input is None:
        return False, "", "Please enter a plant disease name."

    # Strip leading/trailing whitespace
    cleaned = raw_input.strip()

    if not cleaned:
        return False, "", "Disease name cannot be empty. Please enter a valid plant disease."

    if len(cleaned) < MIN_QUERY_LENGTH:
        return False, cleaned, "The entered query is too short. Please provide a more descriptive disease name."

    if len(cleaned) > MAX_QUERY_LENGTH:
        return False, cleaned[:MAX_QUERY_LENGTH], f"Query exceeds maximum length of {MAX_QUERY_LENGTH} characters."

    # Check for script or injection tags
    if DISALLOWED_PATTERN.search(cleaned):
        cleaned = DISALLOWED_PATTERN.sub("", cleaned).strip()
        if not cleaned:
            return False, "", "Input contained invalid special characters."

    # Check if query is only numbers or only punctuation
    alphanumeric_chars = [c for c in cleaned if c.isalnum()]
    if not alphanumeric_chars:
        return False, cleaned, "Please enter a readable disease name containing letters."

    return True, cleaned, None
