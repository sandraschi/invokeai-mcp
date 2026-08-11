import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import { EmptyState, PageHeader, Spinner } from "../components/ui";
import { apiGet } from "../lib/api";

interface SkillRec {
  name: string;
  uri: string;
}

export default function SkillsPage() {
  const [skills, setSkills] = useState<SkillRec[]>([]);
  const [selected, setSelected] = useState<SkillRec | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await apiGet<{ skills: SkillRec[] }>("/skills");
        setSkills(data.skills ?? []);
        if (data.skills?.length) {
          setSelected(data.skills[0]);
          const detail = await apiGet<{ content: string }>(
            `/skills/${data.skills[0].name}`,
          );
          setContent(detail.content);
        }
      } catch {
        setSkills([]);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const open = async (s: SkillRec) => {
    setSelected(s);
    const detail = await apiGet<{ content: string }>(`/skills/${s.name}`);
    setContent(detail.content);
  };

  return (
    <div className="mx-auto max-w-6xl p-6" data-testid="skills-page">
      <PageHeader
        title="Skills"
        subtitle="SKILL.md guides that teach the agent how to operate this server"
      />
      {loading && <Spinner />}
      {!loading && skills.length === 0 && (
        <EmptyState
          icon={<Sparkles className="h-8 w-8" />}
          title="No skills"
          hint="Skills ship with the server; check backend logs."
        />
      )}
      <div className="grid gap-5 lg:grid-cols-3">
        <div className="space-y-2">
          {skills.map((s) => (
            <button
              key={s.name}
              onClick={() => open(s)}
              className={`w-full rounded-lg border px-4 py-3 text-left text-sm ${
                selected?.name === s.name
                  ? "border-amber-500/60 bg-amber-500/10 text-amber-300"
                  : "border-slate-800 bg-slate-900/60 text-slate-300 hover:bg-slate-800"
              }`}
              data-testid={`skill-${s.name}`}
            >
              {s.name}
            </button>
          ))}
        </div>
        <div
          className="markdown-body rounded-xl border border-slate-800 bg-slate-900/60 p-6 lg:col-span-2"
          data-testid="skill-content"
        >
          <ReactMarkdown>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
