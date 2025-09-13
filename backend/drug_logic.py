from typing import List, Dict, Optional
import re

# Comprehensive drug database with dosage, alternatives, interactions, and uses
_drug_db = {
    "paracetamol": {
        "dosage": {"adult": "500-1000 mg q6-8h (max 4 g/day)", "child": "10-15 mg/kg q6-8h"},
        "alternatives": ["ibuprofen", "aspirin"],
        "interactions": ["alcohol", "warfarin"],
        "uses": ["fever", "mild-moderate pain", "headache"]
    },
    "ibuprofen": {
        "dosage": {"adult": "200-400 mg q6-8h (max 3.2 g/day)", "child": "5-10 mg/kg q6-8h"},
        "alternatives": ["naproxen", "diclofenac", "aspirin"],
        "interactions": ["warfarin", "aspirin", "corticosteroids"],
        "uses": ["pain", "inflammation", "arthritis", "fever"]
    },
    "aspirin": {
        "dosage": {"adult": "75-325 mg/day (cardiac), up to 4 g/day (pain)"},
        "alternatives": ["clopidogrel", "ibuprofen", "naproxen"],
        "interactions": ["warfarin", "ssris"],
        "uses": ["pain", "fever", "heart attack prevention", "stroke prevention"]
    },
    "amoxicillin": {
        "dosage": {"adult": "500 mg q8h or 875 mg q12h", "child": "25-50 mg/kg/day"},
        "alternatives": ["ampicillin", "cephalexin", "azithromycin"],
        "interactions": ["methotrexate", "warfarin"],
        "uses": ["bacterial infections", "respiratory infections", "urinary infections", "skin infections"]
    },
    "azithromycin": {
        "dosage": {"adult": "500 mg day 1, then 250 mg x4 days"},
        "alternatives": ["clarithromycin", "doxycycline"],
        "interactions": ["statins", "qt-prolonging drugs"],
        "uses": ["respiratory infections", "skin infections", "sexually transmitted infections"]
    },
    "ciprofloxacin": {
        "dosage": {"adult": "250-750 mg q12h"},
        "alternatives": ["levofloxacin", "ofloxacin"],
        "interactions": ["antacids", "warfarin"],
        "uses": ["urinary tract infections", "respiratory infections", "gastrointestinal infections"]
    },
    "metformin": {
        "dosage": {"adult": "500-1000 mg BID (max 2.5 g/day)"},
        "alternatives": ["sitagliptin", "pioglitazone"],
        "interactions": ["alcohol", "iodinated contrast agents"],
        "uses": ["type 2 diabetes", "insulin resistance"]
    },
    "insulin": {
        "dosage": {"adult": "0.2-1.0 units/kg/day"},
        "alternatives": ["insulin lispro", "insulin glargine"],
        "interactions": ["beta-blockers", "alcohol"],
        "uses": ["type 1 diabetes", "type 2 diabetes"]
    },
    "glibenclamide": {
        "dosage": {"adult": "2.5-5 mg OD (max 20 mg/day)"},
        "alternatives": ["glimepiride", "gliclazide"],
        "interactions": ["alcohol", "beta-blockers"],
        "uses": ["type 2 diabetes", "blood sugar control"]
    },
    "losartan": {
        "dosage": {"adult": "50 mg OD (25-100 mg/day)"},
        "alternatives": ["valsartan", "telmisartan"],
        "interactions": ["potassium supplements", "nsaids"],
        "uses": ["hypertension", "heart failure", "kidney protection"]
    },
    "amlodipine": {
        "dosage": {"adult": "5-10 mg OD"},
        "alternatives": ["nifedipine", "diltiazem"],
        "interactions": ["grapefruit juice", "simvastatin"],
        "uses": ["hypertension", "angina"]
    },
    "lisinopril": {
        "dosage": {"adult": "10-40 mg OD"},
        "alternatives": ["enalapril", "ramipril"],
        "interactions": ["potassium supplements", "nsaids", "lithium"],
        "uses": ["hypertension", "heart failure", "kidney disease"]
    },
    "atorvastatin": {
        "dosage": {"adult": "10-80 mg OD"},
        "alternatives": ["rosuvastatin", "simvastatin"],
        "interactions": ["grapefruit juice", "macrolides"],
        "uses": ["high cholesterol", "heart disease prevention"]
    },
    "simvastatin": {
        "dosage": {"adult": "10-40 mg OD (evening)"},
        "alternatives": ["pravastatin", "rosuvastatin"],
        "interactions": ["grapefruit juice", "clarithromycin"],
        "uses": ["high cholesterol"]
    },
    "omeprazole": {
        "dosage": {"adult": "20-40 mg OD"},
        "alternatives": ["pantoprazole", "esomeprazole"],
        "interactions": ["clopidogrel", "warfarin"],
        "uses": ["gerd", "stomach ulcers", "acidity"]
    },
    "pantoprazole": {
        "dosage": {"adult": "40 mg OD"},
        "alternatives": ["omeprazole", "rabeprazole"],
        "interactions": ["methotrexate", "warfarin"],
        "uses": ["gerd", "acidity", "ulcers"]
    },
    "ranitidine": {
        "dosage": {"adult": "150 mg BID"},
        "alternatives": ["famotidine", "nizatidine"],
        "interactions": ["warfarin", "alcohol"],
        "uses": ["acidity", "heartburn"]
    },
    "furosemide": {
        "dosage": {"adult": "20-80 mg/day"},
        "alternatives": ["bumetanide", "torsemide"],
        "interactions": ["digoxin", "aminoglycosides"],
        "uses": ["edema", "hypertension", "heart failure"]
    },
    "spironolactone": {
        "dosage": {"adult": "25-100 mg/day"},
        "alternatives": ["eplerenone", "amiloride"],
        "interactions": ["ace inhibitors", "arbs"],
        "uses": ["heart failure", "hypertension", "pcos", "acne"]
    },
    "hydrochlorothiazide": {
        "dosage": {"adult": "12.5-50 mg OD"},
        "alternatives": ["chlorthalidone", "indapamide"],
        "interactions": ["lithium", "nsaids"],
        "uses": ["hypertension", "edema"]
    },
    "salbutamol": {
        "dosage": {"adult": "inhaler: 100-200 mcg q4-6h PRN"},
        "alternatives": ["terbutaline", "formoterol"],
        "interactions": ["beta-blockers", "maois"],
        "uses": ["asthma", "copd", "shortness of breath"]
    },
    "prednisone": {
        "dosage": {"adult": "5-60 mg/day (variable)"},
        "alternatives": ["dexamethasone", "methylprednisolone"],
        "interactions": ["nsaids", "vaccines"],
        "uses": ["inflammation", "asthma", "autoimmune diseases"]
    },
    "levothyroxine": {
        "dosage": {"adult": "25-200 mcg OD"},
        "alternatives": ["liothyronine"],
        "interactions": ["iron supplements", "calcium supplements", "warfarin"],
        "uses": ["hypothyroidism"]
    },
    "warfarin": {
        "dosage": {"adult": "2-10 mg OD (INR-guided)"},
        "alternatives": ["apixaban", "rivaroxaban"],
        "interactions": ["antibiotics", "nsaids", "vitamin k foods"],
        "uses": ["prevents blood clots", "dvt prevention", "stroke prevention", "atrial fibrillation"]
    },
    "heparin": {
        "dosage": {"adult": "5000 units SC q8-12h"},
        "alternatives": ["enoxaparin", "fondaparinux"],
        "interactions": ["nsaids", "antiplatelets"],
        "uses": ["prevents blood clots", "treats blood clots"]
    },
    "apixaban": {
        "dosage": {"adult": "5 mg BID"},
        "alternatives": ["rivaroxaban", "dabigatran"],
        "interactions": ["rifampicin", "nsaids"],
        "uses": ["stroke prevention", "dvt prevention", "pulmonary embolism prevention"]
    },
    "clopidogrel": {
        "dosage": {"adult": "75 mg OD"},
        "alternatives": ["prasugrel", "ticagrelor"],
        "interactions": ["omeprazole", "nsaids"],
        "uses": ["prevents stroke", "prevents heart attack", "blood thinner"]
    },
    "metoprolol": {
        "dosage": {"adult": "25-100 mg BID"},
        "alternatives": ["atenolol", "bisoprolol"],
        "interactions": ["verapamil", "insulin"],
        "uses": ["hypertension", "angina", "arrhythmia"]
    },
    "sertraline": {
        "dosage": {"adult": "50-200 mg OD"},
        "alternatives": ["fluoxetine", "escitalopram"],
        "interactions": ["maois", "nsaids"],
        "uses": ["depression", "anxiety", "ocd"]
    },
    "fluoxetine": {
        "dosage": {"adult": "20-60 mg OD"},
        "alternatives": ["sertraline", "paroxetine"],
        "interactions": ["triptans", "warfarin", "maois"],
        "uses": ["depression", "panic disorder"]
    },
    "diazepam": {
        "dosage": {"adult": "2-10 mg 2-4x daily"},
        "alternatives": ["lorazepam", "alprazolam"],
        "interactions": ["alcohol", "opioids"],
        "uses": ["anxiety", "muscle spasms", "seizures"]
    },
    "morphine": {
        "dosage": {"adult": "10-30 mg q4h (oral)"},
        "alternatives": ["oxycodone", "fentanyl"],
        "interactions": ["alcohol", "benzodiazepines", "maois"],
        "uses": ["severe pain", "post-surgery pain"]
    },
    "codeine": {
        "dosage": {"adult": "15-60 mg q4-6h (max 360 mg/day)"},
        "alternatives": ["tramadol", "morphine"],
        "interactions": ["alcohol", "antihistamines"],
        "uses": ["mild-moderate pain", "cough"]
    },
    "tramadol": {
        "dosage": {"adult": "50-100 mg q4-6h (max 400 mg/day)"},
        "alternatives": ["codeine", "tapentadol"],
        "interactions": ["ssris", "alcohol"],
        "uses": ["moderate-severe pain"]
    },
    "cetirizine": {
        "dosage": {"adult": "10 mg OD"},
        "alternatives": ["loratadine", "fexofenadine"],
        "interactions": ["alcohol", "cns depressants"],
        "uses": ["allergies", "hay fever", "runny nose"]
    }
}



