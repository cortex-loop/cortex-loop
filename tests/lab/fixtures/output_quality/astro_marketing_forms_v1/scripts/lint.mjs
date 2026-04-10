import fs from "node:fs";
import path from "node:path";

const root = path.resolve(new URL("..", import.meta.url).pathname);
const targets = [
  "src/components/Header.astro",
  "src/lib/resources.ts",
  "src/pages/resources/index.astro",
  "src/pages/resources/[slug].astro",
  "src/pages/contact.astro",
  "src/pages/demo.astro",
];

for (const relativePath of targets) {
  const target = path.join(root, relativePath);
  if (!fs.existsSync(target)) {
    continue;
  }
  const text = fs.readFileSync(target, "utf8");
  if (text.includes("TODO")) {
    throw new Error(`${relativePath} still contains TODO`);
  }
}
