This fixture bank keeps only source-defining task content in the main repo.

Local fixture policy:
- keep `README_TASK.md`, manifests, source files, tests, and scripts
- do not keep generated or vendor state such as `node_modules`, `dist`, or `.astro`
- restore historical heavy payloads only through `internal/archive/manifest.json`
