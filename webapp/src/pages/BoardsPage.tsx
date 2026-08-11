import { FolderKanban, Image, Plus, Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet, apiPost } from "../lib/api";

interface Board {
  board_id: string;
  board_name: string;
  created_at?: string;
}

export default function BoardsPage() {
  const [boards, setBoards] = useState<Board[]>([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [notice, setNotice] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await apiGet<{ boards: Board[] }>("/invokeai/boards");
      setBoards(data.boards ?? []);
    } catch {
      setBoards([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const create = async () => {
    if (!name.trim()) return;
    const res = await apiPost<{ success: boolean; message?: string }>(
      "/invokeai/boards",
      {
        operation: "create",
        board_name: name.trim(),
      },
    );
    setNotice(res.message ?? "");
    setName("");
    void load();
  };

  const remove = async (boardId: string) => {
    await apiPost<{ success: boolean }>("/invokeai/boards", {
      operation: "delete",
      board_id: boardId,
    });
    void load();
  };

  return (
    <div className="mx-auto max-w-4xl p-6" data-testid="boards-page">
      <PageHeader
        title="Boards"
        subtitle="Organize generated images into collections"
      />
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}

      <div className="mb-5 flex gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && create()}
          placeholder="New board name"
          className="flex-1 rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-amber-500/60"
          data-testid="board-name"
        />
        <button
          onClick={create}
          disabled={!name.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-40"
          data-testid="board-create"
        >
          <Plus className="h-4 w-4" /> Create
        </button>
      </div>

      {loading && <Spinner />}
      {!loading && boards.length === 0 && (
        <EmptyState
          icon={<FolderKanban className="h-8 w-8" />}
          title="No boards"
          hint="Create your first board to organize images."
        />
      )}
      <div className="grid gap-3 md:grid-cols-2">
        {boards.map((b) => (
          <div
            key={b.board_id}
            className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/60 p-4"
            data-testid="board-row"
          >
            <div className="flex items-center gap-3">
              <Image className="h-5 w-5 text-amber-400/70" />
              <div>
                <div className="text-sm font-medium text-slate-200">
                  {b.board_name}
                </div>
                <code className="text-[11px] text-slate-500">{b.board_id}</code>
              </div>
            </div>
            <button
              onClick={() => remove(b.board_id)}
              className="text-slate-500 hover:text-red-400"
              title="Delete board"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
