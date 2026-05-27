from tools.common_utils import call_llm


def run_market_analyst(startup_idea: str) -> str:
    print("Market Analyst is researching...")

    system = """You are a skeptical market research analyst.
Your job is to validate startup ideas with real reasoning, not hype.
If the idea is too vague, ask one clarifying question, then proceed.
Always structure your output exactly as specified."""

    prompt = f"""
Analyze this startup idea: "{startup_idea}"

Provide a structured market report with these exact sections:

1. PROBLEM DEFINITION
   - What specific problem does this solve?
   - How painful is this problem from 1-10 and why?

2. TARGET USERS
   - Who exactly are the users? Be specific, not "everyone".
   - Primary focus: India, including estimated demand signals and urban/rural split.

3. MARKET SIZE
   - India TAM / SAM / SOM as primary focus.
   - Global TAM one-liner as secondary context, including Southeast Asia or Africa potential.
   - Keep numbers rough but reasoned.

4. COMPETITORS
   - Top 3 existing solutions, including Indian players if any.
   - Your positioning versus them.

5. RISKS & GAPS
   - Top 3 risks specific to the Indian market, such as regulation, infrastructure, or trust.
   - What is still unknown.

6. BUSINESS MODEL
   - Suggested India-appropriate pricing.
   - Revenue model.
   - One line on global replicability.

Be concise but specific. No fluff.
"""

    return call_llm(prompt, system)
