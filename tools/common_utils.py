import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MAX_LLM_PROMPT_CHARS = 18_000


def truncate_text(text: str, max_chars: int, label: str = "text") -> str:
    if len(text) <= max_chars:
        return text

    marker = f"\n\n[TRUNCATED {label}: removed {len(text) - max_chars:,} chars]\n\n"
    if len(marker) >= max_chars:
        return text[:max_chars]
    keep = max(max_chars - len(marker), 0)
    head = keep // 2
    tail = keep - head
    return f"{text[:head]}{marker}{text[-tail:] if tail else ''}"


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY not found. Copy .env.example to .env and add your Groq key.")
    return Groq(api_key=api_key)


def call_llm(
    prompt: str,
    system: str = "",
    model: str = "llama-3.3-70b-versatile",
    max_prompt_chars: int = MAX_LLM_PROMPT_CHARS,
) -> str:
    client = get_groq_client()
    prompt = truncate_text(prompt, max_prompt_chars, "prompt")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2048,
    )
    return response.choices[0].message.content
