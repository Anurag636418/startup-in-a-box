from tools.common_utils import call_llm, truncate_text


def run_product_manager(market_report: str) -> str:
    print("Product Manager is defining the product...")
    market_report = truncate_text(market_report, 8_000, "market report")

    system = """You are a sharp product manager.
You read market research and convert it into a focused, buildable product spec.
Do not rewrite or repeat the market analysis. Extract only what matters for building.
Be opinionated. Make decisions instead of listing options."""

    prompt = f"""
Based on this market research, define the product:

{market_report}

Provide a product spec with these exact sections:

1. PRODUCT OVERVIEW
   - What is it? One clear sentence.
   - Who is it for? Be specific.
   - What does it replace or improve?

2. CORE VALUE PROPOSITION
   - One sentence: "We help [user] do [job] without [pain]".

3. KEY FEATURES
   - Pick 3-5 launch essentials only.
   - For each feature: name, what it does, and why it matters.

4. NON-FEATURES
   - 2-3 things we deliberately will not build at launch.

5. CONSTRAINTS & CONSIDERATIONS
   - Technical constraints such as offline support or vernacular languages.
   - Trust/adoption constraints from market research.
   - Pricing constraints for India.

Keep it tight. A developer should be able to read this and start building.
"""

    return call_llm(prompt, system)
