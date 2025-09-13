import os
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class GeminiAPI:
    """
    Enhanced Gemini API wrapper for pharmaceutical information queries.

    This class provides a safe interface to the Gemini API with fallback behavior
    when API credentials are not available. It handles drug information queries
    and returns structured responses.
    """

    def __init__(self, api_key: Optional[str] = None, endpoint: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the Gemini API client.

        Args:
            api_key: Gemini API key. If None, uses GEMINI_API_KEY environment variable or hardcoded fallback.
            endpoint: API endpoint URL. If None, uses GEMINI_ENDPOINT or default.
            model: Model name. If None, uses GEMINI_MODEL or default 'gemini-2.0-flash'.
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or "AIzaSyBgl-L1XzFr62P4L_XYAn1qcSVPhOoV-ms"
        self.model = model or os.environ.get("GEMINI_MODEL") or "gemini-2.0-flash"
        self.base_url = endpoint or os.environ.get("GEMINI_ENDPOINT") or f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"

        if not self.api_key or not self.base_url:
            logger.warning("Gemini API key or endpoint not set. MediBot functionality may be limited. Please set GEMINI_API_KEY and GEMINI_ENDPOINT or GEMINI_MODEL in your environment.")

    def _build_prompt(self, drug_name: str) -> str:
        """
        Build the prompt for drug information queries.

        Args:
            drug_name: Name of the drug to query.

        Returns:
            Formatted prompt string.
        """
        return (
            f"Provide detailed pharmaceutical information for the drug '{drug_name}'."
            f"\n\nIf '{drug_name}' is not a recognized medication, please respond with 'UNKNOWN_MEDICATION' at the beginning of your response, "
            f"followed by your best guess about what this might be, if possible."
            f"\n\nFor recognized medications, include the following sections:\n"
            f"Name: (standard name)\n"
            f"Dosage: (typical dosage ranges for adults and children if applicable)\n"
            f"Frequency: (how often it should be taken)\n"
            f"Interactions: (list major drug interactions, separated by commas)\n"
            f"Alternatives: (list alternative medications, separated by commas)\n"
            f"\nFormat as plain text with clear section headers."
        )

    def _make_api_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        """
        Make the API request to Gemini.

        Args:
            prompt: The prompt to send to the API.

        Returns:
            Parsed JSON response from the API, or None if request fails.
        """
        if not self.api_key or not self.base_url:
            return None

        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        params = {"key": self.api_key}

        try:
            resp = requests.post(self.base_url, json=data, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.error(f"Gemini API error: {resp.status_code} {resp.text}")
                return None
        except Exception as e:
            logger.error(f"Error querying Gemini API: {e}")
            return None

    def _parse_response(self, response_json: Dict[str, Any], drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Parse the API response into structured drug information.

        Args:
            response_json: Raw JSON response from the API.
            drug_name: Original drug name queried.

        Returns:
            Structured drug information dictionary, or None if parsing fails.
        """
        try:
            text = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            if not text:
                return None

            # Check if the medication is unknown
            if text.strip().startswith("UNKNOWN_MEDICATION"):
                return {
                    "name": drug_name,
                    "dosage": "Unknown - not a recognized medication",
                    "frequency": "Unknown - consult a healthcare professional",
                    "interactions": [],
                    "alternatives": [],
                    "is_recognized": False
                }

            # Parse the text into structured dict for recognized medications
            result = {
                "name": drug_name,
                "dosage": "",
                "frequency": "",
                "interactions": [],
                "alternatives": [],
                "is_recognized": True
            }

            lines = text.split('\n')
            current_section = None
            section_content = ""

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for section headers
                if line.lower().startswith("name:"):
                    current_section = "name"
                    section_content = line.split(":", 1)[1].strip()
                    if section_content:
                        result["name"] = section_content
                elif line.lower().startswith("dosage:"):
                    current_section = "dosage"
                    section_content = line.split(":", 1)[1].strip()
                    if section_content:
                        result["dosage"] = section_content
                elif line.lower().startswith("frequency:"):
                    current_section = "frequency"
                    section_content = line.split(":", 1)[1].strip()
                    if section_content:
                        result["frequency"] = section_content
                elif line.lower().startswith("interactions:"):
                    current_section = "interactions"
                    section_content = line.split(":", 1)[1].strip()
                    if section_content:
                        result["interactions"] = [i.strip() for i in section_content.split(',') if i.strip()]
                elif line.lower().startswith("alternatives:"):
                    current_section = "alternatives"
                    section_content = line.split(":", 1)[1].strip()
                    if section_content:
                        result["alternatives"] = [a.strip() for a in section_content.split(',') if a.strip()]
                # Handle continuation lines for the current section
                elif current_section:
                    if current_section == "interactions":
                        additional_items = [i.strip() for i in line.split(',') if i.strip()]
                        result["interactions"].extend(additional_items)
                    elif current_section == "alternatives":
                        additional_items = [a.strip() for a in line.split(',') if a.strip()]
                        result["alternatives"].extend(additional_items)
                    elif current_section in ["dosage", "frequency"]:
                        if result[current_section]:
                            result[current_section] += " " + line
                        else:
                            result[current_section] = line

            return result

        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return None

    def query_drug(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Query the Gemini API for drug information.

        Args:
            drug_name: Name of the drug to query.

        Returns:
            Dict with drug information: {"name":..., "dosage":..., "frequency":..., "interactions":[...], "alternatives":[...], "is_recognized": bool}
            Returns None if API is not available or request fails.
        """
        if not self.api_key or not self.base_url:
            logger.warning("Gemini API not configured. Skipping query for drug: %s", drug_name)
            return None

        prompt = self._build_prompt(drug_name)
        response_json = self._make_api_request(prompt)

        if response_json:
            return self._parse_response(response_json, drug_name)

        return None

    def query(self, prompt: str) -> Optional[str]:
        """
        Make a general query to the Gemini API.

        Args:
            prompt: The prompt to send to the API.

        Returns:
            The text response from the API, or None if request fails.
        """
        if not self.api_key or not self.base_url:
            logger.warning("Gemini API not configured. Skipping general query.")
            return None

        response_json = self._make_api_request(prompt)
        if response_json:
            try:
                text = response_json.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                return text if text else None
            except Exception as e:
                logger.error(f"Error extracting text from Gemini response: {e}")
                return None
        return None
