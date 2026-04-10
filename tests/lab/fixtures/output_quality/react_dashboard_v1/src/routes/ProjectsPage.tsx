import type { Project } from "../data/projects";

type Props = {
  projects: Project[];
  activeFilter: string;
  onFilterChange: (value: string) => void;
};

export function ProjectsPage({ projects, activeFilter, onFilterChange }: Props) {
  return (
    <main className="shell">
      <section className="panel stack">
        <div>
          <p>Projects</p>
          <h1>Starter projects list</h1>
        </div>
        <label>
          Filter
          <select
            aria-label="Status filter"
            value={activeFilter}
            onChange={(event) => onFilterChange(event.target.value)}
          >
            <option value="all">All</option>
            <option value="on-track">On track</option>
            <option value="at-risk">At risk</option>
            <option value="done">Done</option>
          </select>
        </label>
      </section>
      <section className="stack">
        {projects.map((project) => (
          <article className="panel stack" key={project.slug}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem" }}>
              <div>
                <h2>{project.name}</h2>
                <p>{project.summary}</p>
              </div>
              <span className="badge">{project.status}</span>
            </div>
            <small>Owner: {project.owner}</small>
          </article>
        ))}
      </section>
    </main>
  );
}
