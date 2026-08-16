from huggingface_hub import InferenceClient
from config import Settings
import json

settings = Settings()

client = InferenceClient(
    provider="together",
    api_key=settings.HF_API_TOKEN
)


def analyze_resume(text: str) -> dict:
    prompt = f"""
Analyze this resume and return ONLY valid JSON.

Required JSON format:

{{
    "skills": ["Python", "FastAPI", "SQL"],
    "experience": "Short summary of work and project experience",
    "education": "Short summary of education",
    "summary": "Short professional summary"
}}

Rules:
- skills MUST be an array of strings.
- experience MUST be a string.
- education MUST be a string.
- summary MUST be a string.
- Return ONLY JSON.
- Do NOT use markdown.
- Do NOT use ```json.
- Do NOT add any explanation.

Resume:
{text}
"""

    response = client.chat.completions.create(
        model=settings.HF_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a professional resume analyzer. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=1000
    )

    # Debug: نشوف الـ response الحقيقي من AI
    print("========== AI RESPONSE ==========")
    print(response)
    print("=================================")

    if not response.choices:
        raise ValueError("AI returned no choices")

    message = response.choices[0].message

    if not message:
        raise ValueError("AI returned no message")

    content = message.content

    print("========== AI CONTENT ==========")
    print(repr(content))
    print("================================")

    if not content or not content.strip():
        raise ValueError("AI returned an empty response")

    content = content.strip()

    # لو الموديل رجع ```json ... ```
    if content.startswith("```"):
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

    try:
        analysis = json.loads(content)
    except json.JSONDecodeError as e:
        print("AI returned invalid JSON:")
        print(content)
        raise ValueError(f"AI returned invalid JSON: {e}")

    required_fields = {
        "skills",
        "experience",
        "education",
        "summary"
    }

    if set(analysis.keys()) != required_fields:
        raise ValueError(
            f"AI response has invalid fields. Got: {list(analysis.keys())}"
        )

    if not isinstance(analysis["skills"], list):
        raise ValueError("AI returned skills as something other than a list")

    if not all(isinstance(skill, str) for skill in analysis["skills"]):
        raise ValueError("Every skill must be a string")

    return analysis