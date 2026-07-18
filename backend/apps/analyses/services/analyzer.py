from .prompts import IDEA_VALIDATION_PROMPT
from .llm_client import call_llm


def analyze_idea(idea_text):
    return call_llm(
        prompt=IDEA_VALIDATION_PROMPT,
        idea_text=idea_text
    )