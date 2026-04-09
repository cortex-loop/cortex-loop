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

describe("inbox feature extension", () => {
  it("renders a useful saved views page", () => {
    renderApp("/views");

    expect(screen.getByRole("heading", { name: /saved views/i })).toBeInTheDocument();
    expect(screen.getByText(/needs follow-up/i)).toBeInTheDocument();
  });

  it("keeps the thread detail route working", () => {
    renderApp("/threads/acme-renewal");

    expect(screen.getByRole("heading", { name: /renewal questions/i })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("link", { name: /back to inbox/i }));
    expect(screen.getByRole("heading", { name: /conversations/i })).toBeInTheDocument();
  });
});
