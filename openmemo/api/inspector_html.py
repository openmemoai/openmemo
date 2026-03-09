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
.live{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text-m)}
.dot-live{width:6px;height:6px;border-radius:50%;background:var(--green);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}

.layer-label{font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--text-m);padding:24px 28px 8px;opacity:0.6}
.page{max-width:1360px;margin:0 auto;padding:0 28px 60px}

.hero{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:4px}
.hero-c{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);padding:18px 20px;position:relative;overflow:hidden;transition:all .2s}
.hero-c:hover{border-color:var(--border-hover);transform:translateY(-1px)}
.hero-l{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.8px;color:var(--text-m);margin-bottom:6px}
.hero-v{font-size:28px;font-weight:800;letter-spacing:-1px;line-height:1.1}
.hero-s{font-size:11px;color:var(--text-m);margin-top:3px}
.hero-i{position:absolute;top:14px;right:16px;width:34px;height:34px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:15px}

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

@media(max-width:1024px){.hero{grid-template-columns:repeat(3,1fr)}.chk{grid-template-columns:1fr 1fr}}
@media(max-width:768px){.hero{grid-template-columns:1fr 1fr}.g,.g-60-40{grid-template-columns:1fr}.chk{grid-template-columns:1fr}.info-g{grid-template-columns:1fr}.info-i:nth-child(even){padding-left:0;border-left:none}.info-i:nth-child(odd){padding-right:0}.page{padding:0 16px 40px}.header{padding:12px 16px}}
</style>
</head>
<body>

<div class="header">
  <div class="header-l">
    <div class="logo">M</div>
    <h1>Memory Inspector</h1>
  </div>
  <div class="header-r">
    <span class="ver" id="header-version"></span>
    <span class="live"><span class="dot-live"></span> Live</span>
  </div>
</div>

<div class="page">

<div class="layer-label">Value Layer</div>
<div class="hero" id="hero-stats"></div>

<div class="layer-label">Intelligence Layer</div>
<div class="g">
  <div class="c gf">
    <div class="ct"><span class="d" style="background:var(--green)"></span> System Health</div>
    <div class="chk" id="checklist"></div>
  </div>
</div>

<div class="g g-60-40">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--accent)"></span> Scene Dynamics</div>
    <div id="scene-dynamics"><div class="empty">Scene data not available</div></div>
  </div>
  <div class="c" style="display:flex;flex-direction:column;gap:12px">
    <div>
      <div class="ct"><span class="d" style="background:var(--accent)"></span> Type Distribution</div>
      <div id="type-dist"><div class="empty">No data yet</div></div>
    </div>
    <div>
      <div class="ct"><span class="d" style="background:var(--green)"></span> Scene Distribution</div>
      <div id="scene-dist"><div class="empty">No data yet</div></div>
    </div>
  </div>
</div>

<div class="layer-label">Decision Layer</div>
<div class="g">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--cyan)"></span> Task Pre-Check</div>
    <div class="task-box" id="task-check"><div class="empty">No task check data available</div></div>
  </div>
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--amber)"></span> System Info</div>
    <div class="info-g" id="system-info"></div>
  </div>
</div>

<div class="layer-label">Memory Layer</div>
<div class="g">
  <div class="c gf">
    <div class="ct"><span class="d" style="background:var(--blue)"></span> Memory Search</div>
    <div class="search-w">
      <span class="search-ic">&#x1F50D;</span>
      <input type="text" class="search-in" id="search-input" placeholder="Search through agent memories..." />
    </div>
    <div class="search-res" id="search-results"></div>
  </div>
</div>

<div class="g g-60-40">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--cyan)"></span> Memory Stream</div>
    <div class="tl" id="recent-writes"></div>
  </div>
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--purple)"></span> Memory Growth</div>
    <div class="growth-chart" id="growth-chart"><div class="empty" style="width:100%">Growth data available with extended API</div></div>
    <div class="snap-btn" title="Save full agent memory state for debugging or replay. Available in Pro plan.">
      <span class="snap-ic">&#x1F4F8;</span>
      <div class="snap-t">
        <div class="name">Memory Snapshot</div>
        <div class="desc">Save full agent memory state</div>
      </div>
      <span class="snap-lock">PRO</span>
    </div>
  </div>
