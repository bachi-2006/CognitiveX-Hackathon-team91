# Drug Recognition - Enhanced

This project contains a **Streamlit** frontend and **FastAPI** backend to parse prescriptions and provide dosage, interactions, and alternative suggestions. It includes a simple fallback integration scaffold for calling a Gemini-like API.

## Structure
```
backend/         # FastAPI backend
frontend/        # Streamlit frontend (app.py)
react-frontend/  # Placeholder react landing page (optional)
requirements.txt
package.json
```

## Requirements
- Python 3.9+
- Node.js (for React if needed)
- Install Python deps:
```bash
python -m venv venv
source venv/bin/activate   # mac/linux
venv\Scripts\activate      # windows
pip install -r requirements.txt
```

## Environment
Set `GEMINI_API_KEY` if you want the app to use the Gemini API fallback:
```bash
export GEMINI_API_KEY="your_api_key_here"
export BACKEND_URL="http://localhost:8000"
```

## Run backend
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Run frontend (Streamlit)
In project root:
```bash
streamlit run frontend/app.py
```

## React landing page
A basic placeholder exists in `react-frontend/`. You can replace or enhance it; the Streamlit app is the main functional UI.

## Notes / Design decisions
- The Gemini API wrapper is a **placeholder**: update `backend/gemini_api.py` with the correct endpoint and request format for the Gemini API you plan to use.
- The extractor uses a best-effort regex-based approach and falls back to Gemini when possible.
- This repo intentionally avoids shipping large models. If you want to run IBM Granite locally, update `models.py` to load it and ensure you have sufficient hardware.

## Disclaimer
This tool is **informational only** and **not medical advice**. Always consult a licensed healthcare provider before acting on any medication guidance.

## Additional files
- `.env.example` — sample environment variables
- `docker-compose.yml` & `Dockerfile` — run backend + streamlit via docker-compose
- `react-frontend/` — simple static landing page that calls the backend

## Running with Docker
```bash
# build and run
docker-compose up --build
```

## Gemini / Failsafe
The app will attempt to use the Gemini API (or any OpenAI Responses-compatible endpoint) if `GEMINI_API_KEY` is set. The Gemini wrapper is conservative and will not crash the app if the key or endpoint is missing.

## Important
- **This tool is informational only. Always consult a qualified healthcare professional before acting on medication data.**
