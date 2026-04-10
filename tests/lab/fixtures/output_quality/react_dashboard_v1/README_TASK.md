Extend the provided React dashboard starter.

Please implement it in a clean, maintainable way that fits the existing codebase. Follow normal React best practices, keep the structure stable, and make sure there are no obvious bugs or broken user flows. Keep the implementation reasonably minimal rather than over-engineered.

What to add:
- a projects area with useful filtering
- project detail routes
- a small mutation flow so a project can be updated from its detail page
- navigation that makes the dashboard feel coherent across overview, projects, and team pages

Constraints:
- keep changes within these files:
  - `src/App.tsx`
  - `src/components/AppNav.tsx`
  - `src/data/projects.ts`
  - `src/routes/ProjectsPage.tsx`
  - `src/routes/ProjectDetailPage.tsx`
  - `src/routes/TeamPage.tsx`
- the app should build and pass the provided checks
- additional verifier-only checks may run

Visible check command:
- `npm run test:visible`
