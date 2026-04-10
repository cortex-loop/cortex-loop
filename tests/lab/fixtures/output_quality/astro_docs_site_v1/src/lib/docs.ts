export type DocEntry = {
  section: string;
  slug: string;
  title: string;
  summary: string;
  tags: string[];
  body: string[];
};

export const docs: DocEntry[] = [
  {
    section: "guides",
    slug: "launch-checklist",
    title: "Launch Checklist",
    summary: "A concise checklist for launch-week fixes and handoffs.",
    tags: ["release", "astro"],
    body: [
      "Write down every irreversible step before launch day.",
      "Assign an owner for rollback, support, and comms coverage.",
      "Keep one small dashboard that answers whether the release is healthy.",
    ],
  },
  {
    section: "guides",
    slug: "incident-handoff",
    title: "Incident Handoff",
    summary: "How to hand an incident to the next engineer without losing context.",
    tags: ["ops", "handoff"],
    body: [
      "Capture the current state in plain language first.",
      "List what changed, what remains unknown, and the safest next move.",
      "Leave links to logs, dashboards, and customer-facing impact notes.",
    ],
  },
  {
    section: "reference",
    slug: "navigation-patterns",
    title: "Navigation Patterns",
    summary: "A reference guide for shared header, section nav, and route naming.",
    tags: ["astro", "ux"],
    body: [
      "Keep the main route tree understandable from file names alone.",
      "Prefer stable labels in navigation over clever wording.",
      "Treat every new section as part of the whole site, not a sidecar.",
    ],
  },
];

export function getAllDocs(): DocEntry[] {
  return docs;
}

export function findDoc(section: string, slug: string): DocEntry | undefined {
  return docs.find((entry) => entry.section === section && entry.slug === slug);
}

export function listTags(): string[] {
  return [];
}

export function docsForTag(_tag: string): DocEntry[] {
  return [];
}

export function searchDocs(_query: string): DocEntry[] {
  return [];
}
