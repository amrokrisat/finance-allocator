"use client";

import { useState } from "react";

import { PlannerForm } from "@/components/planner-form";
import { PlanResults } from "@/components/plan-results";
import type { PlannerResponse } from "@/lib/types";

export default function HomePage() {
  const [plan, setPlan] = useState<PlannerResponse | null>(null);

  return (
    <main className="pageShell">
      <section className="hero">
        <p className="eyebrow">Personal Finance Allocation System</p>
        <h1>Know exactly where your next dollars should go.</h1>
        <p className="heroCopy">
          Finance Allocator turns a financial profile into a realistic monthly plan, a per-paycheck cash map, debt and savings priorities, and a plain-English explanation of why the recommendation makes sense.
        </p>
        <div className="heroPoints">
          <p>Clear problem: most people know their goals but not the exact monthly allocations to get there.</p>
          <p>Useful output: monthly plan, paycheck plan, debt summary, risk summary, and next-step roadmap.</p>
          <p>Transparent logic: deterministic rules, visible assumptions, and practical tradeoffs instead of black-box recommendations.</p>
        </div>
      </section>
      <section className="trustStrip">
        <div className="trustCard">
          <span>What it solves</span>
          <strong>Monthly money decisions</strong>
          <p>Turns “I should probably save more” into exact allocation amounts.</p>
        </div>
        <div className="trustCard">
          <span>Why trust it</span>
          <strong>Explainable engine</strong>
          <p>Every recommendation is tied to strategy, debt rules, or cash-safety logic.</p>
        </div>
        <div className="trustCard">
          <span>What makes it different</span>
          <strong>Paycheck-aware planning</strong>
          <p>It does not stop at monthly budgets. It shows timing by paycheck.</p>
        </div>
      </section>
      <section className="workspace">
        <PlannerForm onPlanReady={setPlan} />
        <PlanResults plan={plan} />
      </section>
    </main>
  );
}
