import {
  ArrowRight,
  BrainCircuit,
  Building2,
  ChartNoAxesCombined,
  CircleDollarSign,
  Leaf,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

const features = [
  {
    icon: ChartNoAxesCombined,
    eyebrow: "01 · See the signal",
    title: "Building energy dashboard",
    description: "Turn thousands of meter readings into a focused view of energy use, impact, and the events that need attention.",
  },
  {
    icon: BrainCircuit,
    eyebrow: "02 · Find the outliers",
    title: "Explainable anomaly detection",
    description: "Compare off-hours electricity use with historical, schedule-aware baselines—not opaque black-box scores.",
  },
  {
    icon: CircleDollarSign,
    eyebrow: "03 · Act on impact",
    title: "Cost & carbon estimates",
    description: "Prioritize potential interventions with estimated financial and environmental impact, plus a clear next step.",
  },
];

export default function HeroPage({ onEnterDashboard }) {
  return (
    <main className="min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="relative isolate">
        <div className="absolute inset-x-0 top-0 -z-10 h-[38rem] bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-700/35 via-slate-950 to-slate-950" />
        <div className="absolute -right-40 top-28 -z-10 h-96 w-96 rounded-full bg-lime-400/10 blur-3xl" />
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="rounded-2xl bg-emerald-400 p-2.5 text-slate-950 shadow-lg shadow-emerald-500/20"><Sparkles size={20} /></div>
            <div><p className="text-sm font-bold tracking-[0.18em] text-emerald-300">GHOSTWATT</p><p className="text-xs text-slate-400">Energy intelligence</p></div>
          </div>
          <button onClick={onEnterDashboard} className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:border-emerald-300 hover:bg-emerald-400 hover:text-slate-950">
            Open dashboard <ArrowRight size={16} />
          </button>
        </nav>

        <section className="mx-auto grid max-w-7xl items-center gap-14 px-6 pb-24 pt-16 lg:grid-cols-[1.05fr_0.95fr] lg:px-8 lg:pb-32 lg:pt-24">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-300/20 bg-emerald-300/10 px-3 py-1.5 text-xs font-semibold text-emerald-200"><Leaf size={14} /> Climate Tech & Clean Energy</div>
            <h1 className="mt-7 max-w-3xl text-5xl font-semibold leading-[1.02] tracking-tight text-white sm:text-6xl lg:text-7xl">Find energy waste <span className="text-emerald-300">before it becomes routine.</span></h1>
            <p className="mt-7 max-w-2xl text-lg leading-8 text-slate-300">GhostWatt gives commercial building teams the energy-auditing intelligence usually reserved for expensive building-management systems—using the data they already collect.</p>
            <div className="mt-9 flex flex-wrap gap-3">
              <button onClick={onEnterDashboard} className="inline-flex items-center gap-2 rounded-xl bg-emerald-400 px-5 py-3.5 font-semibold text-slate-950 shadow-xl shadow-emerald-500/20 transition hover:bg-emerald-300">Explore the dashboard <ArrowRight size={18} /></button>
              <a href="#how-it-works" className="rounded-xl border border-white/15 px-5 py-3.5 font-semibold text-white transition hover:border-emerald-300">How it works</a>
            </div>
            <div className="mt-10 flex flex-wrap gap-x-7 gap-y-3 text-sm text-slate-400"><span className="flex items-center gap-2"><ShieldCheck size={16} className="text-emerald-300" /> Explainable baselines</span><span className="flex items-center gap-2"><Building2 size={16} className="text-emerald-300" /> Built for real operations</span></div>
          </div>

          <div className="relative mx-auto w-full max-w-xl rounded-3xl border border-white/10 bg-slate-900/75 p-5 shadow-2xl shadow-black/30 backdrop-blur">
            <div className="flex items-center justify-between border-b border-white/10 pb-4"><div><p className="text-xs font-semibold uppercase tracking-widest text-emerald-300">Live opportunity</p><p className="mt-1 text-lg font-semibold text-white">Off-hours energy use</p></div><span className="rounded-full bg-orange-400/15 px-3 py-1 text-xs font-bold text-orange-200">High impact</span></div>
            <div className="mt-6 grid grid-cols-3 gap-3"><MiniMetric label="Actual" value="460 kWh" /><MiniMetric label="Expected" value="225 kWh" /><MiniMetric label="Excess" value="+235 kWh" accent /></div>
            <div className="mt-6 rounded-2xl border border-white/10 bg-slate-950/70 p-4"><div className="mb-4 flex items-center justify-between text-xs text-slate-400"><span>Actual vs. expected</span><span>Low-occupancy schedule</span></div><svg viewBox="0 0 420 160" className="h-44 w-full" aria-label="Example actual versus expected energy chart"><defs><linearGradient id="energy-fill" x1="0" x2="0" y1="0" y2="1"><stop stopColor="#34d399" stopOpacity=".35" /><stop offset="1" stopColor="#34d399" stopOpacity="0" /></linearGradient></defs>{[32, 76, 120].map((y) => <line key={y} x1="0" x2="420" y1={y} y2={y} stroke="#334155" />)}<path d="M0 116 L55 112 L110 116 L165 110 L220 114 L275 110 L330 114 L420 111" fill="none" stroke="#94a3b8" strokeDasharray="6 6" strokeWidth="3" /><path d="M0 112 L55 106 L110 82 L165 48 L220 36 L275 41 L330 58 L420 76 L420 140 L0 140 Z" fill="url(#energy-fill)" /><path d="M0 112 L55 106 L110 82 L165 48 L220 36 L275 41 L330 58 L420 76" fill="none" stroke="#34d399" strokeLinecap="round" strokeLinejoin="round" strokeWidth="4" /><circle cx="220" cy="36" r="6" fill="#fb923c" /></svg></div>
            <div className="mt-5 flex items-start gap-3 rounded-xl bg-emerald-400/10 p-3 text-sm leading-5 text-emerald-100"><BrainCircuit className="mt-0.5 shrink-0 text-emerald-300" size={18} /> Electricity is substantially above the expected level during a low-occupancy schedule period.</div>
          </div>
        </section>
      </div>

      <section id="how-it-works" className="border-y border-slate-800 bg-slate-900/60 py-20"><div className="mx-auto max-w-7xl px-6 lg:px-8"><div className="max-w-2xl"><p className="text-sm font-semibold uppercase tracking-[0.15em] text-emerald-300">From data to decision</p><h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">Energy auditing that speaks operations.</h2><p className="mt-4 leading-7 text-slate-400">GhostWatt combines historical electricity, building schedules, occupancy evidence, weather, and operational context to surface potential waste worth investigating.</p></div><div className="mt-12 grid gap-5 md:grid-cols-3">{features.map(({ icon: Icon, eyebrow, title, description }) => <article key={title} className="rounded-2xl border border-slate-800 bg-slate-950 p-6 transition hover:-translate-y-1 hover:border-emerald-400/40"><div className="inline-flex rounded-xl bg-emerald-400/10 p-3 text-emerald-300"><Icon size={22} /></div><p className="mt-6 text-xs font-bold uppercase tracking-widest text-emerald-300">{eyebrow}</p><h3 className="mt-2 text-xl font-semibold text-white">{title}</h3><p className="mt-3 leading-7 text-slate-400">{description}</p></article>)}</div></div></section>

      <section className="mx-auto max-w-7xl px-6 py-20 lg:px-8"><div className="rounded-3xl bg-emerald-400 px-7 py-10 text-slate-950 sm:px-12 sm:py-14"><div className="max-w-3xl"><p className="text-sm font-bold uppercase tracking-[0.15em] text-emerald-900">The GhostWatt mission</p><h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-5xl">Make energy auditing accessible and affordable.</h2><p className="mt-5 max-w-2xl text-lg leading-8 text-emerald-950">Built for property managers, facility teams, universities, and energy auditors who have meter data—but not a dedicated analytics platform.</p><button onClick={onEnterDashboard} className="mt-8 inline-flex items-center gap-2 rounded-xl bg-slate-950 px-5 py-3.5 font-semibold text-white transition hover:bg-slate-800">See Building 59 insights <ArrowRight size={18} /></button></div></div></section>
      <footer className="border-t border-slate-800 px-6 py-7 text-center text-sm text-slate-500">GhostWatt · AI-powered building energy waste detection</footer>
    </main>
  );
}

function MiniMetric({ label, value, accent = false }) {
  return <div className={`rounded-xl border border-white/10 p-3 ${accent ? "bg-orange-400/10" : "bg-white/5"}`}><p className="text-xs text-slate-400">{label}</p><p className={`mt-1 text-sm font-semibold ${accent ? "text-orange-200" : "text-white"}`}>{value}</p></div>;
}
