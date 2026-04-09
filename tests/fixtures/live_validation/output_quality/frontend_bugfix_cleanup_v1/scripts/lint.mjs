import fs from "node:fs";
import path from "node:path";

const root = path.resolve(new URL("..", import.meta.url).pathname);
for (const relativePath of [
  "src/App.tsx",
  "src/components/AppNav.tsx",
  "src/data/plans.ts",
  "src/routes/BillingPage.tsx",
  "src/routes/InvoicesPage.tsx",
  "src/routes/PlanComparePage.tsx",
]) {
  const target = path.join(root, relativePath);
  if (!fs.existsSync(target)) {
    continue;
  }
  const text = fs.readFileSync(target, "utf8");
  if (text.includes("TODO")) {
    throw new Error(`${relativePath} still contains TODO`);
  }
}
