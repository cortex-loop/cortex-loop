import { Navigate, Route, Routes } from "react-router-dom";
import { useState } from "react";

import { AppNav } from "./components/AppNav";
import { invoices, plans } from "./data/plans";
import { BillingPage } from "./routes/BillingPage";
import { InvoicesPage } from "./routes/InvoicesPage";
import { PlanComparePage } from "./routes/PlanComparePage";

export default function App() {
  const [activeStatus, setActiveStatus] = useState("all");
  return (
    <>
      <AppNav />
      <Routes>
        <Route path="/" element={<BillingPage invoices={invoices} plans={plans} />} />
        <Route path="/compare" element={<PlanComparePage plans={plans} />} />
        <Route
          path="/invoices"
          element={
            <InvoicesPage
              activeStatus={activeStatus}
              invoices={invoices}
              onStatusChange={setActiveStatus}
            />
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