</div>

<div class="g">
  <div class="c">
    <div class="ct"><span class="d" style="background:var(--accent)"></span> Version</div>
    <div id="update-status"></div>
  </div>
</div>

</div>

<script>
const API='';
let expandIdx=-1;
let recallScores=[];

function esc(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML}
function safeC(s){return(s||'').replace(/[^a-zA-Z0-9_-]/g,'')}
function typeIc(t){return{preference:'&#x2764;',task_execution:'&#x26A1;',fact:'&#x1F4CC;',decision:'&#x2696;',observation:'&#x1F441;'}[safeC(t)]||'&#x1F4AD;'}
async function fetchJSON(url){try{const r=await fetch(API+url);return await r.json()}catch(e){return null}}

function statusDisplay(s){
  if(s==='ok')return{text:'&#x2713; Healthy',color:'var(--green)',sub:'all checks passed'};
  if(s==='warning')return{text:'! Degraded',color:'var(--amber)',sub:'some checks need attention'};
  if(s==='fail'||s==='error')return{text:'&#x2717; Unhealthy',color:'var(--red)',sub:'system issues detected'};
  if(s==='cold_start')return{text:'&#x25CB; Cold Start',color:'var(--text-m)',sub:'warming up'};
  return{text:esc(s||'-'),color:'var(--text-m)',sub:'status unknown'};
}

function renderHero(memories,cells,scenes,status){
  const sd=statusDisplay(status);
  const mem=parseInt(memories)||0;
  const cel=parseInt(cells)||0;
  const tokens=Math.round(mem*97.5);
  const cost=(tokens*0.00003).toFixed(2);
  const avgRecall=recallScores.length>0?(recallScores.reduce((a,b)=>a+b,0)/recallScores.length).toFixed(2):'-';
  const rcColor=recallScores.length>0?'var(--green)':'var(--text-m)';
  document.getElementById('hero-stats').innerHTML=
    '<div class="hero-c"><div class="hero-l">Total Memories</div><div class="hero-v">'+mem+'</div><div class="hero-s">stored memory entries</div><div class="hero-i" style="background:var(--blue-bg)">&#x1F9E0;</div></div>'+
    '<div class="hero-c"><div class="hero-l">Memory Cells</div><div class="hero-v">'+cel+'</div><div class="hero-s">atomic knowledge units</div><div class="hero-i" style="background:var(--purple-bg)">&#x2B21;</div></div>'+
    '<div class="hero-c"><div class="hero-l">Context Tokens</div><div class="hero-v" style="color:var(--cyan)">'+tokens.toLocaleString()+'</div><div class="hero-s" title="tokens saved by injecting structured memory instead of full context history">&#x2248; $'+cost+' saved</div><div class="hero-i" style="background:var(--cyan-bg)">&#x26A1;</div></div>'+
    '<div class="hero-c"><div class="hero-l">Recall Confidence</div><div class="hero-v" style="color:'+rcColor+'">'+avgRecall+'</div><div class="hero-s">avg semantic recall score</div><div class="hero-i" style="background:var(--green-bg)">&#x1F3AF;</div></div>'+
    '<div class="hero-c"><div class="hero-l">System Status</div><div class="hero-v" style="color:'+sd.color+'">'+sd.text+'</div><div class="hero-s">'+sd.sub+'</div><div class="hero-i" style="background:var(--amber-bg)">&#x2699;</div></div>';
}