def normalize_name(name: str) -> str:
    return re.sub(r'[^a-z0-9]', '', name.lower())

def check_interactions(drugs: List[str], gemini=None) -> Dict[str, List[str]]:
    """
    Return a dict mapping each drug to a list of potential interactions with the other provided drugs.
    Uses Gemini API directly for fetching interactions.
    """
    normalized = [normalize_name(d) for d in drugs]
    original_drugs = {normalize_name(d): d for d in drugs}  # Keep original drug names for better output
    interactions = {}
    unrecognized_drugs = []

    for d in normalized:
        interactions[d] = []
        if gemini:
            res = gemini.query_drug(original_drugs.get(d, d))
            if res and isinstance(res, dict):
                if res.get("is_recognized") is False:
                    unrecognized_drugs.append(original_drugs.get(d, d))
                    interactions[d] = [f"'{original_drugs.get(d, d)}' is not a recognized medication"]
                    continue
                if res.get("interactions"):
                    for other in normalized:
                        if other == d:
                            continue
                        for inter in res["interactions"]:
                            if inter and normalize_name(inter) in other:
                                interactions[d].append(original_drugs.get(other, other))
                    if not interactions[d] and res["interactions"]:
                        interactions[d] = [f"May interact with: {', '.join(res['interactions'][:5])}"]
                        if len(res['interactions']) > 5:
                            interactions[d][0] += " and others"
            else:
                interactions[d] = ["Unable to fetch interaction data from Gemini API"]
        else:
            interactions[d] = ["Gemini API not available for interaction check"]

    # Add note for unrecognized drugs or no interactions
    for d in normalized:
        if not interactions[d]:
            interactions[d] = ["No known interactions with the provided drugs"]

    return interactions

