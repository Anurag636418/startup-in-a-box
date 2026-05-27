import json

from tools.common_utils import call_llm


def run_pitch_creator(market_report: str, product_spec: str, financials: dict) -> str:
    print("Pitch Creator is building the deck...")

    finance_summary = json.dumps(
        {
            "assumptions": financials.get("assumptions", {}),
            "projections": financials.get("projections", []),
            "upfront_investment_inr": financials.get("upfront_investment_inr"),
            "break_even_year": financials.get("break_even_year"),
            "breakeven_threshold": financials.get("breakeven_threshold"),
        },
        indent=2,
    )

    comparable_data = financials.get("comparable_data", "No comparable data available.")

    system = """You are an expert startup pitch writer.
You create concise, investor-ready pitch deck outlines in Marp Markdown format.
You do not copy-paste from inputs. You synthesize and tell a story.
Every slide must earn its place. No filler.
Be honest about financials. Never spin break-even if it has not been achieved."""

    prompt = f"""
Create a startup pitch deck in Marp Markdown format using these inputs:

MARKET RESEARCH:
{market_report}

PRODUCT SPEC:
{product_spec}

FINANCIALS:
{finance_summary}

REAL COMPARABLE COMPANIES DATA:
{comparable_data}

Use exactly this slide structure, no more and no less:

---
marp: true
theme: default
paginate: true
---

# [Startup Name]
### [One-line tagline]

---

## The Problem
[2-3 bullet points: specific pain, not generic]

---

## Market Opportunity
[India TAM/SAM/SOM plus one line on global potential]

---

## Our Solution
[One sentence: what it is. One sentence: how it works. No marketing language.]

---

## Key Features
[3-5 bullets: must-have features only]

---

## Business Model
[Pricing and revenue model in 3 bullets]

---

## Comparable Companies
[Table with 2-3 real companies from the comparable data: Name | Founded | Funding | Revenue | Break-even status]
[One line insight: what we learn from their journey]

---

## Financial Projections
[Year 1 to Year 5: transactions, revenue, and profit as a simple table]
[Break-even: state honestly: year number OR "not achieved within 5 years"]
[If not achieved: one line on what cost reduction is needed]

---

## Why Now?
[2-3 reasons this is the right moment, India-specific trends]

---

## The Ask
[Upfront investment needed plus what it will be used for in 3 bullets]

---

RULES:
- Each slide must be short: max 5 bullet points.
- No copying full sentences from inputs.
- Make it sound like a founder presenting, not a report.
- Use INR for Indian rupee amounts.
- On financials slide, never claim break-even if break_even_year is null.
- Comparable companies slide must use real data only.
"""

    return call_llm(prompt, system)
