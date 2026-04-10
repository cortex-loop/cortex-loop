import fs from "node:fs";
import path from "node:path";

const root = path.resolve(new URL("..", import.meta.url).pathname);
const distRoot = path.join(root, "dist");

function requireFile(relativePath) {
  const target = path.join(distRoot, relativePath);
  if (!fs.existsSync(target)) {
    throw new Error(`missing built file: ${relativePath}`);
  }
  return fs.readFileSync(target, "utf8");
}

const docsIndex = requireFile("docs/index.html");
if (!docsIndex.includes("Search docs")) {
  throw new Error("docs index is missing the docs search UI");
}
if (!docsIndex.includes("Launch Checklist")) {
  throw new Error("docs index did not render the launch checklist entry");
}

const guidePage = requireFile("docs/guides/launch-checklist/index.html");
if (!guidePage.includes("Launch Checklist")) {
  throw new Error("guide page did not render the launch checklist title");
}
if (!guidePage.includes("release")) {
  throw new Error("guide page did not render tags");
}
