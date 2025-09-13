import os
from backend.gemini_api import GeminiAPI

# Set the API key for testing (replace with your actual key)
os.environ["GEMINI_API_KEY"] = "AIzaSyDgEGDbhyOk_xTYwex2p_UtP9Mz5cWHLdY"

def test_gemini_api():
    gemini = GeminiAPI()

    # Test with a known drug
    result = gemini.query_drug("paracetamol")
    print("Test 1 - Paracetamol:")
    print(result)
    print()

    # Test with an unknown drug
    result = gemini.query_drug("unknown_drug_xyz")
    print("Test 2 - Unknown drug:")
    print(result)
    print()

    # Test with prescription text
    result = gemini.query_drug("Paracetamol 500 mg twice daily")
    print("Test 3 - Prescription text:")
    print(result)
    print()

if __name__ == "__main__":
    test_gemini_api()
