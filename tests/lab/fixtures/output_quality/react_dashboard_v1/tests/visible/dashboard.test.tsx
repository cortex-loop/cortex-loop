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

describe("dashboard starter", () => {
  it("filters projects by status on the projects route", () => {
    renderApp("/projects");

    fireEvent.change(screen.getByLabelText(/status filter/i), {
      target: { value: "at-risk" },
    });

    expect(screen.getByText("Atlas rollout")).toBeInTheDocument();
    expect(screen.queryByText("Marble pricing update")).not.toBeInTheDocument();
  });

  it("renders the project detail route", () => {
    renderApp("/projects/atlas");

    expect(
      screen.getByRole("heading", { name: "Atlas rollout" }),
    ).toBeInTheDocument();
    expect(screen.getByText(/rollback window/i)).toBeInTheDocument();
  });
});
