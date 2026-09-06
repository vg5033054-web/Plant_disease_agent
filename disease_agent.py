import logging
from typing import Optional, List
from backend.models.schemas import DiseaseResponse, DiseaseInfo
from backend.utils.validation import validate_disease_input
from backend.utils.normalization import normalize_disease_name
from backend.services.disease_search import DiseaseSearchService
from backend.services.llm_service import LLMService

logger = logging.getLogger(__name__)

UNKNOWN_MESSAGE = """I couldn't confidently identify this plant disease.

Please provide:
- Plant name
- Disease name
- Optional symptoms

Example:
Tomato - Early Blight"""

class PlantDiseaseAgent:
    """
    Modular orchestrator agent for plant disease identification and guidance.
    Architecture:
    Input Validation -> Normalization -> Retrieval -> Ambiguity/Unknown Evaluation -> LLM Reasoning -> Formatting
    """
    def __init__(
        self,
        search_service: Optional[DiseaseSearchService] = None,
        llm_service: Optional[LLMService] = None
    ):
        self.search_service = search_service or DiseaseSearchService()
        self.llm_service = llm_service or LLMService()

    async def run(self, raw_input: str) -> DiseaseResponse:
        logger.info(f"Processing query: {raw_input}")

        # Step 1: Input Validation
        is_valid, sanitized_text, val_error = validate_disease_input(raw_input)
        if not is_valid:
            return DiseaseResponse(
                status="error",
                query=raw_input or "",
                message=val_error or "Invalid input.",
                formatted_output=f"❌ Error: {val_error}"
            )

        # Step 2: Disease Name Normalization
        canonical_query, detected_plant, detected_disease = normalize_disease_name(sanitized_text)
        logger.info(f"Normalized query: '{sanitized_text}' -> '{canonical_query}' (Plant: {detected_plant}, Disease: {detected_disease})")

        # Step 3: Disease Information Retrieval & Ambiguity/Unknown Check
        record, matches, search_status = self.search_service.search(
            raw_query=sanitized_text,
            detected_plant=detected_plant,
            detected_disease=detected_disease
        )

        # Step 4: Handle Ambiguous matches (e.g. "Early Blight", "Late Blight")
        if search_status == "ambiguous" and matches:
            formatted_matches = "\n".join([f"{i+1}. {m}" for i, m in enumerate(matches)])
            ambiguous_msg = f"I found multiple possible matches:\n\n{formatted_matches}\n\nPlease select the correct disease."
            return DiseaseResponse(
                status="ambiguous",
                query=raw_input,
                normalized_query=canonical_query,
                matches=matches,
                message=ambiguous_msg,
                formatted_output=ambiguous_msg
            )

        # Step 5: Handle Unknown Diseases (e.g. "xyz disease", unrecognized names)
        if search_status == "unknown" or (not record and not matches):
            return DiseaseResponse(
                status="unknown",
                query=raw_input,
                normalized_query=canonical_query,
                message=UNKNOWN_MESSAGE,
                formatted_output=UNKNOWN_MESSAGE
            )

        # Step 6: LLM Reasoning & Processing with Agricultural Grounding
        try:
            disease_info: Optional[DiseaseInfo] = await self.llm_service.process_disease_reasoning(
                query=canonical_query,
                retrieved_record=record
            )
        except Exception as e:
            logger.error(f"Error during LLM processing: {e}")
            disease_info = None

        if not disease_info:
            unverified_msg = "I could not verify reliable information for this disease name. Please provide the plant name or a more specific disease name."
            return DiseaseResponse(
                status="unknown",
                query=raw_input,
                normalized_query=canonical_query,
                message=unverified_msg,
                formatted_output=unverified_msg
            )

        # Step 7: Response Delivery
        return DiseaseResponse(
            status="success",
            query=raw_input,
            normalized_query=canonical_query,
            data=disease_info,
            formatted_output=disease_info.formatted_text
        )
