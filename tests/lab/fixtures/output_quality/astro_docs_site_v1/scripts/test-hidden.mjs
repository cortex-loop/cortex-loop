import fs from "node:fs";
import path from "node:path";

const root = path.resolve(new URL("..", import.meta.url).pathname);
const distRoot = path.join(root, "dist");

function requireFile(relativePath) {
  const target = path.join(distRoot, relativePath);
  if (!fs.existsSync(target)) {
    throw new Error(`missing hidden-check file: ${relativePath}`);
  }
  return fs.readFileSync(target, "utf8");
}

const tagPage = requireFile("tags/astro/index.html");
if (!tagPage.includes("Navigation Patterns")) {
  throw new Error("astro tag page did not list the expected doc entry");
}
if (!tagPage.includes("Docs")) {
  throw new Error("tag page is missing shared navigation");
}

const docsIndex = requireFile("docs/index.html");
if (!docsIndex.includes("data-doc-search")) {
  throw new Error("docs search dataset marker is missing");
}

for (const relativePath of [
  "src/components/Header.astro",
  "src/lib/docs.ts",
  "src/pages/docs/index.astro",
  "src/pages/docs/[section]/[slug].astro",
  "src/pages/tags/[tag].astro",
]) {
  const text = fs.readFileSync(path.join(root, relativePath), "utf8");
  if (text.includes("fetch(")) {
    throw new Error(`unexpected fetch call in ${relativePath}`);
  }
}
