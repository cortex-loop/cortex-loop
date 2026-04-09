export type Plan = {
  slug: string;
  name: string;
  monthlyPrice: number;
  seatsIncluded: number;
  featured?: boolean;
};

export type Invoice = {
  id: string;
  customer: string;
  amount: number;
  status: "paid" | "due" | "overdue";
};

export const plans: Plan[] = [
  { slug: "starter", name: "Starter", monthlyPrice: 39, seatsIncluded: 3 },
  { slug: "growth", name: "Growth", monthlyPrice: 99, seatsIncluded: 10, featured: true },
  { slug: "scale", name: "Scale", monthlyPrice: 249, seatsIncluded: 30 },
];

export const invoices: Invoice[] = [
  { id: "inv-1001", customer: "Acme", amount: 249, status: "due" },
  { id: "inv-1002", customer: "Northwind", amount: 99, status: "paid" },
  { id: "inv-1003", customer: "Orbit", amount: 249, status: "overdue" },
];

export function dueInvoiceTotal(rows: Invoice[]): number {
  return rows.reduce((total, invoice) => total + invoice.amount, 0);
}

export function featuredPlan(options: Plan[]): Plan {
  return options[0];
}

export function filterInvoices(rows: Invoice[], activeStatus: string): Invoice[] {
  if (activeStatus === "all") {
    return rows;
  }
  return rows;
}