async function loadChecklist(){
  const d=await fetchJSON('/api/inspector/checklist');
  if(!d){document.getElementById('checklist').innerHTML='<div class="empty">Could not load</div>';return}
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
  }else{document.getElementById('type-dist').innerHTML='<div class="empty">No data yet</div>'}

  if(d.scene_distribution&&Object.keys(d.scene_distribution).length>0){
    const mx=Math.max(...Object.values(d.scene_distribution),1);
    document.getElementById('scene-dist').innerHTML=Object.entries(d.scene_distribution).map(([k,v])=>
      '<div class="dr"><span class="dl">'+esc(k||'(none)')+'</span><div class="dt"><div class="df sc" style="width:'+(parseFloat(v/mx)*100)+'%"></div></div><span class="dc">'+parseInt(v)+'</span></div>'
    ).join('');

    const topScene=Object.entries(d.scene_distribution).sort((a,b)=>b[1]-a[1])[0];
    if(topScene){
      document.getElementById('scene-dynamics').innerHTML=
        '<div class="scene-wrap"><div class="scene-badge">'+esc(topScene[0])+'</div><div class="scene-conf">Top scene by volume</div></div>';
    }
  }else{document.getElementById('scene-dist').innerHTML='<div class="empty">No data yet</div>'}
}

async function loadHealth(){
  const d=await fetchJSON('/api/inspector/health');
  if(!d)return;
  document.getElementById('system-info').innerHTML=[
    ['Backend',d.backend||'openmemo'],['Status',d.status||'-'],
    ['API Version',d.api_version||'-'],['Engine',d.engine_version||'-'],
    ['Memories',d.total_memories||0],['Scenes',d.total_scenes||0],
  ].map(([k,v])=>'<div class="info-i"><span class="info-k">'+esc(k)+'</span><span class="info-v">'+esc(String(v))+'</span></div>').join('');
}

function renderTimelineItem(m,idx){
  const content=m.content||m.text||'';
  const scene=m.scene||'';
  const mtype=m.memory_type||m.cell_type||m.type||'';
  const st=safeC(mtype);
  const score=m.score!=null?parseFloat(m.score).toFixed(2):'';
  if(m.score!=null) recallScores.push(parseFloat(m.score));
  let meta='';
  if(scene) meta+='<span class="pill sc">'+esc(scene)+'</span>';
  if(mtype) meta+='<span class="pill tp">'+esc(mtype)+'</span>';
  if(score) meta+='<span class="pill sr">'+score+'</span>';
  const id=m.id||m.memory_id||'mem_'+(idx||0);
  return '<div class="tl-i" onclick="toggleExp('+idx+')">'+
    '<div class="tl-dot '+st+'">'+typeIc(st)+'</div>'+
    '<div class="tl-body">'+
      '<div class="tl-text">'+esc(content.substring(0,200))+'</div>'+
      '<div class="tl-meta">'+meta+'</div>'+
      '<div class="tl-expand" id="exp-'+idx+'">'+
        '<div class="exp-r"><span class="exp-k">Memory ID</span><span class="exp-v mono">'+esc(String(id))+'</span></div>'+
        '<div class="exp-r"><span class="exp-k">Type</span><span class="exp-v">'+esc(mtype)+'</span></div>'+
        '<div class="exp-r"><span class="exp-k">Scene</span><span class="exp-v">'+esc(scene)+'</span></div>'+
        (score?'<div class="exp-r"><span class="exp-k">Score</span><span class="exp-v">'+score+'</span></div>':'')+
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
  if(!d||!d.recent||d.recent.length===0){el.innerHTML='<div class="empty">No memories yet &mdash; cold start</div>';return}
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
  if(!d||!d.results||d.results.length===0){el.innerHTML='<div class="empty">No results for &ldquo;'+esc(q)+'&rdquo;</div>';return}
  el.innerHTML='<div class="tl">'+d.results.map((m,i)=>renderTimelineItem(m,1000+i)).join('')+'</div>';
}

async function refreshAll(){
  await Promise.all([loadChecklist(),loadSummary(),loadHealth(),loadRecent(),loadVersion()]);
}
refreshAll();
setInterval(refreshAll,5000);
</script>
</body>
</html>"""
