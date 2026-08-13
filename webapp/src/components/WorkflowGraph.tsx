import type { Connection } from "@xyflow/react";
import {
  Background,
  Controls,
  Handle,
  MiniMap,
  Position,
  ReactFlow,
  addEdge,
  useEdgesState,
  useNodesState,
} from "@xyflow/react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import "@xyflow/react/dist/style.css";
import { apiPost } from "../lib/api";

type TplInput = {
  kind: string;
  type?: string;
  title?: string;
  description?: string;
  default?: unknown;
  required?: boolean;
  options?: string[] | null;
};

type NodeTpl = {
  title: string;
  category: string;
  description?: string;
  inputs: Record<string, TplInput>;
};

export type { NodeTpl };

type WorkflowGraphProps = {
  workflow: Record<string, unknown>;
  templates: Record<string, NodeTpl>;
  onSaved: (rec: Record<string, unknown> | null, msg: string) => void;
  onError: (msg: string) => void;
};

type FlowNode = {
  id: string;
  type: string;
  position: { x: number; y: number };
  data: { inputs: Record<string, unknown> };
};

type FlowEdge = {
  source: { node_id: string; field: string };
  target: { node_id: string; field: string };
};

const NODE_WIDTH = 240;
void NODE_WIDTH;

function InvokeNode({
  data,
  selected,
}: {
  data: {
    nodeType: string;
    tpl?: NodeTpl;
    inputs: Record<string, unknown>;
    onChange?: (k: string, v: unknown) => void;
  };
  selected: boolean;
}) {
  const tpl = data.tpl;
  const fields = useMemo(
    () =>
      tpl
        ? Object.entries(tpl.inputs).filter(([, f]) => f.kind !== "connection")
        : [],
    [tpl],
  );
  const connections = useMemo(
    () =>
      tpl
        ? Object.entries(tpl.inputs).filter(([, f]) => f.kind === "connection")
        : [],
    [tpl],
  );
  return (
    <div
      className={`w-[240px] rounded-lg border bg-zinc-900 text-xs shadow-lg ${
        selected ? "border-amber-400" : "border-zinc-700"
      }`}
    >
      <div className="border-b border-zinc-700 px-2.5 py-1.5 font-medium text-amber-300">
        {tpl?.title ?? data.nodeType}
      </div>
      <div className="space-y-1.5 px-2.5 py-2">
        {connections.map(([name, f]) => (
          <div
            key={name}
            className="flex items-center justify-between text-slate-400"
          >
            <Handle
              type="target"
              position={Position.Left}
              id={`in:${name}`}
              className="!h-2 !w-2 !border-zinc-500 !bg-slate-300"
            />
            <span className="pl-3">{f.title ?? name}</span>
          </div>
        ))}
        {fields.map(([name, f]) => {
          const value = data.inputs[name];
          const kind = f.kind === "collection" ? "collection" : f.type;
          return (
            <div key={name} className="flex items-center gap-1.5">
              <span
                className="w-20 shrink-0 truncate text-slate-400"
                title={f.title ?? name}
              >
                {f.title ?? name}
              </span>
              {kind === "boolean" ? (
                <input
                  type="checkbox"
                  checked={Boolean(value)}
                  onChange={(e) => data.onChange?.(name, e.target.checked)}
                  className="h-3.5 w-3.5 accent-amber-500"
                />
              ) : f.options?.length ? (
                <select
                  value={String(value ?? "")}
                  onChange={(e) => data.onChange?.(name, e.target.value)}
                  className="flex-1 rounded bg-zinc-800 px-1 py-0.5 text-[11px] text-zinc-100"
                >
                  <option value="" />
                  {f.options.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type="text"
                  value={
                    value === undefined || value === null ? "" : String(value)
                  }
                  onChange={(e) => data.onChange?.(name, e.target.value)}
                  className="flex-1 rounded bg-zinc-800 px-1 py-0.5 text-[11px] text-zinc-100"
                />
              )}
            </div>
          );
        })}
        <Handle
          type="source"
          position={Position.Right}
          id="out:output"
          className="!h-2 !w-2 !border-zinc-500 !bg-amber-400"
        />
      </div>
    </div>
  );
}

const nodeTypes = { invoke: InvokeNode };

export default function WorkflowGraph({
  workflow,
  templates,
  onSaved,
  onError,
}: WorkflowGraphProps) {
  const wf = (workflow.workflow ?? workflow) as {
    nodes?: FlowNode[];
    edges?: FlowEdge[];
  };
  const initialNodes = useMemo(
    () =>
      (wf.nodes ?? []).map((n) => ({
        id: n.id,
        type: "invoke",
        position: n.position ?? { x: 100, y: 100 },
        data: {
          nodeType: n.type,
          tpl: templates[n.type],
          inputs: { ...((n.data?.inputs as Record<string, unknown>) ?? {}) },
        },
      })),
    [wf, templates],
  );
  const initialEdges = useMemo(
    () =>
      (wf.edges ?? []).map((e) => ({
        id: `${e.source.node_id}.${e.source.field}->${e.target.node_id}.${e.target.field}`,
        source: e.source.node_id,
        sourceHandle: `out:${e.source.field}`,
        target: e.target.node_id,
        targetHandle: `in:${e.target.field}`,
      })),
    [wf],
  );
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [paletteQuery, setPaletteQuery] = useState("");
  const [saving, setSaving] = useState(false);
  const paletteRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (paletteOpen) paletteRef.current?.focus();
  }, [paletteOpen]);

  const onConnect = useCallback(
    (conn: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...conn,
            sourceHandle: conn.sourceHandle ?? "out:output",
            targetHandle: conn.targetHandle ?? "in:input",
          },
          eds,
        ),
      );
    },
    [setEdges],
  );

  const changeInput = useCallback(
    (nodeId: string, key: string, value: unknown) => {
      setNodes((nds) =>
        nds.map((n) =>
          n.id === nodeId
            ? {
                ...n,
                data: { ...n.data, inputs: { ...n.data.inputs, [key]: value } },
              }
            : n,
        ),
      );
    },
    [setNodes],
  );

  const paletteItems = useMemo(() => {
    const q = paletteQuery.toLowerCase();
    return Object.entries(templates)
      .filter(
        ([name, t]) =>
          !q ||
          name.toLowerCase().includes(q) ||
          t.title.toLowerCase().includes(q),
      )
      .sort(
        (a, b) =>
          a[1].category.localeCompare(b[1].category) ||
          a[0].localeCompare(b[0]),
      )
      .slice(0, 200);
  }, [templates, paletteQuery]);

  const addNode = useCallback(
    (type: string) => {
      const tpl = templates[type];
      const defaults: Record<string, unknown> = {};
      for (const [name, f] of Object.entries(tpl?.inputs ?? {})) {
        if (
          f.kind !== "connection" &&
          f.default !== undefined &&
          f.default !== null
        ) {
          defaults[name] = f.default;
        }
      }
      const id = `node_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
      setNodes((nds) => [
        ...nds,
        {
          id,
          type: "invoke",
          position: {
            x: 120 + (nds.length % 5) * 40,
            y: 120 + (nds.length % 5) * 40,
          },
          data: { nodeType: type, tpl, inputs: defaults },
        },
      ]);
      setPaletteOpen(false);
    },
    [templates, setNodes],
  );

  const save = useCallback(async () => {
    setSaving(true);
    try {
      const outNodes = nodes.map((n) => ({
        id: n.id,
        type: (n.data as { nodeType: string }).nodeType,
        position: n.position,
        data: {
          id: n.id,
          type: (n.data as { nodeType: string }).nodeType,
          position: n.position,
          inputs: (n.data as { inputs: Record<string, unknown> }).inputs,
        },
      }));
      const outEdges = edges.map((e) => ({
        source: {
          node_id: e.source,
          field: (e.sourceHandle ?? "out:output").replace(/^out:/, ""),
        },
        target: {
          node_id: e.target,
          field: (e.targetHandle ?? "in:input").replace(/^in:/, ""),
        },
      }));
      const inner = (workflow.workflow ?? workflow) as Record<string, unknown>;
      const updated = {
        ...workflow,
        workflow: {
          ...inner,
          nodes: outNodes,
          edges: outEdges,
        },
      };
      const res = await apiPost<{
        success: boolean;
        message?: string;
        data?: Record<string, unknown> | null;
      }>("/invokeai/workflows", {
        operation: "save",
        workflow_id: workflow.workflow_id,
        workflow_json: JSON.stringify(updated),
      });
      if (res.success)
        onSaved(res.data ?? null, res.message ?? "Workflow saved.");
      else onError(res.message ?? "Save failed.");
    } finally {
      setSaving(false);
    }
  }, [nodes, edges, workflow, onSaved, onError]);

  return (
    <div className="relative h-[560px] overflow-hidden rounded-lg border border-zinc-800">
      <ReactFlow
        nodes={nodes.map((n) => ({
          ...n,
          data: {
            ...n.data,
            onChange: (k: string, v: unknown) => changeInput(n.id, k, v),
          },
        }))}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.2}
        colorMode="dark"
      >
        <Background gap={18} color="#27272a" />
        <Controls className="!bg-zinc-900 [&_button]:!border-zinc-700" />
        <MiniMap
          className="!bg-zinc-900"
          nodeColor={(n) => (n.selected ? "#f59e0b" : "#3f3f46")}
          maskColor="rgba(9,9,11,0.7)"
        />
      </ReactFlow>
      <div className="absolute left-3 top-3 z-10 flex gap-2">
        <button
          onClick={() => setPaletteOpen((v) => !v)}
          className="rounded-md border border-amber-500/50 bg-zinc-900/90 px-3 py-1.5 text-xs font-medium text-amber-300 hover:bg-zinc-800"
        >
          + Add node
        </button>
        <button
          onClick={save}
          disabled={saving}
          className="rounded-md border border-emerald-500/50 bg-zinc-900/90 px-3 py-1.5 text-xs font-medium text-emerald-300 hover:bg-zinc-800 disabled:opacity-50"
        >
          {saving ? "Saving..." : "Save workflow"}
        </button>
      </div>
      {paletteOpen && (
        <div className="absolute left-3 top-12 z-10 flex max-h-[380px] w-72 flex-col overflow-hidden rounded-lg border border-zinc-700 bg-zinc-900/95 shadow-xl">
          <input
            ref={paletteRef}
            value={paletteQuery}
            onChange={(e) => setPaletteQuery(e.target.value)}
            placeholder="Search node types..."
            className="border-b border-zinc-700 bg-zinc-900 px-3 py-2 text-xs text-zinc-100 outline-none"
          />
          <div className="flex-1 overflow-y-auto">
            {paletteItems.map(([name, t]) => (
              <button
                key={name}
                onClick={() => addNode(name)}
                className="flex w-full items-baseline justify-between gap-2 px-3 py-1.5 text-left text-[11px] hover:bg-zinc-800"
              >
                <span className="truncate text-zinc-200">{t.title}</span>
                <span className="shrink-0 text-[10px] text-zinc-500">
                  {t.category}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
      <div className="absolute bottom-2 right-3 z-10 text-[10px] text-zinc-500">
        {nodes.length} nodes / {edges.length} edges - drag to connect; engine
        validates on run
      </div>
    </div>
  );
}
