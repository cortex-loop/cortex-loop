Extend the provided React inbox starter with one more real feature.

Please implement it in a clean, maintainable way that fits the existing codebase. Follow normal React best practices, keep the structure stable, and make sure there are no obvious bugs or broken user flows. Keep the implementation reasonably minimal rather than over-engineered.

What to add:
- saved views for the inbox
- a needs-follow-up queue
- navigation that integrates the new view cleanly with the existing inbox and thread detail pages

Constraints:
- keep changes within these files:
  - `src/App.tsx`
  - `src/components/Sidebar.tsx`
  - `src/data/threads.ts`
  - `src/routes/InboxPage.tsx`
  - `src/routes/ThreadDetailPage.tsx`
  - `src/routes/SavedViewsPage.tsx`
- the app should build and pass the provided checks
- additional verifier-only checks may run

Visible check command:
- `npm run test:visible`
