"""Sample planner payloads used for local demos and smoke tests."""

from __future__ import annotations

from typing import Any, Dict


def sample_planning_payload() -> Dict[str, Any]:
    return {
        "user_name": "Avery",
        "objective": "Create a realistic monthly action plan that improves liquidity, pays down debt, and funds near-term goals.",
        "incomes": [
            {"name": "Primary Salary", "net_amount": 2950, "frequency": "semimonthly", "pay_day": 1},
            {"name": "Freelance", "net_amount": 600, "frequency": "monthly", "pay_day": 20},
        ],
        "expenses": [
            {"name": "Rent", "amount": 1750, "frequency": "monthly", "category": "housing", "is_essential": True, "due_day": 1},
            {"name": "Utilities", "amount": 240, "frequency": "monthly", "category": "housing", "is_essential": True, "due_day": 12},
            {"name": "Groceries", "amount": 550, "frequency": "monthly", "category": "food", "is_essential": True, "due_day": 16},
            {"name": "Insurance", "amount": 180, "frequency": "monthly", "category": "insurance", "is_essential": True, "due_day": 18},
            {"name": "Phone", "amount": 85, "frequency": "monthly", "category": "utilities", "is_essential": True, "due_day": 24},
            {"name": "Transit", "amount": 140, "frequency": "monthly", "category": "transportation", "is_essential": True, "due_day": 25},
            {"name": "Gym", "amount": 50, "frequency": "monthly", "category": "lifestyle", "is_essential": False, "due_day": 26},
        ],
        "debts": [
            {"name": "Credit Card", "current_balance": 5200, "interest_rate": 24.99, "minimum_payment": 165, "due_day": 20},
            {"name": "Student Loan", "current_balance": 9800, "interest_rate": 5.4, "minimum_payment": 120, "due_day": 28},
        ],
        "accounts": [
            {"name": "Checking", "account_type": "checking", "balance": 1400, "is_liquid": True},
            {"name": "Savings", "account_type": "savings", "balance": 900, "is_liquid": True},
            {"name": "401k", "account_type": "retirement", "balance": 7600, "is_liquid": False, "is_tax_advantaged": True},
        ],
        "goals": [
            {"name": "Car Maintenance", "goal_type": "sinking_fund", "target_amount": 1200, "current_amount": 300, "priority": 2},
            {"name": "Travel", "goal_type": "short_term", "target_amount": 1800, "current_amount": 250, "priority": 3},
        ],
        "preferences": {
            "strategy_preference": "balanced",
            "debt_focus": "avalanche",
            "wants_employer_match": True,
            "employer_match_rate": 4,
            "employer_match_cap_percent": 4,
            "target_emergency_months": 3,
            "brokerage_enabled": True,
        },
    }
