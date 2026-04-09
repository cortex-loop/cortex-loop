export type ResourceEntry = {
  slug: string;
  title: string;
  category: string;
  summary: string;
  bullets: string[];
};

export const resources: ResourceEntry[] = [
  {
    slug: "launch-qa-brief",
    title: "Launch QA Brief",
    category: "Checklist",
    summary: "A compact brief for launch-week QA coordination and sign-off.",
    bullets: [
      "List product-critical flows and define who signs them off.",
      "Keep regressions visible in one shared checklist.",
      "Write down rollback contacts before launch day.",
    ],
  },
  {
    slug: "growth-reporting-kit",
    title: "Growth Reporting Kit",
    category: "Guide",
    summary: "A practical starter for campaign reporting and team handoff.",
    bullets: [
      "Use one scorecard for both weekly and monthly reviews.",
      "Make every metric answer a team decision.",
      "Document where every number comes from.",
    ],
  },
];

export function getResources(): ResourceEntry[] {
  return resources;
}

export function findResource(slug: string): ResourceEntry | undefined {
  return resources.find((entry) => entry.slug === slug);
}
