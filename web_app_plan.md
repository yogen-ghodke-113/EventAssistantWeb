# Investor Event Assistant Web App - Development Plan

## App Overview

A web application to assist during investor events by providing comprehensive information about investment companies through fuzzy search, detailed company profiles, and real-time news integration using Google Generative AI (Gemini) via Python SDK.

---

## Architecture Overview

- **Language**: Python (Backend), JavaScript/TypeScript (Frontend)
- **Backend Framework**: FastAPI (preferred for async, modern Python APIs)
- **Frontend Framework**: React (with Material UI for design)
- **AI Integration**: Google Generative AI Python SDK
- **Data Sources**: Local CSV (Yogen.csv) + Gemini API
- **Key Libraries**:
  - FastAPI (API server)
  - Uvicorn (ASGI server)
  - Pandas (CSV parsing)
  - RapidFuzz (fuzzy search)
  - Google Generative AI SDK (Python)
  - Requests/HTTPX (for web requests)
  - React (frontend)
  - Material UI (frontend styling)
  - Axios (frontend API calls)

---

## Gemini Prompts (Example)

### Company Information Prompts

- **About the Company**
  ```
  Provide a concise overview about the company "{company_name}". Focus on its history, mission, and unique characteristics. Limit to 3-4 sentences.
  ```
- **What They Do**
  ```
  Summarize what "{company_name}" does, including its main investment focus, sectors, and any notable strategies. Limit to 3-4 sentences.
  ```
- **Major Investments**
  ```
  List the major investments or portfolio companies of "{company_name}". Provide up to 5 key examples with a short description for each.
  ```

### News Articles Prompt

- **Recent News**
  ```
  Provide a list of the 3 most recent news articles about "{company_name}". For each, include:
  - Title
  - Source
  - Date
  - Short summary
  - URL (if available)
  Respond in JSON format.
  ```

---

## CSV Data Loading and Usage

### Loading

- The CSV file (`Yogen.csv`) is placed in the backend's `data/` directory.
- On FastAPI startup, the CSV is loaded into a Pandas DataFrame.
- The DataFrame is cached in memory for fast access (singleton pattern or as a dependency-injected service).
- Each row is mapped to an `Investor` Pydantic model for API responses.

### Usage

- **Fuzzy Search**: On search requests, the backend uses RapidFuzz to compare the query against relevant fields (e.g., name, aliases) in the DataFrame, returning the best matches.
- **Details Lookup**: When an investor is selected, their full row is retrieved from the DataFrame and returned as structured JSON.
- **AI Integration**: For Gemini prompts, the backend can use CSV data (e.g., company name, sector, AUM) to enrich the prompt or provide context.
- **Performance**: The DataFrame is only reloaded if the CSV changes (optional: implement file watcher or reload endpoint for admin).
- **Extensibility**: Additional fields or computed properties (e.g., investment counts) can be added to the model or calculated on the fly.

### Example Data Access Pattern

```python
# Load CSV on startup
import pandas as pd
investors_df = pd.read_csv('data/Yogen.csv')

# Fuzzy search
from rapidfuzz import process
results = process.extract(query, investors_df['Name'], limit=5)

# Get details
def get_investor_by_id(investor_id):
    row = investors_df.loc[investors_df['ID'] == investor_id].iloc[0]
    return row.to_dict()
```

---

## Phase 1: Project Setup & Basic Structure

### Tasks:

1. **Backend Setup**

   - Initialize Python project (venv, requirements.txt/pyproject.toml)
   - Install FastAPI, Uvicorn, Pandas, RapidFuzz, Google Generative AI SDK
   - Set up FastAPI app structure (routers, models, services)
   - Add CORS middleware for frontend integration

2. **Frontend Setup**

   - Initialize React project (Vite/CRA/Next.js)
   - Install Material UI, Axios
   - Set up basic folder structure (components, pages, services)

3. **Version Control**
   - Initialize Git repository
   - Add .gitignore for Python, Node, and environment files

---

## Phase 2: Data Layer Implementation (Backend)

### Tasks:

1. **CSV Data Model**

   - Define `Investor` Pydantic model (all CSV fields)
   - Implement CSV loader using Pandas
   - Create service to load and cache investor data from Yogen.csv

2. **Fuzzy Search Implementation**

   - Integrate RapidFuzz for fuzzy string matching
   - Implement search endpoint for partial/inexact matches
   - Test search with examples (e.g., "Brydon" → "The Brydon Group")

3. **Gemini API Integration**
   - Set up Gemini API key management (use .env for secrets)
   - Create Gemini service for company info and news prompts
   - Implement error handling and logging for API calls

