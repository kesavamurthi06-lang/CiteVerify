import os
import json
import time

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

client = genai.Client(api_key=API_KEY)


def extract_claims(document_text):

    prompt = f"""
You are an expert scientific research analyst.

Extract meaningful scientific claims from the
following research document.

For each claim identify:

1. Claim ID
2. Original claim
3. Simplified claim
4. Associated citation
5. Claim category
6. Numerical values
7. Relevant context

Rules:

- Extract only claims present in the document.
- Never invent citations.
- Preserve numerical values.
- If citation is absent, return null.
- Do not treat every sentence as a scientific claim.

Return valid JSON:

{{
    "claims": [
        {{
            "claim_id": 1,
            "original_claim": "Claim text",
            "simplified_claim": "Simple explanation",
            "citation": null,
            "category": "Scientific Finding",
            "numerical_values": [],
            "context": "Relevant context"
        }}
    ]
}}

Document:

{document_text[:30000]}
"""

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            result = json.loads(response.text)

            if "claims" not in result:
                raise ValueError("Invalid AI response format.")

            return result

        except Exception as error:

            error_message = str(error)

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{error_message}"
            )

            if attempt == 2:
                raise RuntimeError(
                    "AI service is temporarily unavailable. "
                    "Please try again later."
                )

            time.sleep(2 ** attempt)

    return {"claims": []}