from fastapi import FastAPI
from pydantic import BaseModel
from .models import extract_drug_info
from .drug_logic import check_interactions, get_dosage, suggest_alternatives, get_alternatives_and_interactions_via_gemini
from .gemini_api import GeminiAPI

app = FastAPI(title="Drug Recognition API", version="1.0")

gemini_api = GeminiAPI()
if not gemini_api.api_key or not gemini_api.base_url:
    print("Warning: Gemini API key or endpoint not set. MediBot functionality may be limited.")

class ExtractRequest(BaseModel):
    text: str

class InteractionRequest(BaseModel):
    drugs: list[str]


class DosageRequest(BaseModel):
    drug: str
    age: int = 30

class ChildDosageRequest(BaseModel):
    drug: str
    age: int = 10
    weight: float = 30.0
@app.post("/get_child_dosage")
def get_child_dosage_endpoint(request: ChildDosageRequest):
    """
    Calculate dosage for children using IBM Granite model.
    """
    try:
        # --- IBM Granite API integration ---
        # Replace the following with actual IBM Granite API call
        # For now, simulate response
        dosage = f"Recommended child dosage for {request.drug}: {request.weight * 10} mg (simulated by IBM Granite)"
        return {"dosage": dosage}
    except Exception as e:
        print(f"Error in child dosage endpoint: {e}")
        return {"dosage": "Error calculating child dosage. Please consult a healthcare professional."}

class AlternativeRequest(BaseModel):
    drug: str
    age: int = 30
    
class ChatRequest(BaseModel):
    message: str
    context: str = ""  # Optional context from previous conversation

class BMIRequest(BaseModel):
    weight: float  # in kg
    height: float  # in cm
    age: int = 30
    gender: str = ""  # Optional

class DrugAlternativesInteractionsRequest(BaseModel):
    drug: str

@app.post("/extract")
def extract_endpoint(req: ExtractRequest):
    parsed = extract_drug_info(req.text, gemini_api)
    formatted_results = []
    for d in parsed:
        drug_info = {
            "name": d.get('name', ''),
            "dosage": d.get('dosage', ''),
            "frequency": d.get('frequency', '')
        }
        formatted_results.append(drug_info)
    plain_text = ""
    for i, drug in enumerate(formatted_results):
        if i > 0:
            plain_text += "\n\n"
        plain_text += f"Drug: {drug['name']}\n"
        plain_text += f"Dosage: {drug['dosage']}\n"
        plain_text += f"Frequency: {drug['frequency']}"
    return {
        "structured": formatted_results,
        "plain_text": plain_text
    }

@app.post("/check_interactions")
def check_interactions_endpoint(request: InteractionRequest):
    interactions = check_interactions(request.drugs, gemini_api)
    return {"interactions": interactions}

@app.post("/get_dosage")
def get_dosage_endpoint(request: DosageRequest):
    dosage = get_dosage(request.drug, request.age, gemini_api)
    return {"dosage": dosage}

@app.post("/suggest_alternatives")
def suggest_alternatives_endpoint(request: AlternativeRequest):
    alternatives = suggest_alternatives(request.drug, request.age, gemini_api)
    return {"alternatives": alternatives}

@app.post("/get_drug_alternatives_interactions")
def get_drug_alternatives_interactions_endpoint(request: DrugAlternativesInteractionsRequest):
    result = get_alternatives_and_interactions_via_gemini(request.drug, gemini_api)
    return result

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    """
    Process a chat message using the Gemini API and return a response
    focused on medical and pharmaceutical information.
    """
    prompt = f"""
You are MediBot, a helpful medical assistant chatbot. 
Provide accurate, helpful information about medications, health conditions, and general medical advice.

Always include appropriate disclaimers when providing medical information.
If you're unsure about something, acknowledge your limitations and suggest consulting a healthcare professional.

Previous context (if any):
{request.context}

User's question: {request.message}
"""

    try:
        # Use the GeminiAPI class method query to get a response
        text = gemini_api.query(prompt)
        if text:
            # Prevent echoing the user's input as a loop by checking for repeated input
            if text.strip() == request.message.strip():
                return {"response": "I'm sorry, I couldn't generate a new response. Please try rephrasing your question."}
            return {"response": text}
        else:
            return {"response": "I'm sorry, I couldn't generate a response. Please try again."}
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return {"response": "An error occurred while processing your request. Please try again."}

@app.post("/calculate_bmi")
def calculate_bmi_endpoint(request: BMIRequest):
    """
    Calculate BMI and provide health status information based on the result.
    """
    try:
        # Convert height from cm to meters
        height_m = request.height / 100
        
        # Calculate BMI: weight (kg) / height^2 (m)
        bmi = request.weight / (height_m * height_m)
        bmi = round(bmi, 1)  # Round to 1 decimal place
        
        # Determine BMI category
        category = ""
        if bmi < 18.5:
            category = "Underweight"
            color = "#3498db"  # Blue
            advice = "Consider consulting with a healthcare provider about healthy weight gain strategies."
        elif 18.5 <= bmi < 25:
            category = "Normal weight"
            color = "#2ecc71"  # Green
            advice = "Maintain your healthy lifestyle with balanced diet and regular exercise."
        elif 25 <= bmi < 30:
            category = "Overweight"
            color = "#f39c12"  # Orange
            advice = "Consider moderate changes to diet and increasing physical activity."
        else:
            category = "Obese"
            color = "#e74c3c"  # Red
            advice = "Consider consulting with a healthcare provider for personalized weight management strategies."
        
        # Add age-specific considerations
        age_advice = ""
        if request.age < 18:
            age_advice = "Note: BMI calculations for individuals under 18 should use age-specific charts. This is an approximate value."
        elif request.age > 65:
            age_advice = "Note: For older adults, slightly higher BMI values may be acceptable. Consult with your healthcare provider."
        
        return {
            "bmi": bmi,
            "category": category,
            "color": color,
            "advice": advice,
            "age_advice": age_advice,
            "disclaimer": "BMI is a screening tool and not a diagnostic of body fatness or health. Consult a healthcare provider for a complete health assessment."
        }
    except Exception as e:
        print(f"Error calculating BMI: {e}")
        return {"error": "An error occurred while calculating BMI. Please check your input values."}