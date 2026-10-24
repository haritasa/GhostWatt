import { useEffect, useMemo, useState } from "react";
import {
  AlertCircle,
  ArrowUpRight,
  Bolt,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  Cloud,
  Download,
  Leaf,
  LoaderCircle,
  X,
} from "lucide-react";
import {
  clearBuilding59,
  demoDashboard,
  demoDetail,
  demoEvent,
  getAnomalies,
  getAnomaly,
  getDashboard,
  ingestBuilding59,
  updateAnomalyStatus,
} from "./api/ghostwatt";
import HeroPage from "./pages/HeroPage";

const statusOptions = ["all", "new", "investigating", "resolved", "dismissed"];
const severityClasses = {
  low: "bg-sky-100 text-sky-700 ring-sky-200",
  medium: "bg-amber-100 text-amber-800 ring-amber-200",
  high: "bg-orange-100 text-orange-800 ring-orange-200",
  critical: "bg-rose-100 text-rose-800 ring-rose-200",
};
const iconToneClasses = {
  emerald: "bg-emerald-50 text-emerald-600",
  orange: "bg-orange-50 text-orange-600",
  amber: "bg-amber-50 text-amber-600",
  sky: "bg-sky-50 text-sky-600",
  rose: "bg-rose-50 text-rose-600",
};

