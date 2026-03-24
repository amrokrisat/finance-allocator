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
        <h1>Design a realistic monthly action plan with an agent-style planning workflow.</h1>
        <p className="heroCopy">
          Enter a compact financial profile, send it to the planner API, and review a results dashboard with the monthly plan, per-paycheck plan, debt summary, and risk summary.
        </p>
      </section>
      <section className="workspace">
        <PlannerForm onPlanReady={setPlan} />
        <PlanResults plan={plan} />
      </section>
    </main>
  );
}
