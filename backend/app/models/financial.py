"""Domain models for the finance planning engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional


@dataclass
class IncomeSource:
    name: str
    net_amount: Decimal
    frequency: str
    pay_day: Optional[int] = None


@dataclass
class Expense:
    name: str
    amount: Decimal
    frequency: str
    category: str
    is_essential: bool = True
    due_day: Optional[int] = None


@dataclass
class Debt:
    name: str
    current_balance: Decimal
    interest_rate: Decimal
    minimum_payment: Decimal
    due_day: Optional[int] = None


@dataclass
class Account:
    name: str
    account_type: str
    balance: Decimal
    is_liquid: bool = False
    is_tax_advantaged: bool = False


@dataclass
class Goal:
    name: str
    goal_type: str
    target_amount: Decimal
    current_amount: Decimal = Decimal("0.00")
    target_date: Optional[date] = None
    priority: int = 3


@dataclass
class Preferences:
    strategy_preference: str = "balanced"
    debt_focus: str = "avalanche"
    wants_employer_match: bool = False
    employer_match_rate: Decimal = Decimal("0.00")
    employer_match_cap_percent: Decimal = Decimal("0.00")
    retirement_min_percent: Decimal = Decimal("0.05")
    brokerage_enabled: bool = True
    target_emergency_months: Decimal = Decimal("3.00")
    risk_tolerance: str = "moderate"


@dataclass
class PlanningRequest:
    objective: str
    incomes: List[IncomeSource]
    expenses: List[Expense]
    debts: List[Debt]
    accounts: List[Account]
    goals: List[Goal]
    preferences: Preferences = field(default_factory=Preferences)
    user_name: str = "User"


@dataclass
class StageStatus:
    stage: str
    status: str
    details: str


@dataclass
class PlanningSnapshot:
    request: PlanningRequest
    monthly_income_total: Decimal
    monthly_expense_total: Decimal
    monthly_essential_expense_total: Decimal
    monthly_minimum_debt_total: Decimal
    liquid_assets_total: Decimal
    assets_total: Decimal
    liabilities_total: Decimal
    net_worth: Decimal
    monthly_discretionary_pre_strategy: Decimal
    financial_profile: Dict[str, object]
    cash_flow_summary: Dict[str, object]
    balance_sheet_snapshot: Dict[str, object]
    goals_summary: Dict[str, object]
    assumptions: List[str]
    constraints: List[str]
    missing_requirements: List[str]


@dataclass
class StrategyDecision:
    priority_order: List[str]
    decision_waterfall: List[str]
    debt_framework: str
    savings_investing_balance: Dict[str, Decimal]
    strategic_notes: List[str]
    iteration_notes: List[str] = field(default_factory=list)


@dataclass
class DebtComparison:
    framework: str
    estimated_months: int
    total_interest: Decimal
    payoff_order: List[str]


@dataclass
class DebtPlan:
    recommended_framework: str
    comparison: Dict[str, DebtComparison]
    payoff_order: List[str]
    estimated_payoff_months: int
    estimated_interest_cost: Decimal
    interest_saved_vs_alternative: Decimal
    unsustainable_debt_load: bool
    notes: List[str]


@dataclass
class SavingsInvestmentPlan:
    emergency_fund_target: Decimal
    emergency_fund_gap: Decimal
    emergency_fund_monthly_recommendation: Decimal
    sinking_funds: List[Dict[str, object]]
    retirement_recommendation: Decimal
    brokerage_recommendation: Decimal
    short_term_goal_recommendations: List[Dict[str, object]]
    notes: List[str]


@dataclass
class AllocationLine:
    bucket: str
    name: str
    amount: Decimal
    reason: str
    due_day: Optional[int] = None


@dataclass
class PaycheckAllocation:
    paycheck_index: int
    expected_income: Decimal
    allocations: List[AllocationLine]
    remaining_cash: Decimal


@dataclass
class AllocationPlan:
    monthly_allocations: List[AllocationLine]
    per_paycheck_allocations: List[PaycheckAllocation]
    monthly_income_total: Decimal
    monthly_allocated_total: Decimal
    monthly_unallocated_cash: Decimal
    iteration_adjustments: List[str]


@dataclass
class FailureReport:
    code: str
    severity: str
    message: str
    stage: str


@dataclass
class ValidationResult:
    passed: bool
    failures: List[FailureReport]
    warnings: List[str]


@dataclass
class EvaluationReport:
    plan_quality_score: int
    maintainability_score: int
    fragility_risks: List[str]
    behavioral_risks: List[str]
    refinement_opportunities: List[str]
    financial_stability_report: Dict[str, object]


@dataclass
class PlanningSummary:
    objective: str
    stages: List[StageStatus]
    iterations: List[Dict[str, object]]
    final_monthly_plan: List[Dict[str, object]]
    per_paycheck_plan: List[Dict[str, object]]
    debt_payoff_summary: Dict[str, object]
    savings_investing_summary: Dict[str, object]
    risk_assessment: Dict[str, object]
    financial_stability_report: Dict[str, object]
    suggested_next_iteration_roadmap: List[str]
    logs: List[Dict[str, object]]

