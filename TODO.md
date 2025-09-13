# TODO: Refactor Gemini Logic

## Steps:
1. Analyze all backend files for gemini usage
2. Rewrite backend/gemini_api.py with improved structure
3. Test backend functionality to ensure no disruption
4. Verify endpoints work correctly

## Completed:
- Analyzed backend/gemini_api.py, backend/app.py, backend/drug_logic.py, backend/models.py
- Rewritten backend/gemini_api.py with improved structure, logging, error handling, and separation of concerns

## New Task: Add logic to fetch alternatives and interactions using Gemini API

## Steps:
1. Add new function in backend/drug_logic.py: get_alternatives_and_interactions_via_gemini
2. Add new endpoint in backend/app.py: /get_drug_alternatives_interactions
3. Test the new functionality

## Completed:
- Added new function get_alternatives_and_interactions_via_gemini in backend/drug_logic.py
- Added new endpoint /get_drug_alternatives_interactions in backend/app.py
- Modified check_interactions to use Gemini API directly for interactions
- Modified suggest_alternatives to use Gemini API directly for alternatives
- Removed IBM Granite dependency from drug_logic.py
- Tested the new function with sample inputs (paracetamol and unknown drug)
