import type { Project } from "../data/projects";

type Props = {
  projects: Project[];
};

export function OverviewPage({ projects }: Props) {
  const atRiskCount = projects.filter((project) => project.status === "at-risk").length;
  const doneCount = projects.filter((project) => project.status === "done").length;

  return (
    <main className="shell">
      <section className="panel stack">
        <p>Overview</p>
        <h1>Delivery snapshot</h1>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <span className="badge">At risk: {atRiskCount}</span>
          <span className="badge">Done: {doneCount}</span>
        </div>
      </section>
    </main>
  );
}
