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

describe("inbox hidden checks", () => {
  it("filters the inbox to the needs-follow-up queue", () => {
    renderApp("/views");

    fireEvent.click(screen.getByRole("link", { name: /needs follow-up/i }));
    expect(screen.getByText("Acme")).toBeInTheDocument();
    expect(screen.queryByText("Orbit")).not.toBeInTheDocument();
  });

  it("keeps the saved-views navigation integrated with the inbox layout", () => {
    renderApp("/views");

    expect(screen.getByRole("link", { name: /inbox/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /saved views/i })).toBeInTheDocument();
  });
});
