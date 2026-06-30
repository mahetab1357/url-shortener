import { Link, Route, Routes } from "react-router-dom";
import { ShortenPage } from "./pages/ShortenPage";
import { DashboardPage } from "./pages/DashboardPage";

export function App() {
  return (
    <div className="app">
      <nav className="nav">
        <Link to="/" className="nav__brand">
          URL Shortener
        </Link>
        <Link to="/dashboard">Dashboard</Link>
      </nav>
      <Routes>
        <Route path="/" element={<ShortenPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </div>
  );
}
