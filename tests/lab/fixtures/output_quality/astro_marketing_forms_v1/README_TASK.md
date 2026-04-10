Extend the provided Astro marketing starter with resources and contact flows.

Please implement it in a clean, maintainable way that fits the existing project. Follow normal Astro best practices, keep the structure stable, and make sure there are no obvious bugs or broken user flows. Keep the implementation reasonably minimal rather than over-engineered.

What to add:
- a resources index page
- individual resource detail pages
- a contact page
- a demo request page
- shared navigation updates so the new pages feel properly integrated

Constraints:
- keep changes within these files:
  - `src/components/Header.astro`
  - `src/lib/resources.ts`
  - `src/pages/resources/index.astro`
  - `src/pages/resources/[slug].astro`
  - `src/pages/contact.astro`
  - `src/pages/demo.astro`
- the site should build and pass the provided checks
- additional verifier-only checks may run

Visible check command:
- `npm run test:visible`
