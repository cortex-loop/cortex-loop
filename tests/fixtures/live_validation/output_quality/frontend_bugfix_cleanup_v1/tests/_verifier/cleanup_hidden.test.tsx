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

describe("billing hidden checks", () => {
  it("keeps overdue invoices isolated from the due filter", () => {
    renderApp("/invoices");

    fireEvent.change(screen.getByLabelText(/invoice status filter/i), {
      target: { value: "overdue" },
    });

    expect(screen.getByText(/Orbit - overdue/i)).toBeInTheDocument();
    expect(screen.queryByText(/Acme - due/i)).not.toBeInTheDocument();
  });

  it("reports the due invoice total without paid invoices included", () => {
    renderApp("/");

    expect(screen.getByText(/Due invoices total: \$498/)).toBeInTheDocument();
  });
});
