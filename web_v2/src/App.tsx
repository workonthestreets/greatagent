import { useEffect, useRef, useState } from "react";
import type { CaseItem, Run, Spec } from "./api";
import { getSpec, listCases } from "./api";
import CasesPage from "./CasesPage";
import Investigate from "./Investigate";

type View = "cases" | "investigate";
const STORE = "greatagent-v2-runs";
export type Runs = Record<string, Run>;

function loadSaved(): Runs {
  try { const s = localStorage.getItem(STORE); return s ? (JSON.parse(s) as Runs) : {}; } catch { return {}; }
}

export default function App() {
  const [view, setView] = useState<View>("cases");
  const [cases, setCases] = useState<CaseItem[] | null>(null);
  const [selected, setSelected] = useState("");
  const [runs, setRuns] = useState<Runs>(loadSaved);
  const [spec, setSpec] = useState<Spec | null>(null);
  const [loadErr, setLoadErr] = useState("");
  const file = useRef<HTMLInputElement>(null);

  useEffect(() => {
    listCases().then((c) => { setCases(c); setSelected((s) => s || c[0]?.id || ""); }).catch((e) => setLoadErr((e as Error).message));
    getSpec().then(setSpec).catch(() => setSpec(null));
  }, []);

  const addRun = (r: Run) => setRuns((prev) => {
    const next = { ...prev, [r.case]: r };
    try { localStorage.setItem(STORE, JSON.stringify(next)); } catch { /* storage unavailable or full */ }
    return next;
  });
  const download = () => {
    const run = runs[selected];
    if (!run) return;
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([JSON.stringify(run, null, 2)], { type: "application/json" }));
    a.download = `${run.case}.json`;
    a.click();
  };
  const open = async (f?: File) => {
    if (!f) return;
    try { const j = JSON.parse(await f.text()); if (j && j.preprocess && "response" in j) { addRun(j as Run); setSelected(j.case); setView("investigate"); } } catch { /* not a run file */ }
  };
  const go = (id: string, to: View) => { setSelected(id); setView(to); };

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Rivet Delivery Desk <span className="pill">v2</span></div>
        <nav className="tabs nav">
          <button className={`tab ${view === "cases" ? "active" : ""}`} onClick={() => setView("cases")}>Cases</button>
          <button className={`tab ${view === "investigate" ? "active" : ""}`} onClick={() => setView("investigate")}>Investigate</button>
        </nav>
        <div className="who">
          <button className="ghost small" disabled={!runs[selected]} onClick={download}>Download run</button>
          <button className="ghost small" onClick={() => file.current?.click()}>Open run…</button>
          <input ref={file} type="file" accept="application/json,.json" hidden onChange={(e) => { open(e.target.files?.[0]); e.target.value = ""; }} />
        </div>
      </header>
      {view === "cases"
        ? <CasesPage cases={cases} loadErr={loadErr} selected={selected} onSelect={setSelected} runs={runs} onRun={addRun} onInvestigate={(id) => go(id, "investigate")} />
        : <Investigate runs={runs} cases={cases} selected={selected} onSelect={setSelected} spec={spec} onBack={() => setView("cases")} />}
    </div>
  );
}
