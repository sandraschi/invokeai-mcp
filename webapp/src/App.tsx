import { useEffect, useRef } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./Layout";
import BoardsPage from "./pages/BoardsPage";
import ChatPage from "./pages/ChatPage";
import DashboardPage from "./pages/DashboardPage";
import GalleryPage from "./pages/GalleryPage";
import GeneratePage from "./pages/GeneratePage";
import HelpPage from "./pages/HelpPage";
import InboxPage from "./pages/InboxPage";
import LogsPage from "./pages/LogsPage";
import ModelsPage from "./pages/ModelsPage";
import PluginsPage from "./pages/PluginsPage";
import QueuePage from "./pages/QueuePage";
import SettingsPage from "./pages/SettingsPage";
import SkillsPage from "./pages/SkillsPage";
import ToolsPage from "./pages/ToolsPage";
import WorkflowsPage from "./pages/WorkflowsPage";
import { useHealthStore } from "./store/health";
import { useLlmStore } from "./store/llm";

export default function App() {
  const checkHealth = useHealthStore((s) => s.check);
  const probe = useLlmStore((s) => s.probe);
  const probed = useRef(false);

  useEffect(() => {
    checkHealth();
    const id = setInterval(checkHealth, 15000);
    return () => clearInterval(id);
  }, [checkHealth]);

  useEffect(() => {
    if (probed.current) return;
    probed.current = true;
    probe();
  }, [probe]);

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Navigate to="/app/dashboard" replace />} />
        <Route path="/app/dashboard" element={<DashboardPage />} />
        <Route path="/app/generate" element={<GeneratePage />} />
        <Route path="/app/gallery" element={<GalleryPage />} />
        <Route path="/app/models" element={<ModelsPage />} />
        <Route path="/app/plugins" element={<PluginsPage />} />
        <Route path="/app/queue" element={<QueuePage />} />
        <Route path="/app/boards" element={<BoardsPage />} />
        <Route path="/app/workflows" element={<WorkflowsPage />} />
        <Route path="/app/inbox" element={<InboxPage />} />
        <Route path="/app/tools" element={<ToolsPage />} />
        <Route path="/app/skills" element={<SkillsPage />} />
        <Route path="/app/chat" element={<ChatPage />} />
        <Route path="/app/settings" element={<SettingsPage />} />
        <Route path="/app/help" element={<HelpPage />} />
        <Route path="/app/logs" element={<LogsPage />} />
      </Route>
    </Routes>
  );
}