---

## Phase 3: API Layer & Endpoints

### Tasks:

1. **Investor Search API**

   - `/api/investors/search?q=...` (returns fuzzy-matched investors)

2. **Investor Details API**

   - `/api/investors/{id}` (returns full profile from CSV)

3. **Company Info (AI) API**

   - `/api/investors/{id}/ai-info` (returns Gemini-generated info: About, What they do, Major Investments)

4. **News Articles (AI) API**

   - `/api/investors/{id}/news` (returns Gemini-generated news articles)

5. **API Documentation**
   - Add OpenAPI docs via FastAPI

---

## Phase 4: Frontend Implementation - Search & Details UI

### Tasks:

1. **Search Screen**

   - Create search bar with real-time suggestions (calls backend search API)
   - Display dropdown with fuzzy-matched results
   - Add "Investor Details" button for each result
   - Style with Material UI

2. **Details Screen**
   - Tabbed interface: Company Information, News
   - Fetch and display CSV data (key metrics, profile)
   - Fetch and display Gemini-generated content (About, What they do, Major Investments)
   - Fetch and display Gemini-generated news articles
   - Implement loading and error states

---

## Phase 5: AI Prompt Engineering & Integration

### Tasks:

1. **Company Information Prompts**

   - Design prompts for: About the Company, What they do, Major Investments
   - Implement backend logic to call Gemini API with these prompts

2. **News Articles Prompt**

   - Implement news prompt template
   - Parse and structure Gemini response
   - Validate and sanitize links

3. **API Error Handling**
   - Add retries and fallbacks for Gemini API failures
   - Implement offline/empty state handling

---

## Phase 6: Polish & Enhancement

### Tasks:

1. **UI/UX Improvements**

   - Add animations and transitions (React/MUI)
   - Implement proper loading, error, and empty states
   - Responsive design for desktop/tablet/mobile

2. **Performance Optimization**

   - Backend: cache Gemini responses, optimize CSV loading
   - Frontend: memoize API calls, lazy load components
   - Add pagination for large datasets

3. **Link Preview Implementation**
   - Research and implement link preview (Open Graph scraping or 3rd party API)
   - Display metadata for news links

---

## Phase 7: Testing & Final Polish

### Tasks:

1. **Testing**

   - Backend: unit tests (pytest), integration tests (FastAPI TestClient)
   - Frontend: component tests (Jest/React Testing Library), E2E tests (Cypress/Playwright)
   - Test search, API, and navigation flows

2. **Final Polish**
   - Add favicon, branding, and meta tags
   - Accessibility improvements (ARIA, keyboard navigation)
   - Performance testing (Lighthouse, load tests)
   - Deployment scripts (Docker, CI/CD)

---

## Technical Requirements

### Backend Dependencies (requirements.txt):

```
fastapi
uvicorn
pandas
python-dotenv
rapidfuzz
google-generativeai
httpx
```

### Frontend Dependencies (package.json):

```
react
@mui/material
axios
vite (or create-react-app/next)
```

---

## File Structure (Suggested)

```
backend/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── services/
│   │   ├── csv_loader.py
│   │   ├── fuzzy_search.py
│   │   └── gemini_service.py
│   ├── routers/
│   │   ├── investors.py
│   │   └── ai.py
│   └── utils.py
├── data/
│   └── Yogen.csv
├── tests/
│   └── ...
├── requirements.txt
└── .env
frontend/
├── src/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── App.jsx
├── public/
├── package.json
└── ...
```

---

## Data Display Order (Details Screen):

1. **Header Section**
   - Investor Name
   - Primary Investor Type
   - HQ Location & Country
2. **Key Metrics**
   - AUM (Assets Under Management)
   - PE Category
   - Investments | Active Portfolio | Exits
   - Investments in last 12 months
   - Dry Powder
3. **AI-Generated Content**
   - About the Company
   - What they do
   - Major Investments

---

## Estimated Timeline

- **Phase 1-2**: 2-3 days
- **Phase 3-4**: 3-4 days
- **Phase 5**: 2-3 days
- **Phase 6-7**: 2-3 days
- **Total**: 9-13 days

---

## API Key Setup

- Store Gemini API key in `.env` (backend)
- Never expose API key to frontend
- Use environment variables for config
- Implement proper key management for production

---

This plan provides a structured, actionable approach to building the Investor Event Assistant as a modern web app using Python, FastAPI, React, and the Google Generative AI SDK. All features from the Android app are mapped to the web context, with clear phase-wise tasks for efficient development.
