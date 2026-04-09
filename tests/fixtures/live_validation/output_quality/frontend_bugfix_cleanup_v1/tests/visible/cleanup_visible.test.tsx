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

describe("billing cleanup", () => {
  it("shows only due invoices when the due filter is selected", () => {
    renderApp("/invoices");

    fireEvent.change(screen.getByLabelText(/invoice status filter/i), {
      target: { value: "due" },
    });

    expect(screen.getByText(/Acme - due/i)).toBeInTheDocument();
    expect(screen.queryByText(/Northwind - paid/i)).not.toBeInTheDocument();
  });

  it("shows the featured growth plan in the compare view", () => {
    renderApp("/compare");

    expect(screen.getByText(/Growth/i)).toBeInTheDocument();
    expect(screen.getByText(/Starter/i)).toBeInTheDocument();
  });
});
