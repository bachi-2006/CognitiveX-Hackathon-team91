import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional, Dict

class GraniteAPI:
    """
    Local Granite model wrapper for drug information.
    Loads the IBM Granite model locally.
    """
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or "ibm-granite/granite-3.3-2b-instruct"
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            print("✅ Granite model and tokenizer loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load Granite model: {e}")
            self.model = None

    def query_drug(self, drug_name: str) -> Optional[Dict]:
        """
        Query the Granite model for drug information.
        Returns a dict like: {"name":..., "dosage":..., "frequency":..., "interactions":[...], "alternatives":[...]}
        If model not loaded, returns None.
        """
        if not self.model or not self.tokenizer:
            print("Warning: Granite model not loaded. MediBot functionality may be limited.")
            return None
        try:
            # Enhanced prompt with more specific instructions for better results
            prompt = (
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

            inputs = self.tokenizer(prompt, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=512, temperature=0.7)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Parse the response
            result = {"name": drug_name, "is_recognized": True}
            lines = response.split('\n')
            current_section = None
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.lower().startswith("unknown_medication"):
                    result["is_recognized"] = False
                    result["raw_text"] = response
                    return result
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
            print(f"Error querying Granite: {e}")
            return None

    def query(self, message: str) -> Optional[str]:
        """
        General query method for chat-like responses.
        """
        if not self.model or not self.tokenizer:
            return None
        try:
            inputs = self.tokenizer(message, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model.generate(**inputs, max_new_tokens=256, temperature=0.7)
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
        except Exception as e:
            print(f"Error in Granite query: {e}")
            return None
