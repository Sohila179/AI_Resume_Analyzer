from huggingface_hub import InferenceClient
from config import Settings

settings = Settings()

client = InferenceClient(
    provider="together",
    api_key=settings.HF_TOKEN
)


def analyze_resume(text: str) -> dict:

    prompt = f"""
You are a professional resume analyzer.

Analyze the resume below and return ONLY valid JSON.

The JSON must have exactly these fields:

{{
    "skills": "List the candidate's important skills",
    "experience": "Summarize the candidate's work experience",
    "education": "Summarize the candidate's education",
    "summary": "Give a short professional summary"
}}

Resume:
{text}
"""

    response = client.chat.completions.create(
        model=settings.HF_MODEL.split(":")[0],
        messages=[
            {
                "role": "system",
                "content": "You are an expert resume analyzer. Return only valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=1000
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response")

    import json

    return json.loads(content)