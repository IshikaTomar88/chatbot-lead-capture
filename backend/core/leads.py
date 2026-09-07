"""
core/leads.py
Lead storage, isolated so it can be swapped for a real database (Postgres/
Supabase) later without touching main.py's route definitions.
"""
from datetime import datetime
from typing import List

LEADS: List[dict] = []


def save_lead(name: str, contact: str, interest: str) -> dict:
    lead = {
        "name": name,
        "contact": contact,
        "interest": interest or "General inquiry",
        "captured_at": datetime.utcnow().isoformat(),
    }
    LEADS.append(lead)
    return lead


def get_leads() -> List[dict]:
    return LEADS
