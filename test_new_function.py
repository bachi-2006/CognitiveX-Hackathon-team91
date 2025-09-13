from backend.drug_logic import get_alternatives_and_interactions_via_gemini
from backend.gemini_api import GeminiAPI
import os

# Set API key if needed
os.environ["GEMINI_API_KEY"] = "AIzaSyDgEGDbhyOk_xTYwex2p_UtP9Mz5cWHLdY"

def test_new_function():
    gemini = GeminiAPI()

    # Test with paracetamol
    result = get_alternatives_and_interactions_via_gemini("paracetamol", gemini)
    print("Test - Paracetamol:")
    print(result)
    print()

    # Test with unknown drug
    result = get_alternatives_and_interactions_via_gemini("unknown_drug_xyz", gemini)
    print("Test - Unknown drug:")
    print(result)
    print()

if __name__ == "__main__":
    test_new_function()
