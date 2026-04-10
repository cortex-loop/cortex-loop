import { Link } from "react-router-dom";

export function AppNav() {
  return (
    <header className="nav">
      <strong>Ledger Billing</strong>
      <Link to="/">Billing</Link>
      <Link to="/compare">Compare plans</Link>
      <Link to="/invoices">Invoices</Link>
    </header>
  );
}
