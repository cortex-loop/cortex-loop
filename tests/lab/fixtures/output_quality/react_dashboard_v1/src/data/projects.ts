export type ProjectStatus = "on-track" | "at-risk" | "done";

export type Project = {
  slug: string;
  name: string;
  owner: string;
  status: ProjectStatus;
  summary: string;
  nextStep: string;
};

export const initialProjects: Project[] = [
  {
    slug: "atlas",
    name: "Atlas rollout",
    owner: "Mika",
    status: "at-risk",
    summary: "Tighten the launch checklist and unblock the migration review.",
    nextStep: "Confirm the rollback window.",
  },
  {
    slug: "marble",
    name: "Marble pricing update",
    owner: "Sam",
    status: "on-track",
    summary: "Prep the staged rollout and confirm all customer-facing copy.",
    nextStep: "Review billing screenshots.",
  },
  {
    slug: "signal",
    name: "Signal dashboard",
    owner: "Rae",
    status: "done",
    summary: "Ship the refreshed reporting view with the new summary cards.",
    nextStep: "Collect launch feedback.",
  },
];

export function filterProjects(projects: Project[], status: string): Project[] {
  if (status === "all") {
    return projects;
  }
  return projects;
}

export function getProjectBySlug(projects: Project[], slug: string): Project | undefined {
  return projects.find((project) => project.slug === slug);
}

export function updateProjectStatus(
  projects: Project[],
  slug: string,
  status: ProjectStatus,
): Project[] {
  return projects;
}