def get_dosage(drug: str, age: Optional[int]=30, gemini=None) -> str:
    d = normalize_name(drug)
    info = _drug_db.get(d)
    if info:
        if age and age < 18 and "child" in info["dosage"]:
            return info["dosage"]["child"]
        return info["dosage"].get("adult", next(iter(info["dosage"].values())))
    else:
        if gemini:
            res = gemini.query_drug(d)
            if res:
                if isinstance(res, dict) and res.get("is_recognized") is False:
                    return f"'{drug}' is not a recognized medication. Please consult a healthcare professional."
                if isinstance(res, dict) and res.get("dosage"):
                    if age and age < 18 and "child" in res["dosage"].lower():
                        child_dosage_match = re.search(r'child(?:ren)?[:\s]+(.*?)(?:\.|$|;|\n)', res["dosage"], re.IGNORECASE)
                        if child_dosage_match:
                            return child_dosage_match.group(1).strip()
                    return res["dosage"]
                if res.get("raw_text"):
                    return res["raw_text"]
            return "Dosage information not found; consult a healthcare professional."
        return "Dosage information not found; consult a healthcare professional."

def suggest_alternatives(drug: str, age: Optional[int]=30, gemini=None) -> List[str]:
    """
    Suggest alternatives for a drug using Gemini API directly.
    """
    if gemini:
        res = gemini.query_drug(drug)
        if res and isinstance(res, dict):
            if res.get("is_recognized") is False:
                return [f"'{drug}' is not a recognized medication. Please consult a healthcare professional."]
            alternatives = res.get("alternatives", [])
            if alternatives:
                return alternatives
            else:
                return ["No specific alternatives found. Please consult a healthcare professional."]
        return ["Unable to fetch alternatives from Gemini API. Please consult a healthcare professional."]
    return ["Gemini API not available. Please consult a healthcare professional for alternatives."]
def get_alternatives_and_interactions_via_gemini(drug: str, gemini=None) -> Dict[str, List[str]]:
    """
    Fetch alternatives and interactions for a specific drug using Gemini API directly.

    Args:
        drug: Name of the drug to query.
        gemini: GeminiAPI instance.

    Returns:
        Dict with 'alternatives' and 'interactions' lists.
        If Gemini is not available or drug not recognized, returns empty lists with message.
    """
    if not gemini:
        return {
            "alternatives": ["Gemini API not available. Please consult a healthcare professional."],
            "interactions": ["Gemini API not available. Please consult a healthcare professional."]
        }

    res = gemini.query_drug(drug)
    if res and isinstance(res, dict):
        if res.get("is_recognized") is False:
            message = f"'{drug}' is not a recognized medication. Please consult a healthcare professional."
            return {
                "alternatives": [message],
                "interactions": [message]
            }
        alternatives = res.get("alternatives", [])
        interactions = res.get("interactions", [])
        return {
            "alternatives": alternatives if alternatives else ["No specific alternatives found. Please consult a healthcare professional."],
            "interactions": interactions if interactions else ["No specific interactions found. Please consult a healthcare professional."]
        }
    else:
        return {
            "alternatives": ["Unable to fetch data from Gemini API. Please consult a healthcare professional."],
            "interactions": ["Unable to fetch data from Gemini API. Please consult a healthcare professional."]
        }
