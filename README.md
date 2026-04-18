cd # Douyatte

Douyatte is a phone-first web app for learning **how** to use Japanese words in realistic context.

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React + Vite + TypeScript
- LLM/TTS: Gemini (`gemini-3-flash-lite`, `gemini-3-flash-preview`, `gemini-3.1-flash-tts-preview`)

## Features (MVP)

- Input one Japanese word
- Low-cost validation first:
  - Japanese characters only
  - Single lexical word
  - Reject ambiguous hiragana-only forms that need kanji specificity
- Generate:
  - Word explanation section
  - Realistic dialogue scenarios (romaji + English hidden by default and toggleable)
  - Multi-speaker dialogue audio (Japanese lines)

## Setup

1. Copy env file and fill your API key:
   - `copy .env.example backend/.env`
2. Backend setup:
   - `cd backend`
   - `python -m venv .venv`
   - `.venv\\Scripts\\activate`
   - `pip install -e .`
3. Frontend setup:
   - `cd ../frontend`
   - `npm install`

## Run

1. Start backend:
   - `cd backend`
   - `.venv\\Scripts\\activate`
   - `uvicorn app.main:app --reload`
2. Start frontend:
   - `cd frontend`
   - `npm run dev`
3. Open:
   - `http://localhost:5173`

## Test

- Backend:
  - `cd backend`
  - `.venv\\Scripts\\activate`
  - `pytest`
- Frontend:
  - `cd frontend`
  - `npm test`
