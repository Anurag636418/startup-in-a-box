import json

from tools.common_utils import call_llm, truncate_text
from tools.finance_tools import (
    calculate_break_even_gap,
    calculate_revenue,
    find_break_even_year,
    validate_financial_projection,
)
from tools.market_tools import get_financial_benchmarks


def _strip_json_fence(raw: str) -> str:
    clean = raw.strip()
    if clean.startswith("```"):
        clean = clean.split("```", 2)[1]
        if clean.startswith("json"):
            clean = clean[4:]
    return clean.strip()


def run_financial_analyst(market_report: str, product_spec: str) -> dict:
    print("Financial Analyst is building projections...")
    market_report = truncate_text(market_report, 8_000, "market report")
    product_spec = truncate_text(product_spec, 5_000, "product spec")

    sector = call_llm(
        f"Extract the industry/sector in 3 words max from this market report: {market_report[:500]}",
        "Reply with only 3 words describing the sector. Nothing else.",
    ).strip()

    startup_context = f"{market_report[:1200]}\n\nPRODUCT SPEC:\n{product_spec[:800]}"
    benchmark_data = get_financial_benchmarks(startup_context, sector)
    benchmark_data = truncate_text(benchmark_data, 8_000, "financial benchmarks")
    print(f"\nFinancial benchmarks found for sector hint: {sector}")
    print(benchmark_data[:500] + "...\n")

    system = """You are a startup financial analyst.
You create realistic 5-year financial projections based on market and product inputs.
You MUST respond with valid JSON only. No explanation, no markdown, no extra text.
Numbers must be internally consistent: revenue must equal transactions * price * commission rate.
Be conservative and realistic. Use real comparable company data as your benchmark.
Never fabricate break-even. Report honestly even if break-even is beyond Year 5.
Separate public data from estimates. If a benchmark is unavailable, say it is unavailable."""

    prompt = f"""
Based on this market research, product spec, and WEB-RESEARCHED financial benchmarks,
generate a 5-year financial projection.

MARKET RESEARCH:
{market_report}

PRODUCT SPEC:
{product_spec}

WEB-RESEARCHED FINANCIAL BENCHMARKS:
{benchmark_data}

IMPORTANT RULES:
- revenue_inr is ONLY the platform's commission, NOT the full rental fee
- revenue_inr MUST equal: year_transactions * avg_transaction_value_inr * (commission_rate_percent/100)
- Example: 5000 transactions * INR 1000 avg * 20% commission = INR 1,000,000 revenue
- Year 1 transactions should be conservative
- Use comparable companies' early revenue numbers as a reality check
- Use the related industry identified in the benchmark research, not only the wording from the original idea
- Prefer public/available financial data; use estimated ranges only when clearly labeled in notes
- If important benchmark data is unavailable, reflect that uncertainty in notes and stay conservative
- Costs should NOT grow faster than revenue after Year 2
- Do NOT force break-even
- In the notes field, state at what cost level break-even becomes achievable in Year 5

Respond with ONLY this JSON structure:

{{
  "assumptions": {{
    "pricing_model": "string",
    "avg_transaction_value_inr": number,
    "commission_rate_percent": number,
    "year1_target_transactions": number,
    "growth_rate_percent": number,
    "key_costs": ["string", "string", "string"],
    "notes": "string"
  }},
  "projections": [
    {{"year": 1, "transactions": number, "revenue_inr": number, "costs_inr": number, "profit_inr": number}},
    {{"year": 2, "transactions": number, "revenue_inr": number, "costs_inr": number, "profit_inr": number}},
    {{"year": 3, "transactions": number, "revenue_inr": number, "costs_inr": number, "profit_inr": number}},
    {{"year": 4, "transactions": number, "revenue_inr": number, "costs_inr": number, "profit_inr": number}},
    {{"year": 5, "transactions": number, "revenue_inr": number, "costs_inr": number, "profit_inr": number}}
  ],
  "upfront_investment_inr": number,
  "break_even_year": number or null,
  "comparable_companies_summary": "string",
  "financial_benchmark_summary": "string"
}}
"""

    raw = call_llm(prompt, system)

    try:
        result = json.loads(_strip_json_fence(raw))
    except json.JSONDecodeError:
        print("JSON parsing failed, returning raw string")
        return {"raw": raw}

    try:
        result = validate_financial_projection(result)
    except ValueError as exc:
        print(f"Financial projection validation failed: {exc}")
        return {"raw": raw, "validation_error": str(exc)}

    result["comparable_data"] = benchmark_data
    result["financial_benchmark_data"] = benchmark_data

    assumptions = result["assumptions"]
    print("\nValidating financial consistency...")
    for projection in result["projections"]:
        expected = calculate_revenue(
            projection["transactions"],
            assumptions["avg_transaction_value_inr"],
            assumptions["commission_rate_percent"],
        )
        actual = projection["revenue_inr"]
        if abs(expected - actual) > max(expected * 0.1, 1):
            print(
                f"Year {projection['year']}: revenue mismatch. "
                f"Expected INR {expected:,.0f}, got INR {actual:,.0f}"
            )
        else:
            print(f"Year {projection['year']}: revenue consistent at INR {actual:,.0f}")

    result["break_even_year"] = find_break_even_year(result["projections"])
    if result["break_even_year"] is None:
        print("No break-even within 5 years")
    else:
        print(f"Break-even year (verified): Year {result['break_even_year']}")

    result["breakeven_threshold"] = calculate_break_even_gap(result["projections"][4])
    if result["breakeven_threshold"]:
        threshold = result["breakeven_threshold"]
        print("\nBreak-even analysis:")
        print(f"   Year 5 revenue:        INR {threshold['year5_revenue']:,.0f}")
        print(f"   Year 5 current costs:  INR {threshold['year5_current_costs']:,.0f}")
        print(
            "   Cost reduction needed: "
            f"INR {threshold['cost_reduction_needed']:,.0f} to break even by Year 5"
        )

    return result
