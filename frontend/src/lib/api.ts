import demoPlan from "@/lib/fixtures/sample-plan.json";
import type { PlannerPayload, PlannerResponse } from "@/lib/types";

export async function buildPlan(payload: PlannerPayload): Promise<PlannerResponse> {
  const endpoint = process.env.NEXT_PUBLIC_PLANNER_API_URL;

  if (!endpoint) {
    // Demo mode fallback: when no live planner API is configured, we still
    // return a backend-generated example plan so the app is immediately usable.
    return demoPlan as PlannerResponse;
  }

  let response: Response;
  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    throw new Error(
      error instanceof Error
        ? `Planner API request failed: ${error.message}`
        : "Planner API request failed."
    );
  }

  if (!response.ok) {
    throw new Error(`Planner request failed with status ${response.status}.`);
  }

  return (await response.json()) as PlannerResponse;
}
