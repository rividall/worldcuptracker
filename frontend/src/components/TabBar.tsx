import { NavLink } from "react-router-dom";

export default function TabBar() {
  return (
    <nav className="tab-bar" aria-label="Tournament phases">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Groups
      </NavLink>
      <NavLink to="/bracket" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Bracket
      </NavLink>
    </nav>
  );
}
