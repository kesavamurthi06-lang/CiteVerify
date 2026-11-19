import os
import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

client = genai.Client(api_key=API_KEY)


def verify_claim(claim, evidence):
    """
    Compare one scientific claim against retrieved evidence.
    """

    if not evidence:
        return {
            "verdict": "INCONCLUSIVE",
            "explanation": "No relevant research evidence was available.",
            "evidence_used": [],
            "limitations": ["No evidence was retrieved."]
        }

    evidence_text = ""

    for index, item in enumerate(evidence, start=1):
        evidence_text += f"""
Evidence {index}
Source: {item.get("source", "Unknown")}
Title: {item.get("title", "Unknown")}
URL: {item.get("url", "Not available")}
Evidence type: {item.get("evidence_type", "Unknown")}
Text:
{item.get("text", "")}
"""

    prompt = f"""
You are a careful scientific evidence evaluator.

Your task is to evaluate whether the scientific claim is supported
by the supplied research evidence.

SCIENTIFIC CLAIM:
{claim}

RESEARCH EVIDENCE:
{evidence_text}

IMPORTANT RULES:

1. Use ONLY the supplied evidence.
2. Never invent experimental results, quotations, or citations.
3. Do not assume that a paper supports a claim just because its title
   or abstract contains similar words.
4. Distinguish correlation from causation.
5. Check numerical values, populations, conditions, and context.
6. If the evidence is insufficient, use INCONCLUSIVE.
7. If evidence supports only part of the claim, use PARTIALLY_SUPPORTED.
8. Use CONTRADICTORY only when evidence directly conflicts with the claim.
9. Do not treat absence of evidence as proof that a claim is false.
10. Do not treat an abstract as equivalent to full-text evidence.

Return ONLY valid JSON in this format:

{{
    "verdict": "SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | CONTRADICTORY | INCONCLUSIVE",
    "explanation": "Clear explanation of the result",
    "evidence_used": [
        {{
            "source_title": "Research paper title",
            "source_url": "URL",
            "excerpt": "Exact supporting or contradicting text from supplied evidence",
            "relationship": "SUPPORTS | CONTRADICTS | PARTIALLY_SUPPORTS"
        }}
    ],
    "limitations": [
        "Limitations of the available evidence"
    ]
}}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "response_mime_type": "application/json"
        }
    )

    try:
        result = json.loads(response.text)

        allowed_verdicts = {
            "SUPPORTED",
            "PARTIALLY_SUPPORTED",
            "UNSUPPORTED",
            "CONTRADICTORY",
            "INCONCLUSIVE"
        }

        if result.get("verdict") not in allowed_verdicts:
            raise ValueError("Invalid verdict returned by AI.")

        return result

    except (json.JSONDecodeError, TypeError, ValueError):
        return {
            "verdict": "INCONCLUSIVE",
            "explanation": "The AI returned an invalid verification response.",
            "evidence_used": [],
            "limitations": ["The verification response could not be parsed."]
        }