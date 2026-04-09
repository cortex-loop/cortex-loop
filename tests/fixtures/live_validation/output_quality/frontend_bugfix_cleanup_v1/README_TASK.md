Clean up the provided billing UI starter.

Several user-facing issues were reported around the billing summary, plan comparison, and invoice list behavior. Please fix it in a way that feels clean and maintainable, follow normal React best practices, and make sure there are no obvious regressions or broken flows. Keep the implementation reasonably minimal rather than over-engineered.

Constraints:
- keep changes within these files:
  - `src/App.tsx`
  - `src/components/AppNav.tsx`
  - `src/data/plans.ts`
  - `src/routes/BillingPage.tsx`
  - `src/routes/InvoicesPage.tsx`
  - `src/routes/PlanComparePage.tsx`
- the app should build and pass the provided checks
- additional verifier-only checks may run

Visible check command:
- `npm run test:visible`
