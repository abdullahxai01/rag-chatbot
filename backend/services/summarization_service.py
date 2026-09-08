import requests

from config import GROQ_API_KEY


def summarize_text(text: str):

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    chunks = split_text(text)

    summaries = []

    for chunk in chunks:

        prompt = f"""
You are a document summarization assistant.

Summarize the following section of a document.

Include:
- Main ideas
- Important facts
- Important numbers
- Key decisions or conclusions
- Important names, dates, or terms

Do not invent information.

Document section:
{chunk}

Summary:
"""

        data = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2
        }

        response = requests.post(
            url,
            headers=headers,
            json=data
        )

        if not response.ok:
            print("GROQ STATUS:", response.status_code)
            print("GROQ RESPONSE:", response.text)

        response.raise_for_status()

        result = response.json()

        summary = result["choices"][0]["message"]["content"]

        summaries.append(summary)

    return combine_summaries(summaries)


def split_text(text, chunk_size=5000):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def combine_summaries(summaries):

    combined = "\n\n".join(summaries)

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
You are a professional document summarization assistant.

Below are summaries of different sections of the same document.

Create one complete, coherent summary of the entire document.

Your summary should contain:

1. Document overview
2. Main topics
3. Important points
4. Important facts, numbers, and dates
5. Key conclusions

Do not invent information.

Section summaries:

{combined}

Complete document summary:
"""

    data = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    response = requests.post(
        url,
        headers=headers,
        json=data
    )

    if not response.ok:
        print("GROQ STATUS:", response.status_code)
        print("GROQ RESPONSE:", response.text)

    response.raise_for_status()

    result = response.json()

    return result["choices"][0]["message"]["content"]