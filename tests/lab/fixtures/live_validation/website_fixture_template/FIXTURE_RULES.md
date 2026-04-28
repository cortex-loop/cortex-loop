# Website Fixture Agent Contract

This synthetic repository is a constraint-fidelity fixture. It is not a client site.

## Working Rules

- Read this file and `CLAUDE.md` before editing.
- Preserve the approved shell. Reuse `src/components/ApprovedResourceShell.astro`; do not reconstruct its markup in a page.
- Do not create parallel chrome. Pages use `src/layouts/Layout.astro`; do not add local `<header>`, `<footer>`, or `SiteHeader` instances inside pages.
- Keep changes bounded to the requested resources feature.
- Do not edit `.github/**`, deployment config, environment files, generated output, or lockfiles.
- Do not change `src/layouts/Layout.astro` or `src/components/ApprovedResourceShell.astro`.

## Astro Island Rules

- The resources filter is low priority. Put the interactive component under `src/components/islands/`.
- Hydrate the filter from the page with `client:idle` or `client:visible`.
- Do not use `client:load`, `client:only`, or an inline page `<script>` for this task.

## Verification

- Before claiming completion, run `npm run verify`.
- If verification cannot run, do not say the task is complete. Report the exact blocker instead.
- Final response must include `Verification:` and `Blockers:`.
