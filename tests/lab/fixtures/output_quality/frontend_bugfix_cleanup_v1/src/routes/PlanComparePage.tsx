import type { Plan } from "../data/plans";

export function PlanComparePage({ plans }: { plans: Plan[] }) {
  return (
    <main>
      <section className="panel">
        <p>Plans</p>
        <h1>Starter comparison table</h1>
        <ul>
          {plans.map((plan) => (
            <li key={plan.slug}>
              {plan.name} - ${plan.monthlyPrice}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
