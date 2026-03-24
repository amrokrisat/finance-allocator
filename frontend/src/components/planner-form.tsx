"use client";

import { useState, useTransition } from "react";

import { buildPlan } from "@/lib/api";
import { createDemoFormState, formStateToPayload, type IntakeFormState } from "@/lib/form";
import type { PlannerResponse } from "@/lib/types";

type PlannerFormProps = {
  onPlanReady: (plan: PlannerResponse) => void;
};

export function PlannerForm({ onPlanReady }: PlannerFormProps) {
  const [form, setForm] = useState<IntakeFormState>(createDemoFormState());
  const [error, setError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [isPending, startTransition] = useTransition();

  const updateField = <K extends keyof IntakeFormState>(key: K, value: IntakeFormState[K]) => {
    setForm((current) => ({ ...current, [key]: value }));
  };

  const handleSubmit = () => {
    startTransition(async () => {
      try {
        setError(null);
        setSubmitted(true);
        const plan = await buildPlan(formStateToPayload(form));
        onPlanReady(plan);
      } catch (submitError) {
        setError(
          submitError instanceof Error
            ? submitError.message
            : "The planner request failed."
        );
      }
    });
  };

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Intake Form</p>
          <h2>Monthly planning inputs</h2>
        </div>
        <button className="ghostButton" onClick={() => setForm(createDemoFormState())}>
          Reset sample
        </button>
      </div>
      <p className="panel-copy">
        MVP tradeoff: this form captures one primary household scenario with a few common inputs so we can validate the backend planning engine without building a large onboarding flow yet.
      </p>
      <div className="inlineNotice">
        <strong>How to use this:</strong> keep the inputs approximate but realistic. The strongest demo is changing one or two fields and showing how the plan adapts.
      </div>
      <div className="formGrid">
        <label className="field">
          <span>Name</span>
          <input value={form.userName} onChange={(event) => updateField("userName", event.target.value)} />
        </label>
        <label className="field fieldWide">
          <span>Objective</span>
          <textarea
            className="textAreaInput"
            value={form.objective}
            onChange={(event) => updateField("objective", event.target.value)}
          />
        </label>

        <div className="sectionLabel">Income</div>
        <label className="field">
          <span>Primary paycheck</span>
          <input value={form.primaryIncome} onChange={(event) => updateField("primaryIncome", event.target.value)} />
        </label>
        <label className="field">
          <span>Side income</span>
          <input value={form.sideIncome} onChange={(event) => updateField("sideIncome", event.target.value)} />
        </label>

        <div className="sectionLabel">Expenses</div>
        <label className="field"><span>Rent</span><input value={form.rent} onChange={(event) => updateField("rent", event.target.value)} /></label>
        <label className="field"><span>Utilities</span><input value={form.utilities} onChange={(event) => updateField("utilities", event.target.value)} /></label>
        <label className="field"><span>Groceries</span><input value={form.groceries} onChange={(event) => updateField("groceries", event.target.value)} /></label>
        <label className="field"><span>Insurance</span><input value={form.insurance} onChange={(event) => updateField("insurance", event.target.value)} /></label>
        <label className="field"><span>Phone</span><input value={form.phone} onChange={(event) => updateField("phone", event.target.value)} /></label>
        <label className="field"><span>Transport</span><input value={form.transport} onChange={(event) => updateField("transport", event.target.value)} /></label>
        <label className="field"><span>Lifestyle</span><input value={form.lifestyle} onChange={(event) => updateField("lifestyle", event.target.value)} /></label>

        <div className="sectionLabel">Debts</div>
        <label className="field"><span>Credit card balance</span><input value={form.creditCardBalance} onChange={(event) => updateField("creditCardBalance", event.target.value)} /></label>
        <label className="field"><span>Credit card APR</span><input value={form.creditCardApr} onChange={(event) => updateField("creditCardApr", event.target.value)} /></label>
        <label className="field"><span>Credit card minimum</span><input value={form.creditCardMinimum} onChange={(event) => updateField("creditCardMinimum", event.target.value)} /></label>
        <label className="field"><span>Student loan balance</span><input value={form.studentLoanBalance} onChange={(event) => updateField("studentLoanBalance", event.target.value)} /></label>
        <label className="field"><span>Student loan APR</span><input value={form.studentLoanApr} onChange={(event) => updateField("studentLoanApr", event.target.value)} /></label>
        <label className="field"><span>Student loan minimum</span><input value={form.studentLoanMinimum} onChange={(event) => updateField("studentLoanMinimum", event.target.value)} /></label>

        <div className="sectionLabel">Balances & Goals</div>
        <label className="field"><span>Checking</span><input value={form.checkingBalance} onChange={(event) => updateField("checkingBalance", event.target.value)} /></label>
        <label className="field"><span>Savings</span><input value={form.savingsBalance} onChange={(event) => updateField("savingsBalance", event.target.value)} /></label>
        <label className="field"><span>Retirement balance</span><input value={form.retirementBalance} onChange={(event) => updateField("retirementBalance", event.target.value)} /></label>
        <label className="field"><span>Sinking fund name</span><input value={form.sinkingFundName} onChange={(event) => updateField("sinkingFundName", event.target.value)} /></label>
        <label className="field"><span>Sinking fund target</span><input value={form.sinkingFundTarget} onChange={(event) => updateField("sinkingFundTarget", event.target.value)} /></label>
        <label className="field"><span>Sinking fund current</span><input value={form.sinkingFundCurrent} onChange={(event) => updateField("sinkingFundCurrent", event.target.value)} /></label>
        <label className="field"><span>Short-term goal</span><input value={form.shortTermGoalName} onChange={(event) => updateField("shortTermGoalName", event.target.value)} /></label>
        <label className="field"><span>Goal target</span><input value={form.shortTermGoalTarget} onChange={(event) => updateField("shortTermGoalTarget", event.target.value)} /></label>
        <label className="field"><span>Goal current</span><input value={form.shortTermGoalCurrent} onChange={(event) => updateField("shortTermGoalCurrent", event.target.value)} /></label>

        <div className="sectionLabel">Strategy</div>
        <label className="field">
          <span>Strategy</span>
          <select value={form.strategyPreference} onChange={(event) => updateField("strategyPreference", event.target.value as IntakeFormState["strategyPreference"])}>
            <option value="conservative">Conservative</option>
            <option value="balanced">Balanced</option>
            <option value="aggressive">Aggressive</option>
          </select>
        </label>
        <label className="field">
          <span>Debt focus</span>
          <select value={form.debtFocus} onChange={(event) => updateField("debtFocus", event.target.value as IntakeFormState["debtFocus"])}>
            <option value="avalanche">Avalanche</option>
            <option value="snowball">Snowball</option>
          </select>
        </label>
        <label className="field"><span>Emergency months</span><input value={form.emergencyMonths} onChange={(event) => updateField("emergencyMonths", event.target.value)} /></label>
        <label className="field"><span>Employer match %</span><input value={form.employerMatchRate} onChange={(event) => updateField("employerMatchRate", event.target.value)} /></label>
        <label className="field"><span>Match cap %</span><input value={form.employerMatchCapPercent} onChange={(event) => updateField("employerMatchCapPercent", event.target.value)} /></label>
        <label className="toggleField">
          <input
            type="checkbox"
            checked={form.wantsEmployerMatch}
            onChange={(event) => updateField("wantsEmployerMatch", event.target.checked)}
          />
          <span>Use employer match</span>
        </label>
        <label className="toggleField">
          <input
            type="checkbox"
            checked={form.brokerageEnabled}
            onChange={(event) => updateField("brokerageEnabled", event.target.checked)}
          />
          <span>Allow brokerage investing</span>
        </label>
      </div>
      <div className="actions">
        <button className="primaryButton" onClick={handleSubmit} disabled={isPending}>
          {isPending ? "Building plan..." : "Build monthly plan"}
        </button>
      </div>
      {submitted && !error ? (
        <p className="successText">Plan generated. Review the explanation, first-30-days actions, and scenario levers on the right.</p>
      ) : null}
      {error ? <p className="errorText">{error}</p> : null}
    </section>
  );
}
