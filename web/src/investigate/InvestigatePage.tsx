import { useEffect, useRef, useState } from "react";
import type { CaseItem, Run, Spec } from "./api";
import { getSpec, listCases } from "./api";
import CasesPage from "./CasesPage";
import Investigate from "./Investigate";

/** Investigate (from web_v2): run a sample case through preprocess -> deskagent_v1_1 and read its decision trace.
 *  Desk staff only; the hub serves the endpoints under /api/v2. Runs are kept in this browser. */
type View = "cases" | "trace";
const STORE = "greatagent-v2-runs";
export type Runs = Record<string, Run>;

function loadSaved(): Runs {
  try { const s = localStorage.getItem(STORE); return s ? (JSON.parse(s) as Runs) : {}; } catch { return {}; }
}

export default function InvestigatePage() {
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
    try {
      const j = JSON.parse(await f.text());
      if (j && j.preprocess && "response" in j) { addRun(j as Run); setSelected(j.case); setView("trace"); }
    } catch { /* not a run file */ }
  };
  const show = (v: View) => { setView(v); window.scrollTo({ top: 0 }); };

  return (
    <div className="investigate">
      <div className="investigate__bar">
        <div className="tabs" role="tablist" aria-label="Investigate">
          <button role="tab" className="tab" aria-selected={view === "cases"} onClick={() => show("cases")}>Cases</button>
          <button role="tab" className="tab" aria-selected={view === "trace"} onClick={() => show("trace")}>Decision trace</button>
        </div>
        <div className="investigate__actions">
          <button className="btn-text" disabled={!runs[selected]} onClick={download}>Download run</button>
          <button className="btn btn--secondary btn--sm" onClick={() => file.current?.click()}>Open run…</button>
          <input ref={file} type="file" accept="application/json,.json" hidden
                 onChange={(e) => { open(e.target.files?.[0]); e.target.value = ""; }} />
        </div>
      </div>
      {view === "cases"
        ? <CasesPage cases={cases} loadErr={loadErr} selected={selected} onSelect={setSelected} runs={runs} onRun={addRun}
            onTrace={(id) => { setSelected(id); show("trace"); }} />
        : <Investigate runs={runs} cases={cases} selected={selected} onSelect={setSelected} spec={spec} onBack={() => show("cases")} />}
    </div>
  );
}
