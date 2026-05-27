from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class FinancialAssumptions(BaseModel):
    pricing_model: str
    avg_transaction_value_inr: float = Field(gt=0)
    commission_rate_percent: float = Field(gt=0, le=100)
    year1_target_transactions: int = Field(ge=0)
    growth_rate_percent: float = Field(ge=0)
    key_costs: list[str]
    notes: str = ""


class YearProjection(BaseModel):
    year: int = Field(ge=1, le=5)
    transactions: int = Field(ge=0)
    revenue_inr: float = Field(ge=0)
    costs_inr: float = Field(ge=0)
    profit_inr: float


class FinancialProjection(BaseModel):
    assumptions: FinancialAssumptions
    projections: list[YearProjection]
    upfront_investment_inr: float = Field(ge=0)
    break_even_year: int | None = None
    comparable_companies_summary: str = ""
    financial_benchmark_summary: str = ""

    @field_validator("projections")
    @classmethod
    def require_five_years(cls, value: list[YearProjection]) -> list[YearProjection]:
        if len(value) != 5:
            raise ValueError("financial projection must contain exactly 5 years")
        return value


def calculate_revenue(
    transactions: int,
    avg_transaction_value_inr: float,
    commission_rate_percent: float,
) -> float:
    return transactions * avg_transaction_value_inr * (commission_rate_percent / 100)


def calculate_profit(revenue_inr: float, costs_inr: float) -> float:
    return revenue_inr - costs_inr


def find_break_even_year(projections: list[dict[str, Any]]) -> int | None:
    for projection in projections:
        if projection["profit_inr"] > 0:
            return int(projection["year"])
    return None


def calculate_break_even_gap(year_projection: dict[str, Any]) -> dict[str, float] | None:
    revenue = float(year_projection["revenue_inr"])
    costs = float(year_projection["costs_inr"])
    if revenue >= costs:
        return None

    return {
        "year5_revenue": revenue,
        "year5_current_costs": costs,
        "cost_reduction_needed": costs - revenue,
    }


def validate_financial_projection(payload: dict[str, Any]) -> dict[str, Any]:
    validated = FinancialProjection.model_validate(payload)
    return validated.model_dump()
