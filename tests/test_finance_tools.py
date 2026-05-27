from tools.finance_tools import (
    calculate_break_even_gap,
    calculate_profit,
    calculate_revenue,
    find_break_even_year,
    validate_financial_projection,
)


def test_calculate_revenue_uses_commission_only():
    revenue = calculate_revenue(
        transactions=5_000,
        avg_transaction_value_inr=1_000,
        commission_rate_percent=20,
    )

    assert revenue == 1_000_000


def test_calculate_profit():
    assert calculate_profit(1_000_000, 750_000) == 250_000


def test_find_break_even_year_returns_first_profitable_year():
    projections = [
        {"year": 1, "profit_inr": -100},
        {"year": 2, "profit_inr": 0},
        {"year": 3, "profit_inr": 50},
    ]

    assert find_break_even_year(projections) == 3


def test_find_break_even_year_returns_none_when_not_profitable():
    projections = [
        {"year": 1, "profit_inr": -100},
        {"year": 2, "profit_inr": 0},
    ]

    assert find_break_even_year(projections) is None


def test_calculate_break_even_gap():
    gap = calculate_break_even_gap(
        {"year": 5, "revenue_inr": 1_200_000, "costs_inr": 1_500_000}
    )

    assert gap == {
        "year5_revenue": 1_200_000,
        "year5_current_costs": 1_500_000,
        "cost_reduction_needed": 300_000,
    }


def test_validate_financial_projection_accepts_expected_shape():
    payload = {
        "assumptions": {
            "pricing_model": "commission",
            "avg_transaction_value_inr": 1_000,
            "commission_rate_percent": 20,
            "year1_target_transactions": 5_000,
            "growth_rate_percent": 50,
            "key_costs": ["marketing", "operations"],
            "notes": "Directional estimate",
        },
        "projections": [
            {"year": 1, "transactions": 5_000, "revenue_inr": 1_000_000, "costs_inr": 1_500_000, "profit_inr": -500_000},
            {"year": 2, "transactions": 7_500, "revenue_inr": 1_500_000, "costs_inr": 1_700_000, "profit_inr": -200_000},
            {"year": 3, "transactions": 11_250, "revenue_inr": 2_250_000, "costs_inr": 2_000_000, "profit_inr": 250_000},
            {"year": 4, "transactions": 16_875, "revenue_inr": 3_375_000, "costs_inr": 2_500_000, "profit_inr": 875_000},
            {"year": 5, "transactions": 25_312, "revenue_inr": 5_062_400, "costs_inr": 3_000_000, "profit_inr": 2_062_400},
        ],
        "upfront_investment_inr": 500_000,
        "break_even_year": 3,
        "comparable_companies_summary": "Comparable benchmark summary",
    }

    validated = validate_financial_projection(payload)

    assert validated["assumptions"]["commission_rate_percent"] == 20
    assert len(validated["projections"]) == 5