const money = (value) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(value);
const number = (value) => new Intl.NumberFormat("en-US", { maximumFractionDigits: 1 }).format(value);
const readableDate = (value) => new Date(value).toLocaleString([], { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" });

function Kpi({ label, value, caption, icon: Icon, tone = "emerald" }) {
  return (
    <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <p className="text-sm font-medium text-slate-500">{label}</p>
        <span className={`rounded-xl p-2 ${iconToneClasses[tone]}`}><Icon size={19} /></span>
      </div>
      <p className="mt-5 text-3xl font-semibold tracking-tight text-slate-900">{value}</p>
      <p className="mt-1 text-xs text-slate-500">{caption}</p>
    </article>
  );
}

function EnergyChart({ intervals }) {
  const points = intervals.length ? intervals : demoDetail.intervals;
  const maxValue = Math.max(...points.flatMap((point) => [point.actual_kwh, point.expected_kwh]), 1);
  const path = (field) => points.map((point, i) => `${i ? "L" : "M"}${20 + (i * 300) / Math.max(points.length - 1, 1)},${118 - (point[field] / maxValue) * 92}`).join(" ");
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-4">
      <div className="mb-2 flex items-center gap-4 text-xs text-slate-500">
        <span className="flex items-center gap-1"><i className="h-2 w-2 rounded-full bg-emerald-500" />Actual kWh</span>
        <span className="flex items-center gap-1"><i className="h-0 w-4 border-t-2 border-dashed border-slate-400" />Expected kWh</span>
      </div>
      <svg viewBox="0 0 340 140" className="h-40 w-full" role="img" aria-label="Actual versus expected energy chart">
        {[30, 75, 120].map((y) => <line key={y} x1="16" x2="324" y1={y} y2={y} stroke="#e2e8f0" strokeWidth="1" />)}
        <path d={path("expected_kwh")} fill="none" stroke="#94a3b8" strokeDasharray="5 5" strokeWidth="3" />
        <path d={path("actual_kwh")} fill="none" stroke="#10b981" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
        {points.map((point, i) => <circle key={point.timestamp} cx={20 + (i * 300) / Math.max(points.length - 1, 1)} cy={118 - (point.actual_kwh / maxValue) * 92} r="3.5" fill="#f97316" />)}
      </svg>
    </div>
  );
}

function DetailPanel({ event, onClose, onStatusChange, saving }) {
  if (!event) return null;
  return (
    <aside className="fixed inset-y-0 right-0 z-20 flex w-full max-w-xl flex-col border-l border-slate-200 bg-white shadow-2xl">
      <header className="flex items-start justify-between border-b border-slate-200 p-6">
        <div><p className="text-xs font-semibold uppercase tracking-widest text-emerald-600">Anomaly investigation</p><h2 className="mt-1 text-xl font-semibold text-slate-900">{event.title}</h2><p className="mt-1 text-sm text-slate-500">{readableDate(event.start_at)} · {event.duration_minutes} min</p></div>
        <button onClick={onClose} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100" aria-label="Close details"><X size={20} /></button>
      </header>
      <div className="flex-1 space-y-6 overflow-y-auto p-6">
        <div className="flex items-center gap-2"><span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ring-1 ${severityClasses[event.severity]}`}>{event.severity}</span><span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-600">{event.status}</span></div>
        <section><h3 className="font-semibold text-slate-900">What we found</h3><p className="mt-2 leading-6 text-slate-600">{event.explanation.headline}</p><div className="mt-4 grid grid-cols-3 gap-3 text-center"><Metric label="Actual" value={`${number(event.energy.actual_kwh)} kWh`} /><Metric label="Expected" value={`${number(event.energy.expected_kwh)} kWh`} /><Metric label="Excess" value={`${number(event.energy.excess_kwh)} kWh`} emphasis /></div></section>
        <section><h3 className="mb-3 font-semibold text-slate-900">Interval evidence</h3><EnergyChart intervals={event.intervals} /></section>
        <section className="rounded-xl bg-emerald-50 p-4"><div className="flex gap-3"><Bolt className="mt-0.5 shrink-0 text-emerald-600" size={19} /><div><h3 className="font-semibold text-emerald-950">Recommended next step</h3><p className="mt-1 text-sm leading-5 text-emerald-800">{event.recommended_actions[0]?.reason || event.recommended_action}</p></div></div></section>
        <section><h3 className="font-semibold text-slate-900">Impact estimate</h3><div className="mt-3 grid grid-cols-2 gap-3"><Metric label="Potential cost" value={money(event.impact.estimated_cost_usd)} /><Metric label="CO₂ impact" value={`${number(event.impact.estimated_co2_kg)} kg`} /></div><p className="mt-3 text-xs leading-5 text-slate-500">{event.impact.assumptions?.[1]}</p></section>
      </div>
      <footer className="grid grid-cols-3 gap-2 border-t border-slate-200 p-4">
        {[["investigating", "Start investigation"], ["resolved", "Resolve"], ["dismissed", "Dismiss"]].map(([status, label]) => <button key={status} disabled={saving || event.status === status} onClick={() => onStatusChange(status)} className="rounded-lg border border-slate-200 px-2 py-2.5 text-xs font-semibold text-slate-700 transition hover:border-emerald-400 hover:text-emerald-700 disabled:opacity-40">{label}</button>)}
      </footer>
    </aside>
  );
}

function Metric({ label, value, emphasis = false }) { return <div className={`rounded-xl p-3 ${emphasis ? "bg-orange-50" : "bg-slate-50"}`}><p className="text-xs text-slate-500">{label}</p><p className={`mt-1 text-sm font-semibold ${emphasis ? "text-orange-800" : "text-slate-900"}`}>{value}</p></div>; }

function ImportModal({ sourceDir, onSourceDirChange, onClose, onSubmit, onClear, importing, clearing }) {
  return <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/75 p-5 backdrop-blur-sm" role="presentation" onMouseDown={onClose}>
    <section className="w-full max-w-lg rounded-2xl border border-slate-200 bg-white p-6 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="import-title" onMouseDown={(event) => event.stopPropagation()}>
      <div className="flex items-start justify-between gap-4"><div><p className="text-xs font-semibold uppercase tracking-widest text-emerald-600">Data workspace</p><h2 id="import-title" className="mt-1 text-xl font-semibold text-slate-900">Import Building 59 data</h2><p className="mt-2 text-sm leading-6 text-slate-500">Enter the folder containing <code>ele.csv</code>, <code>occ.csv</code>, <code>wifi.csv</code>, and <code>site_weather.csv</code>.</p></div><button type="button" onClick={onClose} disabled={importing} className="rounded-lg p-2 text-slate-500 hover:bg-slate-100" aria-label="Close import dialog"><X size={20} /></button></div>
      <form onSubmit={onSubmit} className="mt-6"><label htmlFor="data-directory" className="text-sm font-semibold text-slate-700">Data folder path</label><input id="data-directory" autoFocus value={sourceDir} onChange={(event) => onSourceDirChange(event.target.value)} placeholder="/path/to/Bldg59_clean data" className="mt-2 w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-3 text-sm text-slate-900 outline-none placeholder:text-slate-400 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20" /><p className="mt-2 text-xs leading-5 text-slate-500">Leave this blank to use the backend’s configured default data directory.</p><div className="mt-6 flex flex-col-reverse justify-between gap-3 sm:flex-row sm:items-center"><button type="button" onClick={onClear} disabled={importing || clearing} className="rounded-xl px-3 py-2.5 text-sm font-semibold text-rose-700 hover:bg-rose-50 disabled:opacity-60">{clearing ? "Clearing…" : "Clear saved data"}</button><div className="flex justify-end gap-3"><button type="button" onClick={onClose} disabled={importing || clearing} className="rounded-xl px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-100">Cancel</button><button disabled={importing || clearing} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:opacity-60">{importing ? <LoaderCircle className="animate-spin" size={16} /> : <Download size={16} />}{importing ? "Importing…" : "Import & analyze"}</button></div></div></form>
    </section>
  </div>;
}

export default function App() {
  const [dashboard, setDashboard] = useState(demoDashboard);
  const [events, setEvents] = useState([demoEvent]);
  const [selected, setSelected] = useState(null);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(true);
  const [error, setError] = useState("");
  const [sourceDir, setSourceDir] = useState("");
  const [showImportModal, setShowImportModal] = useState(false);
  const [importing, setImporting] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [showDashboard, setShowDashboard] = useState(() => window.location.hash === "#/dashboard");
  const [darkMode, setDarkMode] = useState(() => {
    const savedTheme = window.localStorage.getItem("ghostwatt-theme");
    return savedTheme ? savedTheme === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches;
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    window.localStorage.setItem("ghostwatt-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  useEffect(() => {
    const syncRoute = () => setShowDashboard(window.location.hash === "#/dashboard");
    window.addEventListener("hashchange", syncRoute);
    return () => window.removeEventListener("hashchange", syncRoute);
  }, []);

  const reload = async (nextFilter = filter) => {
    setLoading(true); setError("");
    try {
      const [nextDashboard, list] = await Promise.all([getDashboard(), getAnomalies(nextFilter === "all" ? "" : nextFilter)]);
      if (nextDashboard.summary.total_energy_kwh === 0) throw new Error("No Building 59 dataset is loaded yet.");
      setDashboard(nextDashboard); setEvents(list.items); setDemo(false);
    } catch (reason) { setError(reason.message); setDashboard(demoDashboard); setEvents(nextFilter === "all" || nextFilter === "new" ? [demoEvent] : []); setDemo(true); }
    finally { setLoading(false); }
  };
  useEffect(() => { if (showDashboard) reload("all"); }, [showDashboard]);

  const chooseFilter = (value) => { setFilter(value); reload(value); };
  const openEvent = async (event) => { if (demo) { setSelected(demoDetail); return; } try { setSelected(await getAnomaly(event.id)); } catch (reason) { setError(reason.message); } };
  const changeStatus = async (status) => { if (demo) { setSelected((current) => ({ ...current, status })); setEvents((current) => current.map((event) => ({ ...event, status }))); return; } setSaving(true); try { const updated = await updateAnomalyStatus(selected.id, status); setSelected(updated); setEvents((current) => current.map((event) => event.id === updated.id ? updated : event)); } catch (reason) { setError(reason.message); } finally { setSaving(false); } };
  const importData = async (event) => { event.preventDefault(); setImporting(true); setError(""); try { await ingestBuilding59(sourceDir); await reload(filter); setShowImportModal(false); } catch (reason) { setError(reason.message); } finally { setImporting(false); } };
  const clearData = async () => {
    if (!window.confirm("Clear all imported Building 59 readings, anomaly events, and investigation statuses? This cannot be undone.")) return;
    setClearing(true); setError("");
    try {
      await clearBuilding59();
      setDashboard(demoDashboard); setEvents([demoEvent]); setSelected(null); setFilter("all"); setDemo(true);
    } catch (reason) { setError(reason.message); }
    finally { setClearing(false); }
  };
  const openDashboard = () => { window.location.hash = "/dashboard"; };
  const title = useMemo(() => dashboard.building.name, [dashboard]);

  if (!showDashboard) return <HeroPage onEnterDashboard={openDashboard} />;

  return <main className="min-h-screen bg-slate-50 text-slate-900"><div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
    <header className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center"><div className="flex items-center gap-3"><div className="rounded-2xl bg-emerald-600 p-3 text-white shadow-lg shadow-emerald-200"><Bolt size={24} fill="currentColor" /></div><div><p className="text-sm font-semibold tracking-wide text-emerald-700">GHOSTWATT</p><h1 className="text-xl font-semibold tracking-tight">Energy anomaly command center</h1></div></div><div className="flex items-center gap-2"><button type="button" onClick={() => setShowImportModal(true)} className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"><Download size={16} /><span className="hidden sm:inline">Import</span></button><button type="button" onClick={() => setDarkMode((enabled) => !enabled)} aria-pressed={darkMode} aria-label={`Switch to ${darkMode ? "light" : "dark"} mode`} className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-600 transition hover:border-emerald-400 hover:text-emerald-700"><span aria-hidden="true">{darkMode ? "☀︎" : "☾"}</span><span className="ml-2 hidden sm:inline">{darkMode ? "Light" : "Dark"}</span></button><div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600"><span className="h-2 w-2 rounded-full bg-emerald-500" />{title}</div></div></header>
    {demo && <section className="mt-6 rounded-xl border border-amber-200 bg-amber-50 p-4"><div className="flex items-start gap-3"><AlertCircle className="mt-0.5 shrink-0 text-amber-600" size={19} /><div className="flex-1"><p className="font-semibold text-amber-900">Demo view — no live dataset loaded</p><p className="mt-1 text-sm text-amber-800">Import Building 59 data to replace this preview with live energy analysis.</p><button type="button" onClick={() => setShowImportModal(true)} className="mt-3 inline-flex items-center gap-2 rounded-lg bg-amber-900 px-3 py-2 text-sm font-semibold text-white hover:bg-amber-950"><Download size={16} />Import data</button></div></div></section>}
    {error && <p className="mt-4 rounded-lg bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
    <section className="mt-7"><div className="mb-4 flex items-end justify-between"><div><p className="text-sm font-medium text-slate-500">Portfolio overview</p><h2 className="text-2xl font-semibold tracking-tight">Find waste before it becomes routine.</h2></div>{loading && <LoaderCircle className="animate-spin text-emerald-600" size={20} />}</div><div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5"><Kpi label="Total energy" value={`${number(dashboard.summary.total_energy_kwh)} kWh`} caption="Selected analysis period" icon={Bolt} /><Kpi label="Excess energy" value={`${number(dashboard.summary.anomalous_excess_kwh)} kWh`} caption="Across identified events" icon={ArrowUpRight} tone="orange" /><Kpi label="Cost opportunity" value={money(dashboard.summary.estimated_cost_impact_usd)} caption="Estimated, not verified savings" icon={CircleDollarSign} tone="amber" /><Kpi label="CO₂ impact" value={`${number(dashboard.summary.estimated_co2_kg)} kg`} caption="Estimated avoided emissions" icon={Cloud} tone="sky" /><Kpi label="Events" value={dashboard.summary.anomaly_event_count} caption="Require review" icon={AlertCircle} tone="rose" /></div></section>
    <section className="mt-9 rounded-2xl border border-slate-200 bg-white shadow-sm"><div className="flex flex-col gap-4 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between"><div><h2 className="font-semibold">Anomaly queue</h2><p className="mt-1 text-sm text-slate-500">Explainable, comparable-period deviations during low occupancy.</p></div><div className="flex flex-wrap gap-1 rounded-lg bg-slate-100 p-1">{statusOptions.map((option) => <button key={option} onClick={() => chooseFilter(option)} className={`rounded-md px-3 py-1.5 text-xs font-semibold capitalize ${filter === option ? "bg-white text-emerald-700 shadow-sm" : "text-slate-500 hover:text-slate-900"}`}>{option}</button>)}</div></div>
      <div className="divide-y divide-slate-100">{events.length ? events.map((event) => <button key={event.id} onClick={() => openEvent(event)} className="flex w-full items-center gap-4 px-5 py-4 text-left transition hover:bg-slate-50"><span className={`min-w-16 rounded-full px-2.5 py-1 text-center text-xs font-semibold capitalize ring-1 ${severityClasses[event.severity]}`}>{event.severity}</span><div className="min-w-0 flex-1"><div className="flex items-center gap-2"><p className="truncate font-semibold text-slate-900">{event.title}</p><span className="hidden rounded bg-slate-100 px-1.5 py-0.5 text-xs capitalize text-slate-500 sm:inline">{event.status}</span></div><p className="mt-1 truncate text-sm text-slate-500">{readableDate(event.start_at)} · {event.occupancy_context.label}{event.occupancy_context.value == null ? "" : ` (${number(event.occupancy_context.value)} ${event.occupancy_context.unit})`}</p></div><div className="hidden text-right sm:block"><p className="font-semibold text-orange-700">+{number(event.energy.excess_kwh)} kWh</p><p className="mt-1 text-xs text-slate-500">{money(event.impact.estimated_cost_usd)} estimated</p></div><ChevronRight className="shrink-0 text-slate-400" size={20} /></button>) : <div className="p-12 text-center"><CheckCircle2 className="mx-auto text-emerald-500" size={30} /><p className="mt-3 font-semibold">No matching anomalies</p><p className="mt-1 text-sm text-slate-500">Try another status or expand the analysis period.</p></div>}</div></section>
    <p className="mt-5 text-xs text-slate-400">Timestamps use source-local time because the Building 59 files do not specify a timezone.</p>
  </div>{showImportModal && <ImportModal sourceDir={sourceDir} onSourceDirChange={setSourceDir} onClose={() => setShowImportModal(false)} onSubmit={importData} onClear={clearData} importing={importing} clearing={clearing} />}{selected && <DetailPanel event={selected} onClose={() => setSelected(null)} onStatusChange={changeStatus} saving={saving} />}</main>;
}
