import { NavLink } from "react-router-dom";

function Navbar() {
  return (
    <aside className="sidebar">
      <div className="logo">QuantOS</div>

      <NavLink className="nav-link" to="/">
        Dashboard
      </NavLink>

      <NavLink className="nav-link" to="/backtesting">
        Backtesting
      </NavLink>

      <NavLink to="/approval-queue">Approval Queue</NavLink>

      <NavLink className="nav-link" to="/execution">
        Execution Centre
      </NavLink>

      <NavLink className="nav-link" to="/portfolio">
        Portfolio
      </NavLink>

      <NavLink className="nav-link" to="/settings">
        Settings
      </NavLink>
    </aside>
  );
}

export default Navbar;
