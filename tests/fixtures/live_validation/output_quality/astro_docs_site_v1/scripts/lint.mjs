import fs from "node:fs";
import path from "node:path";

const root = new URL("..", import.meta.url);
const targets = [
  "src/components/Header.astro",
  "src/lib/docs.ts",
  "src/pages/docs/index.astro",
  "src/pages/docs/[section]/[slug].astro",
  "src/pages/tags/[tag].astro",
].map((relativePath) => new URL(relativePath, root));

const violations = [];
for (const target of targets) {
  if (!fs.existsSync(target)) {
    continue;
  }
  const text = fs.readFileSync(target, "utf8");
  if (text.includes("TODO")) {
    violations.push(`${path.relative(new URL("..", import.meta.url).pathname, target.pathname)} still contains TODO`);
  }
}

if (violations.length > 0) {
  console.error(violations.join("\n"));
  process.exit(1);
}
