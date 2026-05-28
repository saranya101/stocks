import { Link } from "react-router-dom";

function Navbar() {
  return (
    <aside className="sidebar">
      <div className="logo">QuantOS</div>

      <Link className="nav-link" to="/">Command Center</Link>
      <Link className="nav-link" to="/research">Research Lab</Link>
      <Link className="nav-link" to="/portfolio">Portfolio</Link>
      <Link className="nav-link" to="/settings">Settings</Link>
    </aside>
  );
}

export default Navbar;