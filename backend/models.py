import re
from typing import List, Dict


DOSAGE_RE = re.compile(r'(\d+(?:\.\d+)?\s?(?:mg|mcg|g|ml|units))', re.IGNORECASE)
FREQ_RE = re.compile(r'\b(once(?:\s+daily)?|twice(?:\s+daily)?|three times(?:\s+daily)?|tds|bd|qds|daily|weekly|monthly)\b', re.IGNORECASE)
DRUG_RE = re.compile(r'\b([A-Z][a-zA-Z0-9\-]{2,})\b')

def extract_drug_info(text: str, gemini=None) -> List[Dict]:
    """
    Best-effort extractor:
    - Finds candidate drug names (capitalized tokens)
    - Finds dosages and frequencies nearby
    - If drug not in local heuristics, queries Gemini as fallback
    Returns list of dicts: {name, dosage, frequency}
    """
    text = text.replace('\n', ' ')
    candidates = set()
    for m in DRUG_RE.finditer(text):
        token = m.group(1)
        # simple filter: ignore common words and non-drug terms
        if token.lower() in ('the','and','for','with','prescribe','mild','infection','daily','days'):
            continue
        candidates.add(token)
    results = []
    for cand in candidates:
        name = cand
        pattern = re.compile(re.escape(cand) + r'.{0,80}?' + DOSAGE_RE.pattern, re.IGNORECASE)
        m = pattern.search(text)
        dosage = None
        if m:
            dosage = m.group(1)
        else:
            m2 = DOSAGE_RE.search(text)
            if m2:
                dosage = m2.group(1)
        f = None
        fm = FREQ_RE.search(text)
        if fm:
            f = fm.group(1)
        # fallback to Gemini for missing info
        if gemini and not (dosage or f):
            gem = gemini.query_drug(name)
            if gem and isinstance(gem, dict):
                dosage = dosage or gem.get("dosage")
                f = f or gem.get("frequency")
        results.append({"name": name, "dosage": dosage or "", "frequency": f or ""})
    # if nothing found, try full-text Gemini parse
    if gemini and not results:
        gem = gemini.query_drug(text[:60])
        if gem and isinstance(gem, dict):
            return [{"name": gem.get("name",""), "dosage": gem.get("dosage",""), "frequency": gem.get("frequency","")}]
    return results