import {
  AppWindow,
  Blocks,
  ChevronLeft,
  ChevronRight,
  FolderKanban,
  HelpCircle,
  Image,
  Images,
  Inbox,
  Layers,
  ListOrdered,
  LogOut,
  MessageSquare,
  Settings,
  Sparkles,
  Terminal,
  Wand2,
  Workflow,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useHealthStore } from "./store/health";

const NAV = [
  { to: "/app/dashboard", label: "Dashboard", icon: AppWindow },
  { to: "/app/generate", label: "Generate", icon: Wand2 },
  { to: "/app/gallery", label: "Gallery", icon: Images },
  { to: "/app/models", label: "Models", icon: Layers },
  { to: "/app/queue", label: "Queue", icon: ListOrdered },
  { to: "/app/boards", label: "Boards", icon: FolderKanban },
  { to: "/app/workflows", label: "Workflows", icon: Workflow },
  { to: "/app/inbox", label: "Inbox", icon: Inbox },
  { to: "/app/tools", label: "Tools", icon: Blocks },
  { to: "/app/skills", label: "Skills", icon: Sparkles },
  { to: "/app/chat", label: "Chat", icon: MessageSquare },
  { to: "/app/settings", label: "Settings", icon: Settings },
  { to: "/app/help", label: "Help", icon: HelpCircle },
  { to: "/app/logs", label: "Logs", icon: Terminal },
];

export default function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const configured = useHealthStore((s) => s.configured);

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100">
      <aside
        className={`flex flex-col border-r border-slate-800 bg-slate-900/60 backdrop-blur transition-all duration-200 ${
          collapsed ? "w-16" : "w-56"
        }`}
        data-testid="sidebar"
      >
        <div className="flex items-center gap-2 px-3 py-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-500/15 text-amber-400">
            <Image className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="min-w-0">
              <div className="truncate text-sm font-bold">InvokeAI MCP</div>
              <div className="text-[11px] text-slate-500">v0.1.0</div>
            </div>
          )}
        </div>
        <button
          onClick={() => setCollapsed((v) => !v)}
          className="mx-2 mb-2 flex items-center justify-center gap-1 rounded-md border border-slate-800 px-2 py-1.5 text-xs text-slate-400 hover:bg-slate-800"
          data-testid="sidebar-collapse"
          title={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
          {!collapsed && "Collapse"}
        </button>
        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2">
          {NAV.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              title={label}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors ${
                  isActive
                    ? "bg-amber-500/15 text-amber-300"
                    : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
                }`
              }
              data-testid={`nav-${label.toLowerCase()}`}
            >
              <Icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span className="truncate">{label}</span>}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-slate-800 p-2">
          <button
            onClick={() => navigate("/app/settings")}
            className="flex w-full items-center gap-2 rounded-md px-2.5 py-2 text-sm text-slate-400 hover:bg-slate-800"
          >
            <LogOut className="h-4 w-4" />
            {!collapsed && <span>Status</span>}
          </button>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-900/50 px-4 backdrop-blur">
          <div className="flex items-center gap-2 text-sm font-medium text-slate-300">
            <Sparkles className="h-4 w-4 text-amber-400" />
            <span data-testid="topbar-title">InvokeAI Creative Engine</span>
          </div>
          <div className="flex items-center gap-3">
            <div
              className={`flex items-center gap-1.5 text-xs ${
                configured === null
                  ? "text-slate-500"
                  : configured
                    ? "text-emerald-400"
                    : "text-red-400"
              }`}
              data-testid="backend-dot"
            >
              <span
                className={`h-2 w-2 rounded-full ${configured === null ? "bg-slate-500" : configured ? "bg-emerald-400" : "bg-red-400"} animate-pulse`}
              />
              {configured === null
                ? "Connecting..."
                : configured
                  ? "InvokeAI connected"
                  : "InvokeAI offline"}
            </div>
          </div>
        </header>
        <main className="min-h-0 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
