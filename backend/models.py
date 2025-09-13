import re
from typing import List, Dict



DOSAGE_RE = re.compile(r'(\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|units))', re.IGNORECASE)
# Frequency includes patterns like '14 days', 'before breakfast', etc.
FREQ_RE = re.compile(r'(once(?:\s+daily)?|twice(?:\s+daily)?|three times(?:\s+daily)?|tds|bd|qds|daily|weekly|monthly|before breakfast|after meals|for \d+ days|for \d+ weeks|for \d+ months|\d+ days|\d+ weeks|\d+ months)', re.IGNORECASE)
DRUG_RE = re.compile(r'\b([A-Z][a-zA-Z0-9\-]{2,})\b')
SYMPTOM_RE = re.compile(r'([A-Z][a-z]+(?: [a-z]+){0,3})(?:\.|:|,| -)', re.IGNORECASE)

def extract_drug_info(text: str, gemini=None) -> List[Dict]:
    """
    Best-effort extractor:
    - Finds candidate drug names (capitalized tokens)
    - Finds dosages and frequencies nearby
    - If drug not in local heuristics, queries Gemini as fallback
    Returns list of dicts: {name, dosage, frequency}
    """
    # Improved sentence-based parsing with symptom extraction
    text = text.replace('\n', ' ')
    sentences = re.split(r'(?<=[.!?])\s+', text)
    results = []
    symptom = ""
    # Try to extract symptom from first sentence
    if sentences:
        match = SYMPTOM_RE.match(sentences[0])
        if match:
            symptom = match.group(1).strip()
    for sent in sentences:
        drugs = [m.group(1) for m in DRUG_RE.finditer(sent) if m.group(1).lower() not in ('the','and','for','with','prescribe','mild','infection','daily','days')]
        for drug in drugs:
            dosage = None
            freq = None
            # Find dosage near drug name
            pattern = re.compile(re.escape(drug) + r'.{0,40}?' + DOSAGE_RE.pattern, re.IGNORECASE)
            m = pattern.search(sent)
            if m:
                dosage = m.group(1)
            else:
                # fallback: any dosage in sentence
                m2 = DOSAGE_RE.search(sent)
                if m2:
                    dosage = m2.group(1)
            # Find frequency near drug name (including duration)
            freq_pat = re.compile(re.escape(drug) + r'.{0,40}?' + FREQ_RE.pattern, re.IGNORECASE)
            fm = freq_pat.search(sent)
            if fm:
                freq = fm.group(1)
            else:
                fm2 = FREQ_RE.search(sent)
                if fm2:
                    freq = fm2.group(1)
            # fallback to Gemini for missing info
            if gemini and not (dosage or freq):
                gem = gemini.query_drug(drug)
                if gem and isinstance(gem, dict):
                    dosage = dosage or gem.get("dosage")
                    freq = freq or gem.get("frequency")
            results.append({"name": drug, "dosage": dosage or "", "frequency": freq or "", "symptom": symptom})
    # if nothing found, try full-text Gemini parse
    if gemini and not results:
        gem = gemini.query_drug(text[:60])
        if gem and isinstance(gem, dict):
            return [{"name": gem.get("name",""), "dosage": gem.get("dosage",""), "frequency": gem.get("frequency",""), "symptom": symptom}]
    return results