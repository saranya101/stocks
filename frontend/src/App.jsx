import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

import Dashboard from "./pages/Dashboard";
import ResearchLab from "./pages/ResearchLab";
import PortfolioBacktest from "./pages/PortfolioBacktest";
import Settings from "./pages/Settings";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />

        <main className="main">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/research" element={<ResearchLab />} />
            <Route path="/portfolio" element={<PortfolioBacktest />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;