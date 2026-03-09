"""
Memory Inspector Dashboard — HTML/CSS/JS for the Inspector Web UI.
OpenMemo Agent Memory Infrastructure Control Plane.
4-layer architecture: Value / Intelligence / Decision / Memory.
"""

INSPECTOR_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OpenMemo Memory Inspector</title>
<style>
:root {
  --bg: #06090f;
  --bg-card: #0c1120;
  --bg-hover: #151d2e;
  --bg-input: #0a0f1a;
  --border: #1a2236;
  --border-hover: #2a3654;
  --text: #e8edf5;
  --text-s: #94a3b8;
  --text-m: #64748b;
  --accent: #6366f1;
  --accent-l: #818cf8;
  --green: #22c55e;
  --green-bg: rgba(34,197,94,0.10);
  --amber: #f59e0b;
  --amber-bg: rgba(245,158,11,0.10);
  --red: #ef4444;
  --red-bg: rgba(239,68,68,0.10);
  --blue: #3b82f6;
  --blue-bg: rgba(59,130,246,0.10);
  --purple: #a78bfa;
  --purple-bg: rgba(167,139,250,0.10);
  --cyan: #22d3ee;
  --cyan-bg: rgba(34,211,238,0.10);
  --r: 14px;
  --rs: 8px;
}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);line-height:1.5;-webkit-font-smoothing:antialiased}

.header{background:linear-gradient(135deg,#0c1120 0%,#0f172a 100%);border-bottom:1px solid var(--border);padding:16px 28px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;backdrop-filter:blur(16px)}
.header-l{display:flex;align-items:center;gap:12px}
.logo{width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,var(--accent),#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:15px;color:#fff;font-weight:700}
.header h1{font-size:16px;font-weight:700;letter-spacing:-0.3px}
.header-r{display:flex;align-items:center;gap:14px}
.ver{font-size:11px;color:var(--text-m);font-weight:500}
.live{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text-m);transition:color .3s}
.dot-live{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite;transition:background .3s}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

.lang-btn{padding:4px 10px;border-radius:6px;font-size:11px;font-weight:600;background:rgba(255,255,255,.04);border:1px solid var(--border);color:var(--text-s);cursor:pointer;transition:all .15s;letter-spacing:.3px}
.lang-btn:hover{background:rgba(99,102,241,.12);border-color:var(--accent);color:var(--accent-l)}

.conn-lost .dot-live{background:var(--red)!important;animation:none!important}
.conn-lost .live{color:var(--red)!important}
.conn-banner{display:none;background:var(--red-bg);border:1px solid rgba(239,68,68,.25);color:var(--red);padding:10px 28px;font-size:12px;font-weight:600;text-align:center;letter-spacing:.3px}
.conn-lost .conn-banner{display:block}

.layer-label{font-size:11px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--text-s);padding:28px 28px 10px;background:linear-gradient(90deg,rgba(99,102,241,.08),transparent);border-left:3px solid var(--accent);margin:0 0 4px;border-radius:0 6px 6px 0}
.page{max-width:1360px;margin:0 auto;padding:0 28px 60px}

.hero{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin-bottom:4px}
.hero-c{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);padding:18px 20px;position:relative;overflow:hidden;transition:all .2s}
.hero-c:hover{border-color:var(--border-hover);transform:translateY(-1px)}
.hero-l{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-m);margin-bottom:6px}
.hero-v{font-size:28px;font-weight:800;letter-spacing:-1px;line-height:1.1}
.hero-s{font-size:11px;color:var(--text-m);margin-top:3px}
.hero-i{position:absolute;top:14px;right:16px;width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px}
.hero-c.status-fail{border-color:rgba(239,68,68,.3)}
.hero-c.status-fail .hero-v{color:var(--red)!important}

.g{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:4px}
.gf{grid-column:1/-1}
.g-60-40{grid-template-columns:3fr 2fr}

.c{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);padding:20px;transition:border-color .2s}
.c:hover{border-color:var(--border-hover)}
.ct{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:var(--text-m);margin-bottom:14px;display:flex;align-items:center;gap:7px}
.ct .d{width:5px;height:5px;border-radius:50%}

