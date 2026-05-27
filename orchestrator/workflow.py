import json
from datetime import datetime
from pathlib import Path

from agents.financial_analyst import run_financial_analyst
from agents.market_analyst import run_market_analyst
from agents.pitch_creator import run_pitch_creator
from agents.product_manager import run_product_manager


def run_pipeline(startup_idea: str) -> dict:
    print(f"\nStarting pipeline for: '{startup_idea}'")
    print("=" * 50)

    results = {}

    results["market"] = run_market_analyst(startup_idea)
    print("Market analysis complete\n")

    results["product"] = run_product_manager(results["market"])
    print("Product spec complete\n")

    results["finance"] = run_financial_analyst(
        results["market"],
        results["product"],
    )
    print("Financial projections complete\n")

    results["pitch"] = run_pitch_creator(
        results["market"],
        results["product"],
        results["finance"],
    )
    print("Pitch deck complete\n")

    print("=" * 50)
    print("Pipeline finished successfully!")

    return results


def save_results(results: dict, output_dir: str | None = None) -> Path:
    if output_dir is None:
        run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = Path("data") / "runs" / run_id
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    pitch_path = output_path / "pitch_deck.md"
    pitch_path.write_text(results["pitch"], encoding="utf-8")
    print(f"Pitch deck saved to {pitch_path}")

    finance_path = output_path / "financials.json"
    finance_path.write_text(json.dumps(results["finance"], indent=2), encoding="utf-8")
    print(f"Financials saved to {finance_path}")

    full_path = output_path / "full_results.json"
    full_path.write_text(
        json.dumps(
            {
                "market": results["market"],
                "product": results["product"],
                "finance": results["finance"],
                "pitch": results["pitch"],
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    print(f"Full results saved to {full_path}")

    return output_path
