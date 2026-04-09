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

const resourcesIndex = requireFile("resources/index.html");
if (!resourcesIndex.includes("Growth Reporting Kit")) {
  throw new Error("resources index did not render the expected resource cards");
}

const contactPage = requireFile("contact/index.html");
if (!contactPage.includes("Contact your team")) {
  throw new Error("contact page heading is missing");
}
if (!contactPage.includes("label")) {
  throw new Error("contact page did not render form labels");
}

const demoPage = requireFile("demo/index.html");
if (!demoPage.includes("Book a demo")) {
  throw new Error("demo page heading is missing");
}
