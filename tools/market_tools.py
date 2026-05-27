import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from tools.common_utils import truncate_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

MAX_COMPOUND_INPUT_CHARS = 6_000


def get_comparable_companies(startup_idea: str, sector: str) -> str:
    """
    Use Groq's compound model with web search to find comparable companies
    and financial benchmarks.
    """
    print("Searching for real comparable companies...")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY not found. Copy .env.example to .env and add your key.")

    client = Groq(api_key=api_key)
    startup_idea = truncate_text(startup_idea, MAX_COMPOUND_INPUT_CHARS, "startup idea")
    sector = truncate_text(sector, 500, "sector")

    response = client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Find 2-3 real startup companies similar to this idea: "{startup_idea}"

Focus on the {sector} sector, primarily in India but also Southeast Asia/Africa if relevant.

For each company provide:
1. Company name
2. Founded year
3. Total funding raised in INR or USD
4. Annual revenue, most recent available
5. Break-even status, profitable or not, and when
6. Key costs they faced early on
7. Source/link

Be specific with numbers. If exact numbers are not available, say so clearly. Do not fabricate.
Only report what you can verify from real sources.""",
            }
        ],
        search_settings={
            "country": "india",
            "exclude_domains": ["wikipedia.org"],
        },
    )

    return response.choices[0].message.content


def get_financial_benchmarks(startup_context: str, sector_hint: str) -> str:
    """
    Use Groq Compound web search to identify the closest industry and gather
    public or clearly estimated financial benchmark data for projections.
    """
    print("Searching for financial benchmark data...")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("GROQ_API_KEY not found. Copy .env.example to .env and add your key.")

    client = Groq(api_key=api_key)
    startup_context = truncate_text(startup_context, MAX_COMPOUND_INPUT_CHARS, "startup context")
    sector_hint = truncate_text(sector_hint, 500, "sector hint")

    response = client.chat.completions.create(
        model="groq/compound-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Use web search to research financial benchmarks for this startup context:
"{startup_context}"

Sector hint from the existing market report: "{sector_hint}"

First infer the most relevant industry or related industry from current web results.
Then find public finance data and benchmark ranges that would help a startup financial analyst.

Return a concise markdown report with these sections:
1. Related industry identified
2. Comparable companies or public operators
3. Available public financial data
   - funding raised
   - revenue or GMV
   - gross margin / take rate / commission rate when relevant
   - customer acquisition, operating, staff, inventory, logistics, software, rent, or capex costs
   - profitability or break-even status
4. Estimated benchmark ranges
   - clearly label estimates as ESTIMATE
   - explain what public facts the estimate is based on
5. Missing or unavailable data
6. Source links

Rules:
- Do not fabricate exact numbers.
- If a number is not publicly available, say "not publicly available".
- If you provide a range, label it as an estimate and explain the reasoning.
- Prefer India data, then Southeast Asia or Africa, then global analogs if needed.
- Focus on data useful for 5-year financial projections.""",
            }
        ],
        search_settings={
            "country": "india",
            "exclude_domains": ["wikipedia.org"],
        },
    )

    return response.choices[0].message.content
