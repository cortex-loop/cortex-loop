import { Navigate, Route, Routes, useParams } from "react-router-dom";
import { useMemo, useState } from "react";

import { AppNav } from "./components/AppNav";
import {
  filterProjects,
  getProjectBySlug,
  initialProjects,
  updateProjectStatus,
  type ProjectStatus,
} from "./data/projects";
import { OverviewPage } from "./routes/OverviewPage";
import { ProjectDetailPage } from "./routes/ProjectDetailPage";
import { ProjectsPage } from "./routes/ProjectsPage";
import { TeamPage } from "./routes/TeamPage";

function ProjectDetailRoute({
  onStatusChange,
  projects,
}: {
  onStatusChange: (slug: string, status: ProjectStatus) => void;
  projects: typeof initialProjects;
}) {
  const { slug = "" } = useParams();
  const project = getProjectBySlug(projects, slug);
  return (
    <ProjectDetailPage
      project={project}
      onStatusChange={(status) => onStatusChange(slug, status)}
    />
  );
}

export default function App() {
  const [projects, setProjects] = useState(initialProjects);
  const [activeFilter, setActiveFilter] = useState("all");
  const filteredProjects = useMemo(
    () => filterProjects(projects, activeFilter),
    [projects, activeFilter],
  );

  return (
    <>
      <AppNav />
      <Routes>
        <Route path="/" element={<OverviewPage projects={projects} />} />
        <Route
          path="/projects"
          element={
            <ProjectsPage
              activeFilter={activeFilter}
              onFilterChange={setActiveFilter}
              projects={filteredProjects}
            />
          }
        />
        <Route
          path="/projects/:slug"
          element={
            <ProjectDetailRoute
              projects={projects}
              onStatusChange={(slug, status) => {
                setProjects((currentProjects) => updateProjectStatus(currentProjects, slug, status));
              }}
            />
          }
        />
        <Route path="/team" element={<TeamPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
