"""Schema parsing and serialization helpers."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.core.finance import decimal_to_float, money
from app.models.financial import (
    Account,
    Debt,
    Expense,
    Goal,
    IncomeSource,
    PlanningRequest,
    PlanningSummary,
    Preferences,
)

SUPPORTED_FREQUENCIES = {
    "weekly",
    "biweekly",
    "semimonthly",
    "monthly",
    "quarterly",
    "annual",
}
SUPPORTED_ACCOUNT_TYPES = {
    "checking",
    "savings",
    "emergency_fund",
    "retirement",
    "brokerage",
    "debt",
    "other",
}
SUPPORTED_GOAL_TYPES = {
    "emergency_fund",
    "sinking_fund",
    "short_term",
    "retirement",
    "brokerage",
}


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    return date.fromisoformat(value)


def _require_string(payload: Dict[str, Any], field: str) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required.")
    return value


def _require_list(payload: Dict[str, Any], field: str) -> List[Dict[str, Any]]:
    value = payload.get(field, [])
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return value


def _validate_frequency(value: str, field_name: str) -> str:
    if value not in SUPPORTED_FREQUENCIES:
        raise ValueError(f"{field_name} must be one of {sorted(SUPPORTED_FREQUENCIES)}.")
    return value


def _validate_non_negative(value: Decimal, field_name: str) -> Decimal:
    if value < 0:
        raise ValueError(f"{field_name} must be non-negative.")
    return value


def _validate_day(value: Optional[int], field_name: str) -> Optional[int]:
    if value is None:
        return None
    if not isinstance(value, int) or value < 1 or value > 31:
        raise ValueError(f"{field_name} must be an integer between 1 and 31.")
    return value


def _validate_account_type(value: str) -> str:
    if value not in SUPPORTED_ACCOUNT_TYPES:
        raise ValueError(f"account_type must be one of {sorted(SUPPORTED_ACCOUNT_TYPES)}.")
    return value


def _validate_goal_type(value: str) -> str:
    if value not in SUPPORTED_GOAL_TYPES:
        raise ValueError(f"goal_type must be one of {sorted(SUPPORTED_GOAL_TYPES)}.")
    return value


def _validate_priority(value: int) -> int:
    if value < 1 or value > 5:
        raise ValueError("priority must be between 1 and 5.")
    return value


def planning_request_from_dict(payload: Dict[str, Any]) -> PlanningRequest:
    objective = _require_string(payload, "objective")
    incomes_payload = _require_list(payload, "incomes")
    expenses_payload = _require_list(payload, "expenses")
    debts_payload = _require_list(payload, "debts")
    accounts_payload = _require_list(payload, "accounts")
    goals_payload = _require_list(payload, "goals")
    preferences_payload = payload.get("preferences", {})
    preferences = Preferences(
        strategy_preference=preferences_payload.get("strategy_preference", "balanced"),
        debt_focus=preferences_payload.get("debt_focus", "avalanche"),
        wants_employer_match=bool(preferences_payload.get("wants_employer_match", False)),
        employer_match_rate=money(preferences_payload.get("employer_match_rate", 0)),
        employer_match_cap_percent=money(preferences_payload.get("employer_match_cap_percent", 0)),
        retirement_min_percent=money(preferences_payload.get("retirement_min_percent", 0.05)),
        brokerage_enabled=bool(preferences_payload.get("brokerage_enabled", True)),
        target_emergency_months=money(preferences_payload.get("target_emergency_months", 3)),
        risk_tolerance=preferences_payload.get("risk_tolerance", "moderate"),
    )

    return PlanningRequest(
        objective=objective,
        user_name=payload.get("user_name", "User"),
        incomes=[
            IncomeSource(
                name=_require_string(item, "name"),
                net_amount=_validate_non_negative(money(item["net_amount"]), "net_amount"),
                frequency=_validate_frequency(item["frequency"], "income frequency"),
                pay_day=_validate_day(item.get("pay_day"), "pay_day"),
            )
            for item in incomes_payload
        ],
        expenses=[
            Expense(
                name=_require_string(item, "name"),
                amount=_validate_non_negative(money(item["amount"]), "amount"),
                frequency=_validate_frequency(item["frequency"], "expense frequency"),
                category=item.get("category", "general"),
                is_essential=bool(item.get("is_essential", True)),
                due_day=_validate_day(item.get("due_day"), "due_day"),
            )
            for item in expenses_payload
        ],
        debts=[
            Debt(
                name=_require_string(item, "name"),
                current_balance=_validate_non_negative(money(item["current_balance"]), "current_balance"),
                interest_rate=_validate_non_negative(money(item["interest_rate"]), "interest_rate"),
                minimum_payment=_validate_non_negative(money(item["minimum_payment"]), "minimum_payment"),
                due_day=_validate_day(item.get("due_day"), "due_day"),
            )
            for item in debts_payload
        ],
        accounts=[
            Account(
                name=_require_string(item, "name"),
                account_type=_validate_account_type(item["account_type"]),
                balance=_validate_non_negative(money(item["balance"]), "balance"),
                is_liquid=bool(item.get("is_liquid", False)),
                is_tax_advantaged=bool(item.get("is_tax_advantaged", False)),
            )
            for item in accounts_payload
        ],
        goals=[
            Goal(
                name=_require_string(item, "name"),
                goal_type=_validate_goal_type(item["goal_type"]),
                target_amount=_validate_non_negative(money(item["target_amount"]), "target_amount"),
                current_amount=_validate_non_negative(money(item.get("current_amount", 0)), "current_amount"),
                target_date=_parse_date(item.get("target_date")),
                priority=_validate_priority(int(item.get("priority", 3))),
            )
            for item in goals_payload
        ],
        preferences=preferences,
    )


def _serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return decimal_to_float(value)
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _serialize_value(asdict(value))
    if isinstance(value, date):
        return value.isoformat()
    return value


def planning_summary_to_dict(summary: PlanningSummary) -> Dict[str, Any]:
    return _serialize_value(asdict(summary))