.chk{display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.chk-i{display:flex;align-items:center;gap:8px;padding:9px 12px;border-radius:var(--rs);background:rgba(255,255,255,.015);border-left:2px solid transparent;transition:all .15s}
.chk-i:hover{background:rgba(255,255,255,.03)}
.chk-i.ok{border-left-color:var(--green)}
.chk-i.warning{border-left-color:var(--amber)}
.chk-i.fail{border-left-color:var(--red)}
.chk-i.cold_start{border-left-color:var(--text-m)}
.chk-ic{width:18px;height:18px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;font-weight:700;flex-shrink:0}
.chk-ic.ok{background:var(--green-bg);color:var(--green)}
.chk-ic.warning{background:var(--amber-bg);color:var(--amber)}
.chk-ic.fail{background:var(--red-bg);color:var(--red)}
.chk-ic.cold_start{background:rgba(100,116,139,.12);color:var(--text-m)}
.chk-t{font-size:12px;color:var(--text-s);font-weight:500}

.scene-wrap{display:flex;align-items:center;gap:16px;margin-bottom:14px}
.scene-badge{padding:8px 20px;border-radius:20px;font-size:15px;font-weight:700;background:linear-gradient(135deg,rgba(99,102,241,.15),rgba(139,92,246,.15));color:var(--accent-l);border:1px solid rgba(99,102,241,.25)}
.scene-conf{font-size:12px;color:var(--text-s)}
.scene-conf b{color:var(--accent-l);font-weight:700;font-size:14px}
.scene-source{display:inline-block;font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;margin-left:8px;letter-spacing:.4px;text-transform:uppercase}
.scene-source.heuristic{background:rgba(99,102,241,.1);color:var(--accent-l)}
.scene-source.manual{background:var(--green-bg);color:var(--green)}
.override-btn{margin-top:14px;padding:7px 16px;border-radius:8px;background:rgba(99,102,241,.1);border:1px solid rgba(99,102,241,.25);color:var(--accent-l);font-size:11px;font-weight:600;cursor:pointer;transition:all .15s}
.override-btn:hover{background:rgba(99,102,241,.2)}
.override-opts{margin-top:8px;display:none;flex-wrap:wrap;gap:6px}
.override-opts.show{display:flex}
.override-opt{padding:5px 12px;border-radius:14px;font-size:11px;font-weight:600;background:rgba(255,255,255,.04);border:1px solid var(--border);color:var(--text-s);cursor:pointer;transition:all .15s}
.override-opt:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.override-opt.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.override-toast{position:fixed;bottom:24px;right:24px;padding:10px 18px;border-radius:8px;font-size:12px;font-weight:600;color:#fff;z-index:200;opacity:0;transform:translateY(10px);transition:all .3s;pointer-events:none}
.override-toast.show{opacity:1;transform:translateY(0)}
.override-toast.ok{background:var(--green)}
.override-toast.err{background:var(--red)}

.dr{display:flex;align-items:center;gap:10px;padding:4px 0}
.dl{font-size:12px;color:var(--text-s);min-width:90px;font-weight:500}
.dt{flex:1;height:5px;background:rgba(255,255,255,.04);border-radius:3px;overflow:hidden}
.df{height:100%;border-radius:3px;transition:width .6s cubic-bezier(.22,1,.36,1)}
.df.tp{background:linear-gradient(90deg,var(--accent),var(--accent-l))}
.df.sc{background:linear-gradient(90deg,var(--green),#4ade80)}
.dc{font-size:12px;color:var(--text-m);min-width:28px;text-align:right;font-weight:600;font-variant-numeric:tabular-nums}

.task-box{background:rgba(99,102,241,.04);border:1px solid rgba(99,102,241,.12);border-radius:var(--rs);padding:16px}
.task-r{display:flex;justify-content:space-between;align-items:center;padding:5px 0}
.task-k{font-size:12px;color:var(--text-m)}
.task-v{font-size:12px;color:var(--text);font-weight:500}
.task-v.act{color:var(--green);font-weight:700}
.task-v.mono{font-family:'SF Mono','Fira Code',monospace;font-size:11px;color:var(--accent-l)}

.info-g{display:grid;grid-template-columns:1fr 1fr;gap:0}
.info-i{display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid rgba(255,255,255,.03)}
.info-i:nth-last-child(-n+2){border-bottom:none}
.info-i:nth-child(odd){padding-right:16px}
.info-i:nth-child(even){padding-left:16px;border-left:1px solid rgba(255,255,255,.03)}
.info-k{font-size:12px;color:var(--text-m)}
.info-v{font-size:12px;color:var(--text);font-weight:600;font-variant-numeric:tabular-nums}

.tl{position:relative}
.tl-i{display:flex;gap:14px;padding:10px 6px;position:relative;cursor:pointer;transition:background .15s;border-radius:var(--rs)}
.tl-i:hover{background:rgba(255,255,255,.02)}
.tl-i:not(:last-child)::before{content:'';position:absolute;left:21px;top:36px;bottom:0;width:1px;background:var(--border)}
.tl-i.suppressed{opacity:.45;filter:grayscale(.6)}
.tl-i.suppressed:hover{opacity:.65}
.tl-dot{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:11px;flex-shrink:0;position:relative;z-index:1}
.tl-dot.preference{background:var(--blue-bg);border:1px solid rgba(59,130,246,.25)}
.tl-dot.task_execution{background:var(--green-bg);border:1px solid rgba(34,197,94,.25)}
.tl-dot.fact{background:var(--purple-bg);border:1px solid rgba(167,139,250,.25)}
.tl-dot.decision{background:var(--amber-bg);border:1px solid rgba(245,158,11,.25)}
.tl-dot.observation{background:var(--cyan-bg);border:1px solid rgba(34,211,238,.25)}
.tl-body{flex:1;min-width:0}
.tl-text{font-size:13px;color:var(--text);line-height:1.4;margin-bottom:5px}
.tl-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.pill{display:inline-flex;align-items:center;padding:2px 8px;border-radius:14px;font-size:10px;font-weight:600;letter-spacing:.2px}
.pill.sc{background:rgba(59,130,246,.1);color:#60a5fa}
.pill.tp{background:rgba(34,197,94,.1);color:#4ade80}
.pill.sr{background:rgba(245,158,11,.1);color:#fbbf24}
.pill.tm{background:rgba(100,116,139,.08);color:var(--text-m)}
.pill.ns{background:rgba(167,139,250,.1);color:#c4b5fd}
.pill.suppressed-pill{background:var(--red-bg);color:var(--red)}

.ns-icon{display:inline-flex;align-items:center;gap:4px;padding:2px 8px;border-radius:14px;font-size:10px;font-weight:600;background:rgba(167,139,250,.1);color:#c4b5fd}
.ns-icon .ns-dot{width:5px;height:5px;border-radius:50%;background:currentColor}

.tl-score{display:flex;gap:12px;margin-top:6px;padding:8px 12px;background:rgba(255,255,255,.015);border-radius:6px;flex-wrap:wrap;align-items:center}
.tl-score-i{font-size:11px;color:var(--text-m)}
.tl-score-i b{color:var(--text-s);font-weight:600}
.score-formula{font-size:10px;color:var(--text-m);font-family:'SF Mono','Fira Code',monospace;padding:3px 8px;background:rgba(99,102,241,.06);border-radius:4px;border:1px solid rgba(99,102,241,.1)}

.tl-expand{display:none;margin-top:8px;padding:12px 14px;background:rgba(99,102,241,.04);border:1px solid rgba(99,102,241,.1);border-radius:var(--rs)}
.tl-expand.show{display:block}
.exp-r{display:flex;justify-content:space-between;padding:3px 0;font-size:12px}
.exp-k{color:var(--text-m)}
.exp-v{color:var(--text-s);font-weight:500}
.exp-v.mono{font-family:'SF Mono','Fira Code',monospace;font-size:11px;color:var(--accent-l)}

.search-w{position:relative;margin-bottom:14px}
.search-ic{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:var(--text-m);font-size:13px;pointer-events:none}
.search-in{width:100%;padding:12px 14px 12px 38px;background:var(--bg-input);border:1px solid var(--border);border-radius:var(--rs);color:var(--text);font-size:13px;outline:none;transition:all .2s}
.search-in:focus{border-color:var(--accent);box-shadow:0 0 0 3px rgba(99,102,241,.12)}
.search-in::placeholder{color:var(--text-m)}
.search-res{min-height:16px}

.growth-chart{display:flex;align-items:flex-end;gap:8px;height:100px;padding-top:10px}
.growth-bar-w{flex:1;display:flex;flex-direction:column;align-items:center;gap:4px}
.growth-bar{width:100%;border-radius:4px 4px 0 0;background:linear-gradient(180deg,var(--accent),rgba(99,102,241,.3));transition:height .4s cubic-bezier(.22,1,.36,1);min-height:4px}
.growth-lbl{font-size:10px;color:var(--text-m);font-weight:500}
.growth-val{font-size:10px;color:var(--text-s);font-weight:600}

.snap-btn{display:flex;align-items:center;gap:8px;padding:12px 16px;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:var(--rs);cursor:not-allowed;opacity:.6;width:100%;margin-top:12px}
.snap-ic{font-size:14px}
.snap-t{flex:1}
.snap-t .name{font-size:12px;color:var(--text-s);font-weight:600}
.snap-t .desc{font-size:10px;color:var(--text-m)}
.snap-lock{font-size:10px;color:var(--amber);font-weight:700;padding:2px 8px;border-radius:10px;background:var(--amber-bg)}

.empty{text-align:center;padding:24px;color:var(--text-m);font-size:12px}

@media(max-width:1200px){.hero{grid-template-columns:repeat(3,1fr)}}
@media(max-width:1024px){.chk{grid-template-columns:1fr 1fr}}
@media(max-width:768px){.hero{grid-template-columns:1fr 1fr}.g,.g-60-40{grid-template-columns:1fr}.chk{grid-template-columns:1fr}.info-g{grid-template-columns:1fr}.info-i:nth-child(even){padding-left:0;border-left:none}.info-i:nth-child(odd){padding-right:0}.page{padding:0 16px 40px}.header{padding:12px 16px}}
</style>
</head>
<body>

<div class="header">
  <div class="header-l">
    <div class="logo">M</div>
    <h1 data-i18n="title">Memory Inspector</h1>
  </div>
  <div class="header-r">
    <span class="ver" id="header-version"></span>
    <span class="live" id="conn-status"><span class="dot-live"></span> <span id="conn-text">Live</span></span>
    <button class="lang-btn" id="lang-btn" onclick="toggleLang()">EN / \u4e2d</button>
  </div>
</div>
<div class="conn-banner" id="conn-banner"></div>

<div class="page">

<div class="layer-label" data-i18n="layer_value">Value Layer</div>
<div class="hero" id="hero-stats"></div>

<div class="layer-label" data-i18n="layer_intel">Intelligence Layer</div>
<div class="g">
  <div class="c gf">
    <div class="ct"><span class="d" style="background:var(--green)"></span> <span data-i18n="health">System Health</span></div>
    <div class="chk" id="checklist"></div>
  </div>
</div>

<div class="g g-60-40">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--accent)"></span> <span data-i18n="scene_dynamics">Scene Dynamics</span></div>
    <div id="scene-dynamics"><div class="empty" data-i18n="empty_scene">Scene data not available</div></div>
  </div>
  <div class="c" style="display:flex;flex-direction:column;gap:12px">
    <div>
      <div class="ct"><span class="d" style="background:var(--accent)"></span> <span data-i18n="type_dist">Type Distribution</span></div>
      <div id="type-dist"><div class="empty" data-i18n="empty_data">No data yet</div></div>
    </div>
    <div>
      <div class="ct"><span class="d" style="background:var(--green)"></span> <span data-i18n="scene_dist">Scene Distribution</span></div>
      <div id="scene-dist"><div class="empty" data-i18n="empty_data">No data yet</div></div>
    </div>
  </div>
</div>

<div class="layer-label" data-i18n="layer_decision">Decision Layer</div>
<div class="g">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--cyan)"></span> <span data-i18n="task_precheck">Task Pre-Check</span></div>
    <div class="task-box" id="task-check"><div class="empty" data-i18n="empty_task">No task check data available</div></div>
  </div>
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--amber)"></span> <span data-i18n="system_info">System Info</span></div>
    <div class="info-g" id="system-info"></div>
  </div>
</div>

<div class="layer-label" data-i18n="layer_memory">Memory Layer</div>
<div class="g">
  <div class="c gf">
    <div class="ct"><span class="d" style="background:var(--blue)"></span> <span data-i18n="memory_search">Memory Search</span></div>
    <div class="search-w">
      <span class="search-ic">&#x1F50D;</span>
      <input type="text" class="search-in" id="search-input" />
    </div>
    <div class="search-res" id="search-results"></div>
  </div>
</div>

<div class="g g-60-40">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--cyan)"></span> <span data-i18n="memory_stream">Memory Stream</span></div>
    <div style="margin-bottom:10px"><span class="score-formula" id="score-formula">Score = (Sem &times; 0.6) + (Rec &times; 0.25) + (Scene &times; 0.15)</span></div>
    <div class="tl" id="recent-writes"></div>
  </div>
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--purple)"></span> <span data-i18n="memory_growth">Memory Growth</span></div>
    <div class="growth-chart" id="growth-chart"><div class="empty" style="width:100%" data-i18n="empty_growth">Growth data available with extended API</div></div>
    <div class="snap-btn">
      <span class="snap-ic">&#x1F4F8;</span>
      <div class="snap-t">
        <div class="name" data-i18n="snapshot">Memory Snapshot</div>
        <div class="desc" data-i18n="snapshot_desc">Save full agent memory state</div>
      </div>
      <span class="snap-lock">PRO</span>
    </div>
  </div>
</div>

<div class="g">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--accent)"></span> <span data-i18n="version">Version</span></div>
    <div id="update-status"></div>
  </div>
</div>

</div>

<div class="override-toast" id="override-toast"></div>

<script>
const API='';
let expandIdx=-1;
let recallScores=[];
let recallLatency=0;
let apiConnected=true;
let sceneOverridden=false;
let overriddenScene='';
let LANG=(function(){var v=localStorage.getItem('inspector_lang');return(v==='zh')?'zh':'en'})();

const I18N={
  en:{
    title:"Memory Inspector",
    layer_value:"Value Layer",
    layer_intel:"Intelligence Layer",
    layer_decision:"Decision Layer",
    layer_memory:"Memory Layer",
    health:"System Health",
    scene_dynamics:"Scene Dynamics",
    confidence:"Confidence",
    override_scene:"Override Scene",
    type_dist:"Type Distribution",
    scene_dist:"Scene Distribution",
    task_precheck:"Task Pre-Check",
    system_info:"System Info",
    memory_search:"Memory Search",
    search_placeholder:"Search through agent memories...",
    memory_stream:"Memory Stream",
    memory_growth:"Memory Growth",
    snapshot:"Memory Snapshot",
    snapshot_desc:"Save full agent memory state",
    version:"Version",
    no_results:"No results for",
    empty_scene:"Scene data not available",
    empty_data:"No data yet",
    empty_task:"No task check data available",
    empty_growth:"Growth data available with extended API",
    empty_cold:"No memories yet \\u2014 cold start",
    empty_load:"Could not load",
    hero_memories:"Total Memories",
    hero_memories_sub:"stored memory entries",
    hero_cells:"MemCells",
    hero_cells_sub:"atomic knowledge units",
    hero_tokens:"Tokens Saved",
    hero_tokens_sub_prefix:"\\u2248 $",
    hero_tokens_sub_suffix:" saved",
    hero_recall:"Recall Confidence",
    hero_recall_sub:"avg of last 10 recalls",
    hero_latency:"Recall Latency",
    hero_latency_sub:"last measured p95",
    hero_status:"System Status",
    status_healthy:"\\u2713 Healthy",
    status_degraded:"! Degraded",
    status_unhealthy:"\\u2717 Unhealthy",
    status_cold:"\\u25CB Cold Start",
    status_bypass:"\\u26A0 Memory Bypass Active",
    status_sub_ok:"all checks passed",
    status_sub_warn:"some checks need attention",
    status_sub_fail:"system issues detected",
    status_sub_cold:"warming up",
    status_sub_bypass:"agent running without memory",
    status_unknown:"status unknown",
    top_scene:"Top scene by volume",
    mem_id:"Memory ID",
    type:"Type",
    scene:"Scene",
    score:"Score",
    semantic:"Sem",
    recency:"Rec",
    scene_score:"Scene",
    rank:"Rank",
    namespace:"Namespace",
    suppressed:"Suppressed",
    backend:"Backend",
    status:"Status",
    api_version:"API Version",
    engine:"Engine",
    memories:"Memories",
    scenes:"Scenes",
    conn_ok:"Live",
    conn_lost:"Disconnected",
    bypass_banner:"\\u26A0 Local API Server disconnected \\u2014 Memory Bypass Active",
    override_ok:"Scene overridden to",
    override_fail:"Override failed",
    heuristic:"HEURISTIC",
    manual:"MANUAL",
    formula:"Score = (Sem &times; 0.6) + (Rec &times; 0.25) + (Scene &times; 0.15)",
  },
  zh:{
    title:"\\u8bb0\\u5fc6\\u68c0\\u89c6\\u5668",
    layer_value:"\\u4ef7\\u503c\\u5c42",
    layer_intel:"\\u667a\\u80fd\\u5c42",
    layer_decision:"\\u51b3\\u7b56\\u5c42",
    layer_memory:"\\u8bb0\\u5fc6\\u5c42",
    health:"\\u7cfb\\u7edf\\u5065\\u5eb7",
    scene_dynamics:"\\u573a\\u666f\\u52a8\\u6001",
    confidence:"\\u7f6e\\u4fe1\\u5ea6",
    override_scene:"\\u5207\\u6362\\u573a\\u666f",
    type_dist:"\\u7c7b\\u578b\\u5206\\u5e03",
    scene_dist:"\\u573a\\u666f\\u5206\\u5e03",
    task_precheck:"\\u4efb\\u52a1\\u9884\\u68c0\\u67e5",
    system_info:"\\u7cfb\\u7edf\\u4fe1\\u606f",
    memory_search:"\\u8bb0\\u5fc6\\u641c\\u7d22",
    search_placeholder:"\\u641c\\u7d22\\u667a\\u80fd\\u4f53\\u8bb0\\u5fc6...",
    memory_stream:"\\u8bb0\\u5fc6\\u6d41",
    memory_growth:"\\u8bb0\\u5fc6\\u589e\\u957f",
    snapshot:"\\u8bb0\\u5fc6\\u5feb\\u7167",
    snapshot_desc:"\\u4fdd\\u5b58\\u5b8c\\u6574\\u667a\\u80fd\\u4f53\\u8bb0\\u5fc6\\u72b6\\u6001",
    version:"\\u7248\\u672c\\u4fe1\\u606f",
    no_results:"\\u672a\\u627e\\u5230\\u7ed3\\u679c\\uff1a",
    empty_scene:"\\u573a\\u666f\\u6570\\u636e\\u4e0d\\u53ef\\u7528",
    empty_data:"\\u6682\\u65e0\\u6570\\u636e",
    empty_task:"\\u6682\\u65e0\\u4efb\\u52a1\\u68c0\\u67e5\\u6570\\u636e",
    empty_growth:"\\u589e\\u957f\\u6570\\u636e\\u9700\\u8981\\u6269\\u5c55 API",
    empty_cold:"\\u6682\\u65e0\\u8bb0\\u5fc6 \\u2014 \\u51b7\\u542f\\u52a8",
    empty_load:"\\u52a0\\u8f7d\\u5931\\u8d25",
    hero_memories:"\\u603b\\u8bb0\\u5fc6\\u6570",
    hero_memories_sub:"\\u5df2\\u5b58\\u50a8\\u7684\\u8bb0\\u5fc6\\u6761\\u76ee",
    hero_cells:"\\u8bb0\\u5fc6\\u5355\\u5143",
    hero_cells_sub:"\\u539f\\u5b50\\u77e5\\u8bc6\\u5355\\u5143",
    hero_tokens:"Token \\u8282\\u7701",
    hero_tokens_sub_prefix:"\\u2248 \\u8282\\u7701 $",
    hero_tokens_sub_suffix:"",
    hero_recall:"\\u53ec\\u56de\\u7f6e\\u4fe1\\u5ea6",
    hero_recall_sub:"\\u6700\\u8fd1 10 \\u6b21\\u53ec\\u56de\\u5747\\u503c",
    hero_latency:"\\u53ec\\u56de\\u5ef6\\u8fdf",
    hero_latency_sub:"\\u6700\\u8fd1 p95 \\u6d4b\\u91cf",
    hero_status:"\\u7cfb\\u7edf\\u72b6\\u6001",
    status_healthy:"\\u2713 \\u5065\\u5eb7",
    status_degraded:"! \\u964d\\u7ea7",
    status_unhealthy:"\\u2717 \\u5f02\\u5e38",
    status_cold:"\\u25CB \\u51b7\\u542f\\u52a8",
    status_bypass:"\\u26A0 \\u8bb0\\u5fc6\\u65c1\\u8def\\u6fc0\\u6d3b",
    status_sub_ok:"\\u6240\\u6709\\u68c0\\u67e5\\u5df2\\u901a\\u8fc7",
    status_sub_warn:"\\u90e8\\u5206\\u68c0\\u67e5\\u9700\\u8981\\u5173\\u6ce8",
    status_sub_fail:"\\u68c0\\u6d4b\\u5230\\u7cfb\\u7edf\\u95ee\\u9898",
    status_sub_cold:"\\u542f\\u52a8\\u4e2d",
    status_sub_bypass:"\\u667a\\u80fd\\u4f53\\u5728\\u65e0\\u8bb0\\u5fc6\\u6a21\\u5f0f\\u8fd0\\u884c",
    status_unknown:"\\u72b6\\u6001\\u672a\\u77e5",
    top_scene:"\\u6309\\u6570\\u91cf\\u6392\\u540d\\u7684\\u9876\\u90e8\\u573a\\u666f",
    mem_id:"\\u8bb0\\u5fc6 ID",
    type:"\\u7c7b\\u578b",
    scene:"\\u573a\\u666f",
    score:"\\u5206\\u6570",
    semantic:"\\u8bed\\u4e49",
    recency:"\\u65f6\\u95f4",
    scene_score:"\\u573a\\u666f",
    rank:"\\u7efc\\u5408\\u5206",
    namespace:"\\u547d\\u540d\\u7a7a\\u95f4",
    suppressed:"\\u5df2\\u6291\\u5236",
    backend:"\\u540e\\u7aef",
    status:"\\u72b6\\u6001",
    api_version:"API \\u7248\\u672c",
    engine:"\\u5f15\\u64ce",
    memories:"\\u8bb0\\u5fc6\\u6570",
    scenes:"\\u573a\\u666f\\u6570",
    conn_ok:"\\u5728\\u7ebf",
    conn_lost:"\\u5df2\\u65ad\\u5f00",
    bypass_banner:"\\u26A0 \\u672c\\u5730 API \\u670d\\u52a1\\u5668\\u5df2\\u65ad\\u5f00 \\u2014 \\u8bb0\\u5fc6\\u65c1\\u8def\\u6fc0\\u6d3b",
    override_ok:"\\u573a\\u666f\\u5df2\\u5207\\u6362\\u4e3a",
    override_fail:"\\u5207\\u6362\\u5931\\u8d25",
    heuristic:"\\u542f\\u53d1\\u5f0f",
    manual:"\\u624b\\u52a8",
    formula:"\\u5f97\\u5206 = (\\u8bed\\u4e49 \\u00D7 0.6) + (\\u65f6\\u95f4 \\u00D7 0.25) + (\\u573a\\u666f \\u00D7 0.15)",
  }
};

function t(key){var d=I18N[LANG]||I18N['en'];return d[key]||I18N['en'][key]||key}

function applyLang(){
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    el.textContent=t(el.getAttribute('data-i18n'));
  });
  document.getElementById('search-input').placeholder=t('search_placeholder');
  document.getElementById('lang-btn').textContent=LANG==='en'?'EN / \u4e2d':'\u4e2d / EN';
  document.getElementById('score-formula').innerHTML=t('formula');
  updateConnUI();
}

function toggleLang(){
  LANG=LANG==='en'?'zh':'en';
  localStorage.setItem('inspector_lang',LANG);
  applyLang();
  refreshAll();
}

function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
function safeC(s){return(s||'').replace(/[^a-zA-Z0-9_-]/g,'')}
function typeIc(t){return{preference:'&#x2764;',task_execution:'&#x26A1;',fact:'&#x1F4CC;',decision:'&#x2696;',observation:'&#x1F441;'}[safeC(t)]||'&#x1F4AD;'}
function nsIcon(ns){
  var icons={default:'&#x1F310;',openclaw:'&#x1F916;',personal:'&#x1F464;',team:'&#x1F465;'};
  var key=ns?ns.split('/')[0]:'default';
  return icons[key]||icons['default'];
}

async function fetchJSON(url){
  try{
    const start=performance.now();
    const r=await fetch(API+url);
    const elapsed=Math.round(performance.now()-start);
    if(url.includes('/recent')||url.includes('/search')) recallLatency=elapsed;
    if(!r.ok){return null}
    if(!apiConnected){apiConnected=true;updateConnUI()}
    return await r.json();
  }catch(e){
    if(apiConnected){apiConnected=false;updateConnUI()}
    return null;
  }
}

function updateConnUI(){
  const banner=document.getElementById('conn-banner');
  const connText=document.getElementById('conn-text');
  if(!apiConnected){
    document.body.classList.add('conn-lost');
    banner.innerHTML=t('bypass_banner');
    connText.textContent=t('conn_lost');
  }else{
    document.body.classList.remove('conn-lost');
    connText.textContent=t('conn_ok');
  }
}

function showToast(msg,type){
  const el=document.getElementById('override-toast');
  el.textContent=msg;
  el.className='override-toast '+type+' show';
  setTimeout(()=>{el.className='override-toast'},2500);
}

function statusDisplay(s){
  if(!apiConnected)return{text:t('status_bypass'),color:'var(--red)',sub:t('status_sub_bypass'),cls:'status-fail'};
  if(s==='ok')return{text:t('status_healthy'),color:'var(--green)',sub:t('status_sub_ok'),cls:''};
  if(s==='warning')return{text:t('status_degraded'),color:'var(--amber)',sub:t('status_sub_warn'),cls:''};
  if(s==='fail'||s==='error')return{text:t('status_unhealthy'),color:'var(--red)',sub:t('status_sub_fail'),cls:'status-fail'};
  if(s==='cold_start')return{text:t('status_cold'),color:'var(--text-m)',sub:t('status_sub_cold'),cls:''};
  return{text:esc(s||'-'),color:'var(--text-m)',sub:t('status_unknown'),cls:''};
}

function renderHero(memories,cells,scenes,status){
  const sd=statusDisplay(status);
  const mem=parseInt(memories)||0;
  const cel=parseInt(cells)||0;
  const tokens=Math.round(mem*97.5);
  const cost=(tokens*0.00003).toFixed(2);
  const avgRecall=recallScores.length>0?(recallScores.reduce((a,b)=>a+b,0)/recallScores.length).toFixed(2):'-';
  const rcColor=recallScores.length>0?'var(--green)':'var(--text-m)';
  const latColor=recallLatency<80?'var(--green)':recallLatency<150?'var(--amber)':'var(--red)';
  const latVal=recallLatency>0?recallLatency+'<span style="font-size:14px;font-weight:600">ms</span>':'-';
  document.getElementById('hero-stats').innerHTML=
    '<div class="hero-c"><div class="hero-l">'+t('hero_memories')+'</div><div class="hero-v">'+mem+'</div><div class="hero-s">'+t('hero_memories_sub')+'</div><div class="hero-i" style="background:var(--blue-bg)">&#x1F9E0;</div></div>'+
    '<div class="hero-c"><div class="hero-l">'+t('hero_cells')+'</div><div class="hero-v">'+cel+'</div><div class="hero-s">'+t('hero_cells_sub')+'</div><div class="hero-i" style="background:var(--purple-bg)">&#x2B21;</div></div>'+
    '<div class="hero-c"><div class="hero-l">'+t('hero_tokens')+'</div><div class="hero-v" style="color:var(--cyan)">'+tokens.toLocaleString()+'</div><div class="hero-s">'+t('hero_tokens_sub_prefix')+cost+t('hero_tokens_sub_suffix')+'</div><div class="hero-i" style="background:var(--cyan-bg)">&#x26A1;</div></div>'+
    '<div class="hero-c"><div class="hero-l">'+t('hero_recall')+'</div><div class="hero-v" style="color:'+rcColor+'">'+avgRecall+'</div><div class="hero-s">'+t('hero_recall_sub')+'</div><div class="hero-i" style="background:var(--green-bg)">&#x1F3AF;</div></div>'+
    '<div class="hero-c"><div class="hero-l">'+t('hero_latency')+'</div><div class="hero-v" style="color:'+latColor+'">'+latVal+'</div><div class="hero-s">'+t('hero_latency_sub')+'</div><div class="hero-i" style="background:var(--cyan-bg)">&#x23F1;</div></div>'+
    '<div class="hero-c '+sd.cls+'"><div class="hero-l">'+t('hero_status')+'</div><div class="hero-v" style="color:'+sd.color+'">'+sd.text+'</div><div class="hero-s">'+sd.sub+'</div><div class="hero-i" style="background:var(--amber-bg)">&#x2699;</div></div>';
}

async function loadChecklist(){
  const d=await fetchJSON('/api/inspector/checklist');
  if(!d){document.getElementById('checklist').innerHTML='<div class="empty">'+t('empty_load')+'</div>';return}
  document.getElementById('checklist').innerHTML=d.checks.map(c=>{
    const st=safeC(c.status);
    const ic=st==='ok'?'&#x2713;':st==='warning'?'!':st==='cold_start'?'&#x25CB;':'&#x2717;';
    return '<div class="chk-i '+st+'"><div class="chk-ic '+st+'">'+ic+'</div><div><div class="chk-t">'+esc(c.name)+'</div></div></div>';
  }).join('');
}

async function loadSummary(){
  const d=await fetchJSON('/api/inspector/memory-summary');
  const h=await fetchJSON('/api/inspector/health');
  if(!d)return;
  renderHero(d.total_memories||0,d.total_cells||0,d.total_scenes||0,h?h.status:'-');

  if(d.type_distribution&&Object.keys(d.type_distribution).length>0){
    const mx=Math.max(...Object.values(d.type_distribution),1);
    document.getElementById('type-dist').innerHTML=Object.entries(d.type_distribution).map(([k,v])=>
      '<div class="dr"><span class="dl">'+esc(k)+'</span><div class="dt"><div class="df tp" style="width:'+(parseFloat(v/mx)*100)+'%"></div></div><span class="dc">'+parseInt(v)+'</span></div>'
    ).join('');
  }else{document.getElementById('type-dist').innerHTML='<div class="empty">'+t('empty_data')+'</div>'}

  if(d.scene_distribution&&Object.keys(d.scene_distribution).length>0){
    const mx=Math.max(...Object.values(d.scene_distribution),1);
    document.getElementById('scene-dist').innerHTML=Object.entries(d.scene_distribution).map(([k,v])=>
      '<div class="dr"><span class="dl">'+esc(k||'(none)')+'</span><div class="dt"><div class="df sc" style="width:'+(parseFloat(v/mx)*100)+'%"></div></div><span class="dc">'+parseInt(v)+'</span></div>'
    ).join('');

    const topScene=Object.entries(d.scene_distribution).sort((a,b)=>b[1]-a[1])[0];
    if(topScene){
      const activeScene=sceneOverridden?overriddenScene:topScene[0];
      const srcLabel=sceneOverridden?t('manual'):t('heuristic');
      const srcCls=sceneOverridden?'manual':'heuristic';
      document.getElementById('scene-dynamics').innerHTML=
        '<div class="scene-wrap"><div class="scene-badge">'+esc(activeScene)+'</div><div class="scene-conf">'+t('top_scene')+'</div><span class="scene-source '+srcCls+'">'+srcLabel+'</span></div>'+
        '<button class="override-btn" onclick="toggleSceneOpts()">'+t('override_scene')+'</button>'+
        '<div class="override-opts" id="scene-override-opts"></div>';
      renderSceneOpts(Object.keys(d.scene_distribution),activeScene);
    }
  }else{document.getElementById('scene-dist').innerHTML='<div class="empty">'+t('empty_data')+'</div>'}
}

function renderSceneOpts(scenes,active){
  const el=document.getElementById('scene-override-opts');
  if(!el)return;
  el.innerHTML=scenes.map(s=>
    '<span class="override-opt'+(s===active?' active':'')+'" data-scene="'+esc(s)+'">'+esc(s)+'</span>'
  ).join('');
  el.onclick=function(e){
    if(e.target.classList.contains('override-opt')){
      doSceneOverride(e.target,e.target.dataset.scene);
    }
  };
}

window.toggleSceneOpts=function(){
  const el=document.getElementById('scene-override-opts');
  if(el)el.classList.toggle('show');
};

async function doSceneOverride(btn,scene){
  try{
    const r=await fetch(API+'/session/scene_override',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({scene:scene})});
    if(r.ok){
      sceneOverridden=true;
      overriddenScene=scene;
      showToast(t('override_ok')+' '+scene,'ok');
      const el=document.getElementById('scene-override-opts');
      if(el){el.classList.remove('show');el.querySelectorAll('.override-opt').forEach(o=>o.classList.remove('active'));btn.classList.add('active')}
      const badge=document.querySelector('.scene-badge');
      if(badge)badge.textContent=scene;
      const src=document.querySelector('.scene-source');
      if(src){src.textContent=t('manual');src.className='scene-source manual'}
    }else{showToast(t('override_fail'),'err')}
  }catch(e){showToast(t('override_fail'),'err')}
}

