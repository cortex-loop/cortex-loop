import type { Invoice } from "../data/plans";
import { filterInvoices } from "../data/plans";

type Props = {
  activeStatus: string;
  invoices: Invoice[];
  onStatusChange: (value: string) => void;
};

export function InvoicesPage({ activeStatus, invoices, onStatusChange }: Props) {
  const filtered = filterInvoices(invoices, activeStatus);
  return (
    <main>
      <section className="panel">
        <p>Invoices</p>
        <h1>Starter invoice list</h1>
        <label>
          Status
          <select
            aria-label="Invoice status filter"
            value={activeStatus}
            onChange={(event) => onStatusChange(event.target.value)}
          >
            <option value="all">All</option>
            <option value="due">Due</option>
            <option value="overdue">Overdue</option>
          </select>
        </label>
      </section>
      <section className="panel">
        <ul>
          {filtered.map((invoice) => (
            <li key={invoice.id}>
              {invoice.customer} - {invoice.status} - ${invoice.amount}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
