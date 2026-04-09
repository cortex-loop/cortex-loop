import type { Invoice, Plan } from "../data/plans";
import { dueInvoiceTotal, featuredPlan } from "../data/plans";

type Props = {
  invoices: Invoice[];
  plans: Plan[];
};

export function BillingPage({ invoices, plans }: Props) {
  const featured = featuredPlan(plans);
  return (
    <main>
      <section className="panel">
        <p>Billing summary</p>
        <h1>Revenue and plan health</h1>
        <p>Due invoices total: ${dueInvoiceTotal(invoices)}</p>
        <p>Recommended plan: {featured.name}</p>
      </section>
    </main>
  );
}
