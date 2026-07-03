import { BrowserRouter, Routes, Route } from "react-router-dom";
import SyncStatus from "@/components/SyncStatus";
import TabBar from "@/components/TabBar";
import EliminationPhase from "@/pages/EliminationPhase";
import GroupPhase from "@/pages/GroupPhase";

export default function App() {
  return (
    <BrowserRouter>
      <header className="app-header">
        <h1>World Cup 2026</h1>
        <SyncStatus />
      </header>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<GroupPhase />} />
          <Route path="/bracket" element={<EliminationPhase />} />
        </Routes>
      </main>
      <TabBar />
    </BrowserRouter>
  );
}
