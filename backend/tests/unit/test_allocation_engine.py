import unittest

from app.core.finance import money
from app.models.financial import (
    Account,
    Debt,
    Expense,
    IncomeSource,
    PlanningRequest,
)
from app.services.allocation.agent import AllocationEngineAgent
from app.services.debt.agent import DebtOptimizationAgent
from app.services.intake.agent import IntakeFinancialProfileAgent
from app.services.savings_investing.agent import SavingsInvestmentAgent
from app.services.strategy.agent import StrategyAgent


class AllocationEngineTests(unittest.TestCase):
    def test_monthly_plan_respects_income_constraint(self) -> None:
        request = PlanningRequest(
            objective="Stabilize and grow",
            incomes=[IncomeSource(name="Salary", net_amount=money(3000), frequency="semimonthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1500), frequency="monthly", category="housing", due_day=1),
                Expense(name="Food", amount=money(400), frequency="monthly", category="food", due_day=15),
            ],
            debts=[Debt(name="Card", current_balance=money(2000), interest_rate=money(19.9), minimum_payment=money(75), due_day=20)],
            accounts=[Account(name="Checking", account_type="checking", balance=money(500), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        discretionary = money(snapshot.monthly_income_total - snapshot.monthly_expense_total - snapshot.monthly_minimum_debt_total)
        extra_debt = money(discretionary * strategy.savings_investing_balance["debt_weight"])
        debt_plan = DebtOptimizationAgent().analyze(snapshot, extra_debt)
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, discretionary - extra_debt)
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        self.assertLessEqual(plan.monthly_allocated_total, plan.monthly_income_total)
        self.assertTrue(any(item.bucket == "mandatory_expense" and item.name == "Rent" for item in plan.monthly_allocations))

    def test_buffer_equals_unassigned_monthly_cash(self) -> None:
        request = PlanningRequest(
            objective="Keep a small cash cushion",
            incomes=[IncomeSource(name="Salary", net_amount=money(2000), frequency="monthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(1000), frequency="monthly", category="housing", due_day=1)],
            debts=[],
            accounts=[Account(name="Checking", account_type="checking", balance=money(300), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        debt_plan = DebtOptimizationAgent().analyze(snapshot, money(0))
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, money(1000))
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        buffer_items = [item for item in plan.monthly_allocations if item.bucket == "buffer"]
        self.assertEqual(len(buffer_items), 1)
        self.assertEqual(plan.monthly_allocated_total, plan.monthly_income_total)
        self.assertGreaterEqual(buffer_items[0].amount, money(0))

    def test_paycheck_allocations_do_not_schedule_buffer(self) -> None:
        request = PlanningRequest(
            objective="Avoid fake timing failures",
            incomes=[IncomeSource(name="Salary", net_amount=money(1500), frequency="semimonthly", pay_day=1)],
            expenses=[Expense(name="Rent", amount=money(900), frequency="monthly", category="housing", due_day=1)],
            debts=[],
            accounts=[Account(name="Checking", account_type="checking", balance=money(100), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        debt_plan = DebtOptimizationAgent().analyze(snapshot, money(0))
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, money(600))
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        scheduled_names = {
            allocation.name
            for paycheck in plan.per_paycheck_allocations
            for allocation in paycheck.allocations
        }
        self.assertNotIn("Cash Buffer", scheduled_names)

    def test_nonessential_expenses_are_not_marked_mandatory(self) -> None:
        request = PlanningRequest(
            objective="Fund essentials before lifestyle spending",
            incomes=[IncomeSource(name="Salary", net_amount=money(2500), frequency="monthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1200), frequency="monthly", category="housing", is_essential=True, due_day=1),
                Expense(name="Streaming", amount=money(30), frequency="monthly", category="fun", is_essential=False, due_day=25),
            ],
            debts=[],
            accounts=[Account(name="Checking", account_type="checking", balance=money(100), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        debt_plan = DebtOptimizationAgent().analyze(snapshot, money(0))
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, money(1000))
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        buckets = {item.name: item.bucket for item in plan.monthly_allocations}
        self.assertEqual(buckets["Rent"], "mandatory_expense")
        self.assertEqual(buckets["Streaming"], "flexible_expense")

    def test_mandatory_expenses_and_debt_minimums_appear_before_optional_buckets(self) -> None:
        request = PlanningRequest(
            objective="Follow the waterfall",
            incomes=[IncomeSource(name="Salary", net_amount=money(2800), frequency="monthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1200), frequency="monthly", category="housing", is_essential=True, due_day=1),
                Expense(name="Food", amount=money(300), frequency="monthly", category="food", is_essential=True, due_day=10),
            ],
            debts=[Debt(name="Card", current_balance=money(1000), interest_rate=money(20), minimum_payment=money(50), due_day=18)],
            accounts=[Account(name="Checking", account_type="checking", balance=money(300), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        discretionary = money(snapshot.monthly_income_total - snapshot.monthly_expense_total - snapshot.monthly_minimum_debt_total)
        debt_plan = DebtOptimizationAgent().analyze(snapshot, money(discretionary * strategy.savings_investing_balance["debt_weight"]))
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, discretionary)
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        sequence = [item.bucket for item in plan.monthly_allocations]
        first_optional_index = min(
            index for index, bucket in enumerate(sequence) if bucket not in {"mandatory_expense", "flexible_expense", "debt_minimum"}
        )
        self.assertTrue(all(bucket in {"mandatory_expense", "debt_minimum"} for bucket in sequence[:3]))
        self.assertGreaterEqual(first_optional_index, 3)

    def test_monthly_allocation_totals_are_mathematically_consistent(self) -> None:
        request = PlanningRequest(
            objective="Check the math",
            incomes=[IncomeSource(name="Salary", net_amount=money(3200), frequency="semimonthly", pay_day=1)],
            expenses=[
                Expense(name="Rent", amount=money(1400), frequency="monthly", category="housing", is_essential=True, due_day=1),
                Expense(name="Groceries", amount=money(400), frequency="monthly", category="food", is_essential=True, due_day=14),
            ],
            debts=[Debt(name="Card", current_balance=money(2000), interest_rate=money(18), minimum_payment=money(80), due_day=20)],
            accounts=[Account(name="Checking", account_type="checking", balance=money(500), is_liquid=True)],
            goals=[],
        )
        snapshot = IntakeFinancialProfileAgent().process(request)
        strategy = StrategyAgent().decide(snapshot)
        discretionary = money(snapshot.monthly_income_total - snapshot.monthly_expense_total - snapshot.monthly_minimum_debt_total)
        debt_plan = DebtOptimizationAgent().analyze(snapshot, money(discretionary * strategy.savings_investing_balance["debt_weight"]))
        savings_plan = SavingsInvestmentAgent().build(snapshot, strategy.savings_investing_balance, discretionary)
        plan = AllocationEngineAgent().build_plan(snapshot, strategy, debt_plan, savings_plan)

        summed = money(sum(item.amount for item in plan.monthly_allocations))
        self.assertEqual(summed, plan.monthly_allocated_total)
        self.assertEqual(plan.monthly_allocated_total, plan.monthly_income_total)


if __name__ == "__main__":
    unittest.main()
