# AI Chatbot that answers customer questions and captures leads automatically

![status](https://img.shields.io/badge/status-demo-blue) ![python](https://img.shields.io/badge/python-3.10%2B-blue) ![fastapi](https://img.shields.io/badge/backend-FastAPI-009688)

![demo screenshot placeholder](screenshots/demo.png)
*(Screenshot: replace with a real capture of the widget open + a lead form showing, once you've run it once.)*

**Live demo:** _add your deployed link here once hosted_

## The business problem

Small businesses lose customers because they can't reply to every website visitor's question fast enough — and by the time someone finally gets a reply, they've often already gone to a competitor. This bot answers common questions instantly, and the moment someone shows buying or booking intent, it captures their name and contact so a human can follow up.

## Architecture

```
chatbot-lead-capture/
├── backend/
│   ├── config/
│   │   └── prompts.py       # Business knowledge base + system prompt, isolated from logic
│   ├── core/
│   │   ├── llm.py           # LLM call + offline fallback logic
│   │   └── leads.py         # Lead storage (swap for a real DB in production)
│   ├── main.py               # FastAPI route definitions only
│   ├── .env.example          # Copy to .env — never commit real keys
│   └── requirements.txt
├── frontend/
│   └── index.html            # Standalone chat widget, no build step
└── README.md
```

**Stack:** `Python` · `FastAPI` · `OpenAI API` · `HTML/CSS/JS` (vanilla, zero build step)

## Key features

- Answers customer FAQs instantly, 24/7, in the business's own voice
- Detects buying/booking intent from natural conversation, not a rigid keyword menu
- Automatically surfaces a lead-capture form at the right moment in the conversation
- Runs with zero API key for demo purposes (rule-based fallback), or with a real OpenAI key for natural LLM responses
- Config and prompts fully isolated from application logic — updating the business's FAQ or tone never requires touching route code

## Security

- API keys are never hardcoded or committed — loaded from environment variables via `.env` (gitignored) locally, or your host's secret manager in production
- CORS is wide open (`*`) for local demo purposes only — restrict `allow_origins` to the real frontend domain before going live with a client
- The in-memory lead store is for demo purposes; production use should point `core/leads.py` at a real database with proper access controls

## How to run it locally

**Backend:**
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # add your OPENAI_API_KEY, or leave blank for offline fallback mode
uvicorn main:app --reload --port 8000
```

**Frontend:**
Open `frontend/index.html` directly in a browser. It talks to the backend at `http://localhost:8000` by default — change `API_BASE` at the top of the `<script>` block once deployed.

## Deployment

- **Backend:** any Python host works — Render, Railway, or Fly.io are the simplest for a FastAPI app. Set `OPENAI_API_KEY` as an environment variable in the host's dashboard, not in code.
- **Frontend:** static hosting — Vercel, Netlify, or GitHub Pages. Update `API_BASE` in `index.html` to your deployed backend URL before publishing.

## What I'd improve next

- Swap the in-memory lead store for a real database (Postgres/Supabase) before production use
- Add WhatsApp Business API delivery as a channel alongside the web widget
- Add per-client config loading (JSON/YAML) instead of hardcoding `config/prompts.py`, so onboarding a new client doesn't require a code change

## Contact

[Your LinkedIn] · [Your portfolio link]
