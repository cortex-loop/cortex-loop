import { Link } from "react-router-dom";

export function AppNav() {
  return (
    <header className="nav">
      <strong>Signal Desk</strong>
      <Link to="/">Overview</Link>
      <Link to="/projects">Projects</Link>
      <Link to="/team">Team</Link>
    </header>
  );
}
