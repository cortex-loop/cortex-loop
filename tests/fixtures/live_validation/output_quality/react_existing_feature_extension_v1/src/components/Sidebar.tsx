import { Link } from "react-router-dom";

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div>
        <strong>Relay Inbox</strong>
        <p>Customer support starter.</p>
      </div>
      <nav aria-label="Sidebar">
        <div className="stack">
          <Link to="/inbox">Inbox</Link>
          <Link to="/views">Saved views</Link>
        </div>
      </nav>
    </aside>
  );
}
