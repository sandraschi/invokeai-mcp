import { Download, Image, Search, Star, Trash2 } from "lucide-react";
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
  url: string;
  thumbnail_url: string;
  width?: number;
  height?: number;
  starred?: boolean;
}

export default function GalleryPage() {
  const configured = useHealthStore((s) => s.configured);
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<GalleryImage | null>(null);

  const load = useCallback(async (q = "") => {
    setLoading(true);
    try {
      const data = await apiGet<{ images: GalleryImage[] }>(
        `/invokeai/gallery?limit=60${q ? `&query=${encodeURIComponent(q)}` : ""}`,
      );
      setImages(data.images ?? []);
    } catch {
      setImages([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const action = async (op: string, imageName?: string) => {
    const res = await apiPost<{ success: boolean }>("/invokeai/gallery", {
      operation: op,
      image_name: imageName ?? selected?.image_name,
    });
    if (res.success) void load(query);
  };

  const mock = configured === false;
  const shown: GalleryImage[] = mock
    ? (MOCK.gallery as unknown as GalleryImage[])
    : images;

  return (
    <div className="mx-auto max-w-7xl p-6" data-testid="gallery-page">
      <PageHeader
        title="Gallery"
        subtitle="Everything the engine has produced, searchable by prompt"
      />
      {mock && <MockBanner />}
      <div className="mb-4 flex items-center gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && load(query)}
            placeholder="Search prompts..."
            className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-amber-500/60"
            data-testid="gallery-search"
          />
        </div>
      </div>
      {loading && <Spinner />}
      {!loading && shown.length === 0 && (
        <EmptyState
          icon={<Image className="h-8 w-8" />}
          title="No images"
          hint="Generate images or connect InvokeAI."
        />
      )}
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4 lg:grid-cols-6">
        {shown.map((img) => (
          <div
            key={img.image_name}
            className="group relative overflow-hidden rounded-lg border border-slate-800"
            data-testid="gallery-image"
          >
            {img.url ? (
              <img
                src={img.thumbnail_url || img.url}
                alt={img.image_name}
                loading="lazy"
                onClick={() => setSelected(img)}
                className="aspect-square w-full cursor-pointer object-cover transition group-hover:scale-105"
              />
            ) : (
              <div className="flex aspect-square w-full items-center justify-center bg-slate-900 text-slate-700">
                <Image className="h-8 w-8" />
              </div>
            )}
            {mock && (
              <div className="absolute right-1 top-1">
                <MockBadge />
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
        ))}
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
              src={selected.url}
              alt={selected.image_name}
              className="max-h-[80vh] w-full object-contain"
            />
            <div className="flex items-center justify-between bg-slate-900 px-4 py-3">
              <code className="text-xs text-slate-400">
                {selected.image_name}
              </code>
              <button
                onClick={() => action("download")}
                className="flex items-center gap-1 rounded bg-amber-500 px-3 py-1.5 text-xs font-semibold text-slate-950"
              >
                <Download className="h-3.5 w-3.5" /> Download
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
