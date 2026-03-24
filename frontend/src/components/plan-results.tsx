import type { PlannerResponse } from "@/lib/types";

type PlanResultsProps = {
  plan: PlannerResponse | null;
};

function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2
  }).format(value);
}

export function PlanResults({ plan }: PlanResultsProps) {
  if (!plan) {
    return (
      <section className="panel">
        <p className="eyebrow">Results Dashboard</p>
        <h2>No plan yet</h2>
        <p className="panel-copy">
          Submit the intake form to see the monthly plan, per-paycheck plan, debt summary, and risk summary.
        </p>
      </section>
    );
  }

  return (
    <section className="resultsGrid">
      <article className="panel dashboardPanel">
        <p className="eyebrow">Results Dashboard</p>
        <h2>Plan at a glance</h2>
        <div className="metricGrid">
          <div className="metricCard">
            <span>Monthly items</span>
            <strong>{plan.final_monthly_plan.length}</strong>
          </div>
          <div className="metricCard">
            <span>Paychecks planned</span>
            <strong>{plan.per_paycheck_plan.length}</strong>
          </div>
          <div className="metricCard">
            <span>Debt strategy</span>
            <strong>{plan.debt_payoff_summary.recommended_framework}</strong>
          </div>
          <div className="metricCard">
            <span>Liquidity months</span>
            <strong>{plan.financial_stability_report.liquidity_months}</strong>
          </div>
          <div className="metricCard">
            <span>Stability score</span>
            <strong>{plan.plan_overview?.stability_score ?? "-"}</strong>
          </div>
          <div className="metricCard">
            <span>Plan quality</span>
            <strong>{plan.plan_overview?.plan_quality_score ?? "-"}</strong>
          </div>
        </div>
        <p className="panel-copy highlightCopy">
          {plan.plan_overview?.resilience_summary}
        </p>
      </article>

      <article className="panel">
        <p className="eyebrow">Why This Plan</p>
        <h2>Plain-English rationale</h2>
        <div className="stack">
          {(plan.why_this_plan ?? []).map((note) => (
            <p key={note} className="panel-copy">{note}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">First 30 Days</p>
        <h2>Immediate actions</h2>
        <div className="stack">
          {(plan.first_30_days ?? []).map((step) => (
            <p key={step} className="subtleChip">{step}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Monthly Plan</p>
        <h2>{plan.objective}</h2>
        <div className="tableLike">
          {plan.final_monthly_plan.map((item) => (
            <div className="row" key={`${item.bucket}-${item.name}`}>
              <div>
                <strong>{item.name}</strong>
                <p>{item.reason}</p>
              </div>
              <span>{formatCurrency(item.amount)}</span>
            </div>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Per Paycheck</p>
        <h2>Cash timing view</h2>
        <div className="stack">
          {plan.per_paycheck_plan.map((paycheck) => (
            <div key={paycheck.paycheck_index} className="subPanel">
              <div className="row">
                <strong>Paycheck {paycheck.paycheck_index}</strong>
                <span>{formatCurrency(paycheck.expected_income)}</span>
              </div>
              {paycheck.allocations.map((item) => (
                <div className="row compact" key={`${paycheck.paycheck_index}-${item.name}`}>
                  <p>{item.name}</p>
                  <span>{formatCurrency(item.amount)}</span>
                </div>
              ))}
              <div className="row compact emphasize">
                <p>Remaining cash</p>
                <span>{formatCurrency(paycheck.remaining_cash)}</span>
              </div>
            </div>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Debt</p>
        <h2>Debt summary</h2>
        <p className="panel-copy">
          Recommended approach: {plan.debt_payoff_summary.recommended_framework}.
        </p>
        <p className="panel-copy">
          Estimated payoff timeline: {plan.debt_payoff_summary.estimated_payoff_months} months.
        </p>
        <p className="panel-copy">
          Estimated interest: {formatCurrency(plan.debt_payoff_summary.estimated_interest_cost)}.
        </p>
        <p className="panel-copy">
          Interest saved vs alternative: {formatCurrency(plan.debt_payoff_summary.interest_saved_vs_alternative)}.
        </p>
        <div className="stack">
          {plan.debt_payoff_summary.payoff_order.map((name) => (
            <p key={name} className="subtleChip">{name}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Risk</p>
        <h2>Risk summary</h2>
        <p className="panel-copy">
          Liquidity coverage: {plan.financial_stability_report.liquidity_months} months.
        </p>
        <div className="stack">
          {plan.risk_assessment.fragility_risks.map((risk) => (
            <p key={risk} className="warningChip">{risk}</p>
          ))}
          {plan.risk_assessment.behavioral_risks.map((risk) => (
            <p key={risk} className="warningChip alt">{risk}</p>
          ))}
          {plan.risk_assessment.validation_warnings.map((warning) => (
            <p key={warning} className="warningChip neutral">{warning}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Guardrails</p>
        <h2>Behavior and maintenance</h2>
        <div className="stack">
          {(plan.risk_assessment.behavior_guardrails ?? []).map((item) => (
            <p key={item} className="subtleChip">{item}</p>
          ))}
          {(plan.risk_assessment.opportunity_areas ?? []).map((item) => (
            <p key={item} className="warningChip neutral">{item}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Savings & Investing</p>
        <h2>Reserve and growth mix</h2>
        <p className="panel-copy">
          Emergency target: {formatCurrency(plan.savings_investing_summary.emergency_fund_target)}.
        </p>
        <p className="panel-copy">
          Monthly emergency contribution: {formatCurrency(plan.savings_investing_summary.emergency_fund_monthly_recommendation)}.
        </p>
        <p className="panel-copy">
          Retirement: {formatCurrency(plan.savings_investing_summary.retirement_recommendation)}.
        </p>
        <p className="panel-copy">
          Brokerage: {formatCurrency(plan.savings_investing_summary.brokerage_recommendation)}.
        </p>
      </article>

      <article className="panel">
        <p className="eyebrow">Scenario Levers</p>
        <h2>Ways to improve the plan</h2>
        <div className="stack">
          {(plan.scenario_levers ?? []).map((lever) => (
            <div key={lever.title} className="subPanel">
              <div className="row compact">
                <strong>{lever.title}</strong>
                <span>{formatCurrency(lever.impact)}</span>
              </div>
              <p className="panel-copy">{lever.description}</p>
            </div>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Assumptions</p>
        <h2>What the engine assumed</h2>
        <div className="stack">
          {(plan.assumptions ?? []).map((item) => (
            <p key={item} className="panel-copy">{item}</p>
          ))}
          {(plan.constraints ?? []).map((item) => (
            <p key={item} className="warningChip neutral">{item}</p>
          ))}
        </div>
      </article>

      <article className="panel">
        <p className="eyebrow">Next Iteration</p>
        <h2>Roadmap</h2>
        <div className="stack">
          {plan.suggested_next_iteration_roadmap.map((step) => (
            <p key={step} className="panel-copy">{step}</p>
          ))}
        </div>
      </article>
    </section>
  );
}
