import { BrowserRouter, Routes, Route } from "react-router-dom";
import SyncStatus from "@/components/SyncStatus";
import TabBar from "@/components/TabBar";
import TimezonePicker from "@/components/TimezonePicker";
import EliminationPhase from "@/pages/EliminationPhase";
import GroupPhase from "@/pages/GroupPhase";
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
            <Route path="/" element={<GroupPhase />} />
            <Route path="/bracket" element={<EliminationPhase />} />
          </Routes>
        </main>
        <TabBar />
      </BrowserRouter>
    </TimeZoneProvider>
  );
}
