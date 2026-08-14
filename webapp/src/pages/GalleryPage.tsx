import {
  CheckSquare,
  Download,
  Image,
  Search,
  Square,
  Star,
  Trash2,
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import {
  EmptyState,
  MockBadge,
  MockBanner,
  PageHeader,
  Spinner,
} from "../components/ui";
import { apiGet, apiPost } from "../lib/api";
import { MOCK } from "../lib/mockOnboarding";
import { useHealthStore } from "../store/health";

interface GalleryImage {
  image_name: string;
  image_url?: string;
  url?: string;
  thumbnail_url: string;
  width?: number;
  height?: number;
  starred?: boolean;
  board_id?: string | null;
  created_at?: string;
  styles?: string[];
  artists?: string[];
  franchises?: string[];
  display_name?: string;
}

interface Board {
  board_id: string;
  board_name: string;
}

interface GalleryResponse {
  images: GalleryImage[];
  count: number;
  total: number;
  has_more: boolean;
  styles_matched?: string[];
}

const SORTS = [
  { id: "created_at", label: "Newest first" },
  { id: "oldest", label: "Oldest first" },
  { id: "name", label: "Name A-Z" },
  { id: "name_desc", label: "Name Z-A" },
  { id: "starred", label: "Starred first" },
];

export default function GalleryPage() {
  const configured = useHealthStore((s) => s.configured);
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState("created_at");
  const [starredOnly, setStarredOnly] = useState(false);
  const [boardFilter, setBoardFilter] = useState("");
  const [styleFilter, setStyleFilter] = useState("");
  const [boards, setBoards] = useState<Board[]>([]);
  const [styles, setStyles] = useState<{ id: string; name: string }[]>([]);
  const [artists, setArtists] = useState<{ id: string; name: string }[]>([]);
  const [franchises, setFranchises] = useState<{ id: string; name: string }[]>(
    [],
  );
  const [selected, setSelected] = useState<GalleryImage | null>(null);
  const [selectMode, setSelectMode] = useState(false);
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const [batchBusy, setBatchBusy] = useState(false);
  const [notice, setNotice] = useState("");
  const [artistFilter, setArtistFilter] = useState("");
  const [franchiseFilter, setFranchiseFilter] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const qs = new URLSearchParams({ limit: "100", sort });
      if (query) qs.set("query", query);
      if (starredOnly) qs.set("starred", "1");
      if (boardFilter) qs.set("board", boardFilter);
      if (styleFilter) qs.set("style", styleFilter);
      if (artistFilter) qs.set("artist", artistFilter);
      if (franchiseFilter) qs.set("franchise", franchiseFilter);
      const data = await apiGet<GalleryResponse>(`/invokeai/gallery?${qs}`);
      setImages(data.images ?? []);
    } catch {
      setImages([]);
    } finally {
      setLoading(false);
    }
  }, [
    query,
    sort,
    starredOnly,
    boardFilter,
    styleFilter,
    artistFilter,
    franchiseFilter,
  ]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    apiGet<{ boards?: Board[] }>("/invokeai/boards")
      .then((d) => setBoards(d.boards ?? []))
      .catch(() => setBoards([]));
    apiGet<{ styles?: { id: string; name: string }[] }>("/invokeai/styles")
      .then((d) => setStyles(d.styles ?? []))
      .catch(() => setStyles([]));
    apiGet<{ artists?: { id: string; name: string }[] }>("/invokeai/artists")
      .then((d) => setArtists(d.artists ?? []))
      .catch(() => setArtists([]));
    apiGet<{ franchises?: { id: string; name: string }[] }>(
      "/invokeai/franchises",
    )
      .then((d) => setFranchises(d.franchises ?? []))
      .catch(() => setFranchises([]));
  }, []);

  const action = async (op: string, imageName?: string) => {
    const res = await apiPost<{ success: boolean }>("/invokeai/gallery", {
      operation: op,
      image_name: imageName ?? selected?.image_name,
    });
    if (res.success) void load();
  };

  const togglePick = (name: string) => {
    setPicked((prev) => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name);
      else next.add(name);
      return next;
    });
  };

  const pickPage = () => {
    setPicked((prev) => {
      const next = new Set(prev);
      for (const i of images) next.add(i.image_name);
      return next;
    });
  };

  const clearPicks = () => setPicked(new Set());

  const batch = async (op: string, body?: Record<string, unknown>) => {
    if (picked.size === 0) return;
    setBatchBusy(true);
    setNotice("");
    try {
      if (op === "zip") {
        const r = await fetch("/api/invokeai/gallery/zip", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_names: [...picked] }),
        });
        if (r.ok) {
          const blob = await r.blob();
          const a = document.createElement("a");
          a.href = URL.createObjectURL(blob);
          a.download = `invokeai-${picked.size}.zip`;
          a.click();
          URL.revokeObjectURL(a.href);
          setNotice(`Exported ${picked.size} images.`);
        } else {
          setNotice("Zip export failed.");
        }
      } else {
        const res = await apiPost<{ success: boolean; error?: string }>(
          "/invokeai/gallery/batch",
          { operation: op, image_names: [...picked], ...(body ?? {}) },
        );
        setNotice(
          res.success
            ? `${op} on ${picked.size} images.`
            : (res.error ?? "Batch failed."),
        );
        if (res.success) {
          clearPicks();
          void load();
        }
      }
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "batch failed");
    } finally {
      setBatchBusy(false);
    }
  };

  const moveToBoard = async (boardId: string) => {
    if (!boardId) return;
    setBatchBusy(true);
    try {
      const res = await apiPost<{ success: boolean; error?: string }>(
        "/invokeai/gallery/board",
        { image_names: [...picked], board_id: boardId },
      );
      setNotice(
        res.success
          ? `Moved ${picked.size} images to board.`
          : (res.error ?? "Move failed."),
      );
      if (res.success) {
        clearPicks();
        void load();
      }
    } catch (e) {
      setNotice(e instanceof Error ? e.message : "move failed");
    } finally {
      setBatchBusy(false);
    }
  };

  const mock = configured === false;
  const shown: GalleryImage[] = mock
    ? (MOCK.gallery as unknown as GalleryImage[])
    : images;

  return (
    <div className="mx-auto max-w-7xl p-6" data-testid="gallery-page">
      <PageHeader
        title="Gallery"
        subtitle="Everything the engine has produced - sort, filter, batch"
      />
      {mock && <MockBanner />}
      {notice && <p className="mb-3 text-xs text-emerald-300">{notice}</p>}

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <div className="relative flex-1 min-w-52 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load()}
            placeholder="Search prompts..."
            className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-amber-500/60"
            data-testid="gallery-search"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-xs text-slate-200 outline-none"
          title="Sort"
          data-testid="gallery-sort"
        >
          {SORTS.map((s) => (
            <option key={s.id} value={s.id}>
              {s.label}
            </option>
          ))}
        </select>
        <button
          onClick={() => setStarredOnly((v) => !v)}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs ${
            starredOnly
              ? "border-amber-500/60 bg-amber-500/10 text-amber-300"
              : "border-slate-700 bg-slate-900 text-slate-300"
          }`}
          title="Starred only"
        >
          <Star
            className={`h-3.5 w-3.5 ${starredOnly ? "fill-amber-300" : ""}`}
          />
          Starred
        </button>
        <select
          value={boardFilter}
          onChange={(e) => setBoardFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-xs text-slate-200 outline-none"
          title="Board"
          data-testid="gallery-board-filter"
        >
          <option value="">All boards</option>
          {boards.map((b) => (
            <option key={b.board_id} value={b.board_id}>
              {b.board_name}
            </option>
          ))}
        </select>
        <select
          value={styleFilter}
          onChange={(e) => setStyleFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-xs text-slate-200 outline-none"
          title="Style"
          data-testid="gallery-style-filter"
        >
          <option value="">All styles</option>
          {styles.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
        <select
          value={artistFilter}
          onChange={(e) => setArtistFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-xs text-slate-200 outline-none"
          title="Painter"
          data-testid="gallery-artist-filter"
        >
          <option value="">All painters</option>
          {artists.map((a) => (
            <option key={a.id} value={a.id}>
              {a.name}
            </option>
          ))}
        </select>
        <select
          value={franchiseFilter}
          onChange={(e) => setFranchiseFilter(e.target.value)}
          className="rounded-lg border border-slate-700 bg-slate-900 px-2 py-2 text-xs text-slate-200 outline-none"
          title="Franchise"
          data-testid="gallery-franchise-filter"
        >
          <option value="">All franchises</option>
          {franchises.map((f) => (
            <option key={f.id} value={f.id}>
              {f.name}
            </option>
          ))}
        </select>
        <button
          onClick={() => {
            setSelectMode((v) => {
              if (v) clearPicks();
              return !v;
            });
          }}
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs ${
            selectMode
              ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300"
              : "border-slate-700 bg-slate-900 text-slate-300"
          }`}
          title="Select multiple for batch actions"
          data-testid="gallery-select-mode"
        >
          {selectMode ? (
            <CheckSquare className="h-3.5 w-3.5" />
          ) : (
            <Square className="h-3.5 w-3.5" />
          )}
          {selectMode ? "Done" : "Select"}
        </button>
      </div>

      {selectMode && !mock && (
        <div
          className="mb-4 flex flex-wrap items-center gap-2 rounded-lg border border-emerald-500/40 bg-emerald-500/5 px-3 py-2"
          data-testid="gallery-batch-bar"
        >
          <span className="text-xs font-medium text-emerald-200">
            {picked.size} selected
          </span>
          <button
            onClick={pickPage}
            className="rounded border border-slate-600 px-2 py-1 text-[11px] text-slate-300 hover:text-white"
          >
            Select page
          </button>
          <button
            onClick={clearPicks}
            className="rounded border border-slate-600 px-2 py-1 text-[11px] text-slate-300 hover:text-white"
          >
            Clear
          </button>
          <span className="mx-1 h-4 w-px bg-slate-700" />
          <button
            onClick={() => batch("star")}
            disabled={batchBusy || picked.size === 0}
            className="flex items-center gap-1 rounded border border-amber-500/50 px-2 py-1 text-[11px] text-amber-300 hover:bg-amber-500/10 disabled:opacity-40"
          >
            <Star className="h-3 w-3" /> Star
          </button>
          <button
            onClick={() => batch("unstar")}
            disabled={batchBusy || picked.size === 0}
            className="rounded border border-slate-600 px-2 py-1 text-[11px] text-slate-300 hover:text-white disabled:opacity-40"
          >
            Unstar
          </button>
          <button
            onClick={() => batch("zip")}
            disabled={batchBusy || picked.size === 0}
            className="flex items-center gap-1 rounded border border-slate-600 px-2 py-1 text-[11px] text-slate-300 hover:text-white disabled:opacity-40"
          >
            <Download className="h-3 w-3" /> Zip
          </button>
          <select
            value=""
            onChange={(e) => e.target.value && moveToBoard(e.target.value)}
            disabled={batchBusy || picked.size === 0}
            className="rounded border border-slate-600 bg-slate-900 px-2 py-1 text-[11px] text-slate-300 disabled:opacity-40"
            title="Move to board"
          >
            <option value="">Move to board...</option>
            {boards.map((b) => (
              <option key={b.board_id} value={b.board_id}>
                {b.board_name}
              </option>
            ))}
          </select>
          <button
            onClick={() => batch("delete")}
            disabled={batchBusy || picked.size === 0}
            className="flex items-center gap-1 rounded border border-red-500/50 px-2 py-1 text-[11px] text-red-300 hover:bg-red-500/10 disabled:opacity-40"
          >
            <Trash2 className="h-3 w-3" /> Delete
          </button>
        </div>
      )}

      {loading && <Spinner />}
      {!loading && shown.length === 0 && (
        <EmptyState
          icon={<Image className="h-8 w-8" />}
          title="No images"
          hint="Generate images or adjust the filters."
        />
      )}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
        {shown.map((img) => {
          const pickedNow = picked.has(img.image_name);
          return (
            <div
              key={img.image_name}
              className={`group relative overflow-hidden rounded-lg border ${
                pickedNow ? "border-emerald-500/70" : "border-slate-800"
              }`}
              data-testid="gallery-image"
            >
              {selectMode && !mock && (
                <button
                  onClick={() => togglePick(img.image_name)}
                  className="absolute left-1.5 top-1.5 z-10 rounded bg-slate-950/80 p-1 text-emerald-300"
                  title="Toggle selection"
                >
                  {pickedNow ? (
                    <CheckSquare className="h-4 w-4" />
                  ) : (
                    <Square className="h-4 w-4" />
                  )}
                </button>
              )}
              {img.image_url || img.url ? (
                <img
                  src={img.thumbnail_url || img.image_url || img.url}
                  alt={img.image_name}
                  loading="lazy"
                  onClick={() => !selectMode && setSelected(img)}
                  className="aspect-square w-full cursor-pointer object-cover transition group-hover:scale-105"
                />
              ) : (
                <div className="flex aspect-square w-full items-center justify-center bg-slate-900 text-slate-400">
                  <Image className="h-8 w-8" />
                </div>
              )}
              {mock && (
                <div className="absolute right-1 top-1">
                  <MockBadge />
                </div>
              )}
              {!mock && img.styles && img.styles.length > 0 && (
                <div className="absolute right-1.5 top-1.5 flex max-w-[80%] flex-col items-end gap-0.5">
                  {img.styles.slice(0, 3).map((s) => (
                    <span
                      key={s}
                      className="rounded bg-slate-950/80 px-1.5 py-0.5 text-[9px] uppercase tracking-wide text-amber-300"
                      title="Generated with this style"
                    >
                      {s}
                    </span>
                  ))}
                  {img.styles.length > 3 && (
                    <span className="rounded bg-slate-950/80 px-1.5 py-0.5 text-[9px] text-slate-400">
                      +{img.styles.length - 3}
                    </span>
                  )}
                </div>
              )}
              {!mock && img.artists && img.artists.length > 0 && (
                <div className="absolute left-1.5 top-1.5 flex max-w-[80%] flex-col items-start gap-0.5">
                  {img.artists.slice(0, 2).map((a) => (
                    <span
                      key={a}
                      className="rounded bg-slate-950/80 px-1.5 py-0.5 text-[9px] uppercase tracking-wide text-sky-300"
                      title="Generated in the style of this painter"
                    >
                      {a}
                    </span>
                  ))}
                </div>
              )}
              {!mock && img.franchises && img.franchises.length > 0 && (
                <div className="absolute bottom-1.5 left-1.5 flex max-w-[80%] flex-col items-start gap-0.5">
                  {img.franchises.slice(0, 2).map((f) => (
                    <span
                      key={f}
                      className="rounded bg-slate-950/80 px-1.5 py-0.5 text-[9px] uppercase tracking-wide text-fuchsia-300"
                      title="Generated in this franchise style"
                    >
                      {f}
                    </span>
                  ))}
                </div>
              )}
              {!mock && (
                <div className="absolute inset-x-0 bottom-0 flex items-center justify-between bg-gradient-to-t from-slate-950/90 to-transparent p-2 opacity-0 transition group-hover:opacity-100">
                  <button
                    onClick={() => action("star", img.image_name)}
                    className="text-amber-300 hover:text-amber-200"
                    title="Star"
                  >
                    <Star
                      className={`h-4 w-4 ${img.starred ? "fill-amber-300" : ""}`}
                    />
                  </button>
                  <button
                    onClick={() => action("download", img.image_name)}
                    className="text-slate-300 hover:text-white"
                    title="Download"
                  >
                    <Download className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => action("delete", img.image_name)}
                    className="text-red-400 hover:text-red-300"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {selected && !mock && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/90 p-6"
          onClick={() => setSelected(null)}
        >
          <div
            className="max-h-[90vh] max-w-4xl overflow-hidden rounded-xl border border-slate-700"
            onClick={(e) => e.stopPropagation()}
          >
            <img
              src={selected.image_url || selected.url}
              alt={selected.image_name}
              className="max-h-[80vh] w-full object-contain"
            />
            <div className="flex items-center justify-between bg-slate-900 px-4 py-3">
              <div className="flex min-w-0 items-center gap-2">
                {selected.styles && selected.styles.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {selected.styles.map((s) => (
                      <span
                        key={s}
                        className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-amber-300"
                      >
                        {s}
                      </span>
                    ))}
                  </div>
                )}
                {selected.artists && selected.artists.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {selected.artists.map((a) => (
                      <span
                        key={a}
                        className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-sky-300"
                      >
                        {a}
                      </span>
                    ))}
                  </div>
                )}
                {selected.franchises && selected.franchises.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {selected.franchises.map((f) => (
                      <span
                        key={f}
                        className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] uppercase tracking-wide text-fuchsia-300"
                      >
                        {f}
                      </span>
                    ))}
                  </div>
                )}
                <code
                  className="truncate text-xs text-slate-400"
                  title={selected.image_name}
                >
                  {selected.display_name ?? selected.image_name}
                </code>
              </div>
              <div className="flex items-center gap-2">
                {selected.starred && (
                  <Star className="h-3.5 w-3.5 fill-amber-300 text-amber-300" />
                )}
                <button
                  onClick={() => action("download")}
                  className="flex items-center gap-1 rounded bg-amber-500 px-3 py-1.5 text-xs font-semibold text-slate-950"
                >
                  <Download className="h-3.5 w-3.5" /> Download
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
