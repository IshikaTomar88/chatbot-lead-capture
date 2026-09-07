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


GREETINGS = {"hi", "hello", "hey", "hii", "helo", "hola", "good morning", "good afternoon", "good evening"}


def is_greeting(text: str) -> bool:
    stripped = text.strip().lower().rstrip("!.")
    return stripped in GREETINGS


# Generic question words that appear across almost any message and would
# cause false matches if treated as meaningful keywords — this caused a real
# bug: "what" alone matched every question to the first FAQ item containing
# it ("What are your hours?"), so literally every question returned the same
# hours answer, confirmed by live testing.
STOPWORDS = {
    "what", "when", "where", "which", "does", "that", "this", "with", "from",
    "have", "about", "would", "could", "should", "there", "their", "your",
    "name", "clinic",
}


def fallback_answer(user_message: str) -> str:
    """Rule-based fallback used when no OPENAI_API_KEY is configured, so the
    demo runs end-to-end with zero external dependencies."""
    if is_greeting(user_message):
        return f"Hi! I'm the assistant for {BUSINESS['name']}. Ask me about our hours, services, pricing, or booking — happy to help."

    lower_words = set(re.findall(r"[a-z]+", user_message.lower()))
    best_item = None
    best_score = 0
    for item in BUSINESS["faq"]:
        keywords = [
            w for w in re.findall(r"[a-z]+", item["q"].lower())
            if len(w) > 3 and w not in STOPWORDS
        ]
        score = sum(1 for w in keywords if w in lower_words)
        if score > best_score:
            best_score = score
            best_item = item
    # Require at least 1 real, specific keyword hit (post-stopword-filtering) —
    # generic words are already excluded above, so any remaining match is a
    # genuine topic word like "hours", "pricing", "insurance", etc.
    if best_item and best_score >= 1:
        return best_item["a"]

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