async function loadHealth(){
  const d=await fetchJSON('/api/inspector/health');
  if(!d)return;
  document.getElementById('system-info').innerHTML=[
    [t('backend'),d.backend||'openmemo'],[t('status'),d.status||'-'],
    [t('api_version'),d.api_version||'-'],[t('engine'),d.engine_version||'-'],
    [t('memories'),d.total_memories||0],[t('scenes'),d.total_scenes||0],
  ].map(([k,v])=>'<div class="info-i"><span class="info-k">'+esc(k)+'</span><span class="info-v">'+esc(String(v))+'</span></div>').join('');
}

function renderTimelineItem(m,idx){
  const content=m.content||m.text||'';
  const scene=m.scene||'';
  const mtype=m.memory_type||m.cell_type||m.type||'';
  const st=safeC(mtype);
  const score=m.score!=null?parseFloat(m.score).toFixed(2):'';
  if(m.score!=null) recallScores.push(parseFloat(m.score));
  const isSup=m.suppressed===true;
  const supCls=isSup?' suppressed':'';
  const ns=m.namespace||m.ns||'';
  let meta='';
  if(scene) meta+='<span class="pill sc">'+esc(scene)+'</span>';
  if(mtype) meta+='<span class="pill tp">'+esc(mtype)+'</span>';
  if(score) meta+='<span class="pill sr">'+score+'</span>';
  if(ns) meta+='<span class="ns-icon"><span class="ns-dot"></span>'+nsIcon(ns)+' '+esc(ns)+'</span>';
  if(isSup) meta+='<span class="pill suppressed-pill">'+t('suppressed')+'</span>';
  const id=m.id||m.memory_id||'mem_'+(idx||0);
  const sem=m.semantic_score!=null?parseFloat(m.semantic_score).toFixed(2):(m.sem!=null?parseFloat(m.sem).toFixed(2):'');
  const rec=m.recency_score!=null?parseFloat(m.recency_score).toFixed(2):(m.rec!=null?parseFloat(m.rec).toFixed(2):'');
  const scn=m.scene_score!=null?parseFloat(m.scene_score).toFixed(2):(m.scn!=null?parseFloat(m.scn).toFixed(2):'');
  let scoreRow='';
  if(score){
    scoreRow='<div class="tl-score">';
    scoreRow+='<div class="tl-score-i">'+t('rank')+': <b>'+score+'</b></div>';
    if(sem) scoreRow+='<div class="tl-score-i">'+t('semantic')+': <b>'+sem+'</b> &times;0.6</div>';
    if(rec) scoreRow+='<div class="tl-score-i">'+t('recency')+': <b>'+rec+'</b> &times;0.25</div>';
    if(scn) scoreRow+='<div class="tl-score-i">'+t('scene_score')+': <b>'+scn+'</b> &times;0.15</div>';
    scoreRow+='</div>';
  }
  return '<div class="tl-i'+supCls+'" onclick="toggleExp('+idx+')">'+
    '<div class="tl-dot '+st+'">'+typeIc(st)+'</div>'+
    '<div class="tl-body">'+
      '<div class="tl-text">'+esc(content.substring(0,200))+'</div>'+
      '<div class="tl-meta">'+meta+'</div>'+
      scoreRow+
      '<div class="tl-expand" id="exp-'+idx+'">'+
        '<div class="exp-r"><span class="exp-k">'+t('mem_id')+'</span><span class="exp-v mono">'+esc(String(id))+'</span></div>'+
        '<div class="exp-r"><span class="exp-k">'+t('type')+'</span><span class="exp-v">'+esc(mtype)+'</span></div>'+
        '<div class="exp-r"><span class="exp-k">'+t('scene')+'</span><span class="exp-v">'+esc(scene)+'</span></div>'+
        '<div class="exp-r"><span class="exp-k">'+t('namespace')+'</span><span class="exp-v">'+esc(ns||'default')+'</span></div>'+
        (score?'<div class="exp-r"><span class="exp-k">'+t('score')+'</span><span class="exp-v">'+score+'</span></div>':'')+
        (isSup?'<div class="exp-r"><span class="exp-k">'+t('suppressed')+'</span><span class="exp-v" style="color:var(--red)">true</span></div>':'')+
      '</div>'+
    '</div>'+
  '</div>';
}

