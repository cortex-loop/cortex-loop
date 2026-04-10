import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import App from "../../src/App";

function renderApp(pathname: string) {
  window.history.pushState({}, "", pathname);
  return render(
    <MemoryRouter initialEntries={[pathname]}>
      <App />
    </MemoryRouter>,
  );
}

describe("dashboard hidden checks", () => {
  it("updates the overview summary when a project is marked complete", () => {
    renderApp("/projects/atlas");

    fireEvent.click(screen.getByRole("button", { name: /mark complete/i }));
    fireEvent.click(screen.getByRole("link", { name: /overview/i }));

    expect(screen.getByText("Done: 2")).toBeInTheDocument();
    expect(screen.getByText("At risk: 0")).toBeInTheDocument();
  });

  it("keeps the projects route reachable from the detail page", () => {
    renderApp("/projects/atlas");

    fireEvent.click(screen.getByRole("link", { name: /back to projects/i }));
    expect(screen.getByRole("heading", { name: /projects/i })).toBeInTheDocument();
  });
});
