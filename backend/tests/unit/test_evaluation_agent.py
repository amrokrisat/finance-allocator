import unittest

from app.core.finance import money
from app.models.financial import (
    Account,
    AllocationLine,
    AllocationPlan,
    Debt,
    DebtComparison,
    DebtPlan,
    Expense,
    IncomeSource,
    PlanningRequest,
    SavingsInvestmentPlan,
)
from app.services.evaluation.agent import EvaluationAgent
from app.services.intake.agent import IntakeFinancialProfileAgent


class EvaluationAgentTests(unittest.TestCase):
    def test_evaluation_flags_low_liquidity_and_brokerage_behavior_risk(self) -> None:
        request = PlanningRequest(
            objective="Balance saving and investing",
            incomes=[IncomeSource(name="Salary", net_amount=money(4000), frequency="monthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(2000), frequency="monthly", category="housing", is_essential=True)],
            debts=[Debt(name="Card", current_balance=money(3000), interest_rate=money(22), minimum_payment=money(90))],
            accounts=[Account(name="Checking", account_type="checking", balance=money(500), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        plan = AllocationPlan(
            monthly_allocations=[
                AllocationLine(bucket="mandatory_expense", name="Rent", amount=money(2000), reason="Required"),
                AllocationLine(bucket="brokerage", name="Brokerage", amount=money(100), reason="Investing"),
                AllocationLine(bucket="buffer", name="Cash Buffer", amount=money(50), reason="Slack"),
            ],
            per_paycheck_allocations=[],
            monthly_income_total=money(4000),
            monthly_allocated_total=money(2150),
            monthly_unallocated_cash=money(1850),
            iteration_adjustments=[],
        )
        debt_plan = DebtPlan(
            recommended_framework="avalanche",
            comparison={
                "avalanche": DebtComparison("avalanche", 10, money(500), ["Card"]),
                "snowball": DebtComparison("snowball", 10, money(550), ["Card"]),
            },
            payoff_order=["Card"],
            estimated_payoff_months=10,
            estimated_interest_cost=money(500),
            interest_saved_vs_alternative=money(50),
            unsustainable_debt_load=False,
            notes=[],
        )
        savings_plan = SavingsInvestmentPlan(
            emergency_fund_target=money(6000),
            emergency_fund_gap=money(5500),
            emergency_fund_monthly_recommendation=money(300),
            sinking_funds=[],
            retirement_recommendation=money(200),
            brokerage_recommendation=money(100),
            short_term_goal_recommendations=[],
            notes=[],
        )

        evaluation = EvaluationAgent().evaluate(snapshot, plan, debt_plan, savings_plan)

        self.assertTrue(evaluation.fragility_risks)
        self.assertTrue(evaluation.behavioral_risks)
        self.assertTrue(evaluation.behavior_guardrails)
        self.assertTrue(evaluation.opportunity_areas)
        self.assertIsInstance(evaluation.resilience_summary, str)
        self.assertGreaterEqual(evaluation.stability_score, 0)
        self.assertLess(evaluation.plan_quality_score, 82)
