import { BrowserRouter, Navigate, Routes, Route } from "react-router-dom";
import SyncStatus from "@/components/SyncStatus";
import TabBar from "@/components/TabBar";
import TimezonePicker from "@/components/TimezonePicker";
import CupNumbers from "@/pages/CupNumbers";
import EliminationPhase from "@/pages/EliminationPhase";
import GroupPhase from "@/pages/GroupPhase";
import MyTeam from "@/pages/MyTeam";
import { TimeZoneProvider } from "@/lib/timezone";

export default function App() {
  return (
    <TimeZoneProvider>
      <BrowserRouter>
        <header className="app-header">
          <h1>World Cup 2026</h1>
          <div className="app-header-right">
            <SyncStatus />
            <TimezonePicker />
          </div>
        </header>
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Navigate to="/bracket" replace />} />
            <Route path="/groups" element={<GroupPhase />} />
            <Route path="/bracket" element={<EliminationPhase />} />
            <Route path="/team" element={<MyTeam />} />
            <Route path="/numbers" element={<CupNumbers />} />
          </Routes>
        </main>
        <TabBar />
        <footer className="app-footer">
          Based on the graph by Emilio Sansolini{" "}
          <a
            href="https://www.instagram.com/emiliosansolini"
            target="_blank"
            rel="noopener noreferrer"
          >
            @emiliosansolini
          </a>
        </footer>
      </BrowserRouter>
    </TimeZoneProvider>
  );
}
