import { Link, Route, Routes } from "react-router-dom";
import { LayoutDashboard, Link2 } from "lucide-react";
import { ShortenPage } from "./pages/ShortenPage";
import { DashboardPage } from "./pages/DashboardPage";

export function App() {
  return (
    <div className="app">
      <nav className="nav">
        <Link to="/" className="nav__brand">
          <span className="nav__brand-icon">
            <Link2 size={18} strokeWidth={2.5} />
          </span>
          Snip
        </Link>
        <Link to="/dashboard" className="nav__link">
          <LayoutDashboard size={16} />
          Dashboard
        </Link>
      </nav>
      <Routes>
        <Route path="/" element={<ShortenPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}
