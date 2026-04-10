import { Link } from "react-router-dom";

import type { Project, ProjectStatus } from "../data/projects";

type Props = {
  project: Project | undefined;
  onStatusChange: (status: ProjectStatus) => void;
};

export function ProjectDetailPage({ project, onStatusChange }: Props) {
  if (!project) {
    return (
      <main className="shell">
        <section className="panel stack">
          <h1>Project not found</h1>
          <Link to="/projects">Back to projects</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="shell">
      <section className="panel stack">
        <p>Project detail</p>
        <h1>{project.name}</h1>
        <p>{project.summary}</p>
        <p>Owner: {project.owner}</p>
        <p>Next step: {project.nextStep}</p>
        <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
          <span className="badge">{project.status}</span>
          <button type="button" onClick={() => onStatusChange("done")}>
            Mark complete
          </button>
        </div>
        <Link to="/projects">Back to projects</Link>
      </section>
    </main>
  );
}
