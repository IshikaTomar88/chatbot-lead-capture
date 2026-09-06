"""
core/llm.py
LLM call logic and the offline fallback, isolated from the API route layer
in main.py. This is what you'd unit-test independently of FastAPI.
"""
import os
import re
from typing import List

from config.prompts import BUSINESS, LEAD_TRIGGER_WORDS, build_system_prompt


def is_lead_intent(text: str) -> bool:
    lower = text.lower()
    return any(word in lower for word in LEAD_TRIGGER_WORDS)


def fallback_answer(user_message: str) -> str:
    """Rule-based fallback used when no OPENAI_API_KEY is configured, so the
    demo runs end-to-end with zero external dependencies."""
    lower = user_message.lower()
    for item in BUSINESS["faq"]:
        keywords = [w for w in re.findall(r"[a-z]+", item["q"].lower()) if len(w) > 3]
        if any(w in lower for w in keywords):
            return item["a"]
    if is_lead_intent(user_message):
        return BUSINESS["pricing_note"]
    return "I'm not fully sure about that — I can have the team follow up. Could you leave your contact info?"


def call_llm(user_message: str, history: List[dict]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return fallback_answer(user_message)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        messages = [{"role": "system", "content": build_system_prompt()}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": user_message})
        response = client.chat.completions.create(
            model="gpt-4o-mini", messages=messages, max_tokens=150, temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return fallback_answer(user_message)
