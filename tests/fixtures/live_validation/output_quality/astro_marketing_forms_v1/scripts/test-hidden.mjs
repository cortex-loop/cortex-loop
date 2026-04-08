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

const resourcePage = requireFile("resources/launch-qa-brief/index.html");
if (!resourcePage.includes("Resources")) {
  throw new Error("resource detail page is missing shared navigation");
}

for (const page of ["contact/index.html", "demo/index.html"]) {
  const html = requireFile(page);
  if (!html.includes("type=\"email\"")) {
    throw new Error(`${page} is missing an email field`);
  }
}

const contactPage = requireFile("contact/index.html");
if (!contactPage.includes("Book demo")) {
  throw new Error("contact page navigation is inconsistent");
}

const demoPage = requireFile("demo/index.html");
if (!demoPage.includes("Contact")) {
  throw new Error("demo page navigation is inconsistent");
}
