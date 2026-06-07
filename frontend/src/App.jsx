import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";

import CommandCenter from "./pages/CommandCenter";
import Portfolio from "./pages/Portfolio";
import Research from "./pages/Research";
import Settings from "./pages/Settings";
import Backtest from "./pages/Backtest";
import ExecutionCenter from "./pages/ExecutionCenter";
import ApprovalQueue from "./pages/ApprovalQueue";

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />

        <main className="main">
          <Routes>
            <Route path="/" element={<CommandCenter />} />
            <Route path="/execution" element={<ExecutionCenter />} />
            <Route path="/research" element={<Research />} />
            <Route path="/approval-queue" element={<ApprovalQueue />} />
            <Route path="/backtesting" element={<Backtest />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;