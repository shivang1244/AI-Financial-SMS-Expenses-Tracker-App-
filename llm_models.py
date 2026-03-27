import torch
from transformers import pipeline
from huggingface_hub import login

import requests

OPENROUTER_API_KEY = "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"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}


def call_gpt(messages, temperature=0):
    """
    Generic GPT caller (no prompt logic here)
    """

    body = {
        "model": "openai/gpt-4o-mini",
        "messages": messages,
        "temperature": temperature
    }

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=OPENROUTER_HEADERS,
            json=body
        )

        data = response.json()
        usage = data.get("usage", {})
        print(" TOKEN USAGE:", usage)
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        print(" GPT API ERROR:", e)
        return None