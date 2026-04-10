Add a docs section to the provided Astro starter.

Please implement it in a clean, maintainable way that fits the existing project. Follow normal Astro best practices, keep the structure stable, and make sure there are no obvious broken routes or navigation issues. Keep the implementation reasonably minimal rather than over-engineered.

What to add:
- a docs index page
- nested docs pages under `/docs/<section>/<slug>/`
- tag pages under `/tags/<tag>/`
- a simple docs search experience on the docs index page
- shared navigation that makes the docs section feel like part of the site

Constraints:
- keep changes within these files:
  - `src/components/Header.astro`
  - `src/lib/docs.ts`
  - `src/pages/docs/index.astro`
  - `src/pages/docs/[section]/[slug].astro`
  - `src/pages/tags/[tag].astro`
- the site should build and pass the provided checks
- additional verifier-only checks may run

Visible check command:
- `npm run test:visible`