window.toggleExp=function(i){
  const el=document.getElementById('exp-'+i);
  if(el) el.classList.toggle('show');
};

async function loadRecent(){
  recallScores=[];
  const d=await fetchJSON('/api/inspector/recent');
  const el=document.getElementById('recent-writes');
  if(!d||!d.recent||d.recent.length===0){el.innerHTML='<div class="empty">'+t('empty_cold')+'</div>';return}
  el.innerHTML=d.recent.map((m,i)=>renderTimelineItem(m,i)).join('');
}

async function loadVersion(){
  const d=await fetchJSON('/version');
  if(!d)return;
  document.getElementById('update-status').innerHTML=[
    ['OpenMemo Core',d.latest_core],['Adapter',d.latest_adapter],['Schema','v'+d.schema_version],
  ].map(([k,v])=>'<div class="info-i"><span class="info-k">'+esc(k)+'</span><span class="info-v">'+esc(String(v))+'</span></div>').join('');
  document.getElementById('header-version').textContent='v'+d.latest_core;
}

let searchTimer;
document.getElementById('search-input').addEventListener('input',function(){
  clearTimeout(searchTimer);
  const q=this.value.trim();
  if(q.length<2){document.getElementById('search-results').innerHTML='';return}
  searchTimer=setTimeout(()=>doSearch(q),300);
});
async function doSearch(q){
  const d=await fetchJSON('/api/inspector/search?q='+encodeURIComponent(q));
  const el=document.getElementById('search-results');
  if(!d||!d.results||d.results.length===0){el.innerHTML='<div class="empty">'+t('no_results')+' &ldquo;'+esc(q)+'&rdquo;</div>';return}
  el.innerHTML='<div class="tl">'+d.results.map((m,i)=>renderTimelineItem(m,1000+i)).join('')+'</div>';
}

async function refreshAll(){
  applyLang();
  await Promise.all([loadChecklist(),loadSummary(),loadHealth(),loadRecent(),loadVersion()]);
}
refreshAll();
setInterval(refreshAll,30000);
</script>
</body>
</html>"""
