import requests

from config import GROQ_API_KEY


def generate_answer(question, context):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    context_text = "\n\n".join(context)

    prompt = f"""
You are a helpful RAG chatbot.

Use the following context to answer the user's question.

Context:
{context_text}

Question:
{question}

Instructions:
- Answer using the provided context.
- If the answer is not present in the context, say that you could not find the answer in the knowledge base.
- Do not invent information.
- Keep the answer clear and concise.

Answer:
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