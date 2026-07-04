import { NavLink } from "react-router-dom";

export default function TabBar() {
  return (
    <nav className="tab-bar" aria-label="Tournament phases">
      <NavLink to="/groups" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Groups
      </NavLink>
      <NavLink to="/bracket" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Bracket
      </NavLink>
      <NavLink to="/team" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        My Team
      </NavLink>
      <NavLink to="/numbers" className={({ isActive }) => (isActive ? "tab active" : "tab")}>
        Cup Numbers
      </NavLink>
    </nav>
  );
}
