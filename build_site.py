#!/usr/bin/env python3
"""Build a self-contained interactive explorer (index.html) with embedded data."""
import os, json, re

ROOT = os.path.dirname(os.path.abspath(__file__))
items = json.load(open(os.path.join(ROOT, "data", "items.json"), encoding="utf-8"))

# Treat an item as a "recording/song" if it has a performer or a tape name or audio.
def is_song(r):
    return bool(r.get("performer") or r.get("tape_name") or r.get("has_audio"))

songs = [r for r in items if is_song(r)]

# normalize a 4-digit year out of the date field
def year_of(r):
    d = str(r.get("date", ""))
    m = re.search(r"(19\d{2})", d)
    return int(m.group(1)) if m else None

for r in songs:
    r["year"] = year_of(r)

# Group multi-part reels under one descriptive name:
#   "Tape 52 - Songs of the Underworld (1)" + "Tape 53 - ... (2)" -> "Songs of the Underworld"
#   "Tape 01 - Anti-Hasidic I" + "Tape 02 - Anti-Hasidic II"      -> "Anti-Hasidic"
def tape_group(t):
    if not t:
        return ""
    s = re.sub(r"^\s*Tape\s+\d+\s*[-:]\s*", "", t)   # drop "Tape 52 - "
    s = re.sub(r"\s*\(\d+\)\s*$", "", s)              # drop trailing "(1)"
    m = re.search(r"\s+([IVX]+)\s*$", s)             # drop trailing roman part-number
    if m and not s[:m.start()].rstrip().endswith("War"):  # ...but keep "World War II"
        s = s[:m.start()]
    s = re.sub(r"\s*[-–:]\s*$", "", s)               # tidy trailing punctuation
    return s.strip()

for r in songs:
    r["tape_group"] = tape_group(r.get("tape_name", ""))

payload = json.dumps(songs, ensure_ascii=False, separators=(",", ":"))
allpayload = json.dumps(items, ensure_ascii=False, separators=(",", ":"))

# Curated album -> per-track best search query (tuned against the data; "|" = OR).
# Built to hold more Ruth Rubin albums later; for now just the Folkways LP.
ALBUMS = [{
    "name": "Jewish Children's Songs and Games (Folkways FC 7224, 1957)",
    "links": [
        ["YIVO", "https://ruthrubin.yivo.org/items/show/2268"],
        ["Smithsonian Folkways", "https://folkways.si.edu/ruth-rubin-and-pete-seeger/jewish-childrens-songs-and-games/judaica/music/album/smithsonian"],
        ["Liner notes (PDF)", "https://folkways-media.si.edu/docs/folkways/artwork/FW07224.pdf"],
        ["YouTube", "https://www.youtube.com/playlist?list=OLAK5uy_mQi01us_X_btTMQDYGIAep_2dz43kziX4"],
        ["Spotify", "https://open.spotify.com/album/2h5Lu8DjzJMVx9z5jFsjm3"],
    ],
    "songs": [
        {"n": "101", "title": "Shpits-Boydim",          "by": "Ruth Rubin & Pete Seeger", "q": "shpits boyd"},
        {"n": "102", "title": "Du Maydeleh Du Fines",   "by": "Ruth Rubin & Pete Seeger", "q": "meydele du"},
        {"n": "103", "title": "Oksn",                   "by": "Ruth Rubin & Pete Seeger", "q": "oksn"},
        {"n": "104", "title": "Lomir Zich Ibberbetn",   "by": "Ruth Rubin",               "q": "iberbetn"},
        {"n": "105", "title": "Amol Iz Geven a Myseh",  "by": "Ruth Rubin",               "q": "geven a mayse"},
        {"n": "106", "title": "Kestelech",              "by": "Ruth Rubin & Pete Seeger", "q": "kestele"},
        {"n": "107", "title": "Homntashn",              "by": "Ruth Rubin & Pete Seeger", "q": "homen"},
        {"n": "201", "title": "Shayn Bin Ich, Shayn",   "by": "Ruth Rubin",               "q": "sheyn bin ikh"},
        {"n": "202", "title": "Beker Lid",              "by": "Ruth Rubin & Pete Seeger", "q": "beker"},
        {"n": "203", "title": "A Genayveh",             "by": "Ruth Rubin & Pete Seeger", "q": "bay mayn rebe"},
        {"n": "204", "title": "Michalku",               "by": "Ruth Rubin & Pete Seeger", "q": "mikhalku"},
        {"n": "205", "title": "By Dem Shtetl",          "by": "Ruth Rubin",               "q": "bay dem shtetl"},
        {"n": "206", "title": "Yomi, Yomi",             "by": "Ruth Rubin",               "q": "yome|yomi"},
        {"n": "207", "title": "Tonts, Tonts",           "by": "Ruth Rubin & Pete Seeger", "q": "tants, tants"},
    ],
}]
albumpayload = json.dumps(ALBUMS, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Ruth Rubin Sound Archive — Data Explorer</title>
<style>
  :root{
    --bg:#1a1410; --panel:#241c16; --panel2:#2e241c; --ink:#f3e9da; --muted:#b9a888;
    --accent:#d9a441; --accent2:#c0612f; --line:#3a2e24; --good:#7fae6e;
  }
  *{box-sizing:border-box}
  body{margin:0;font-family:'Iowan Old Style',Georgia,'Times New Roman',serif;
       background:var(--bg);color:var(--ink);line-height:1.45;padding-bottom:72px}
  header{padding:32px 24px 18px;border-bottom:1px solid var(--line);
         background:linear-gradient(180deg,#241c16,#1a1410)}
  h1{margin:0 0 4px;font-size:30px;letter-spacing:.3px}
  h1 .yi{color:var(--accent)}
  .sub{color:var(--muted);font-size:15px;max-width:760px}
  .wrap{max-width:1180px;margin:0 auto;padding:0 24px}
  section{padding:26px 0;border-bottom:1px solid var(--line)}
  h2{font-size:20px;margin:0 0 14px;color:var(--accent)}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
  .card .n{font-size:30px;font-weight:700;color:var(--accent)}
  .card .l{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}
  .charts{display:grid;grid-template-columns:1fr 1fr;gap:22px}
  @media(max-width:820px){.charts{grid-template-columns:1fr}}
  .chart{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
  .chart h3{margin:0 0 12px;font-size:15px;color:var(--ink);font-weight:600}
  .bar-row{display:flex;align-items:center;gap:8px;margin:3px 0;font-size:13px;cursor:pointer}
  .bar-row:hover .bar{filter:brightness(1.2)}
  .bar-lab{width:150px;flex:0 0 150px;text-align:right;color:var(--muted);
           white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bar-track{flex:1;background:#0e0a07;border-radius:4px;overflow:hidden}
  .bar{height:16px;background:linear-gradient(90deg,var(--accent2),var(--accent));border-radius:4px}
  .bar-val{width:42px;flex:0 0 42px;color:var(--muted);font-variant-numeric:tabular-nums}
  .expand{margin-top:10px;background:var(--panel2);border:1px solid var(--line);color:var(--accent);
          border-radius:6px;padding:5px 11px;font-size:12px;cursor:pointer;font-family:inherit}
  .expand:hover{background:var(--accent);color:#1a1410;border-color:var(--accent)}
  /* timeline */
  svg{display:block;width:100%;height:auto}
  .tl-bar{fill:var(--accent);cursor:pointer}
  .tl-bar:hover{fill:var(--accent2)}
  .axis{stroke:var(--line)}
  .axislab{fill:var(--muted);font-size:11px}
  /* album browser */
  .albumbar{background:linear-gradient(180deg,#2e241c,#241c16);border:1px solid var(--accent);
            border-radius:10px;padding:14px 16px;margin-bottom:16px;display:flex;flex-wrap:wrap;
            gap:12px 16px;align-items:center}
  .albumbar .ab-h{font-size:15px;color:var(--accent);font-weight:600}
  .albumbar .ab-sub{font-size:13px;color:var(--muted);max-width:340px}
  .albumbar select{min-width:200px}
  .ab-info{font-size:13px;color:var(--muted)}
  .ab-info b{color:var(--ink)}
  .ab-info a{color:var(--accent);text-decoration:none}
  /* controls */
  .controls{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:14px}
  input[type=search],select{background:var(--panel);color:var(--ink);border:1px solid var(--line);
        border-radius:8px;padding:9px 11px;font-size:14px;font-family:inherit}
  input[type=search]{flex:1;min-width:220px}
  .chip{background:var(--panel2);border:1px solid var(--line);color:var(--muted);
        border-radius:20px;padding:5px 12px;font-size:12px;cursor:pointer}
  .chip.on{background:var(--accent);color:#1a1410;border-color:var(--accent);font-weight:600}
  .count{color:var(--muted);font-size:13px;margin-left:auto}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
  th{position:sticky;top:0;background:var(--panel2);color:var(--accent);cursor:pointer;
     user-select:none;font-size:12px;text-transform:uppercase;letter-spacing:.5px}
  th:hover{color:var(--ink)}
  tr:hover td{background:#211913}
  td a{color:var(--accent);text-decoration:none}
  td a:hover{text-decoration:underline}
  .tablewrap{max-height:680px;overflow:auto;border:1px solid var(--line);border-radius:10px}
  .play{background:var(--accent);border:none;color:#1a1410;width:26px;height:26px;border-radius:50%;
        cursor:pointer;font-size:12px;line-height:1}
  .play.playing{background:var(--good)}
  .muted{color:var(--muted)}
  #nowbar{position:fixed;left:0;right:0;bottom:0;z-index:60;display:none;align-items:center;gap:14px;
          padding:9px 18px;background:var(--panel2);border-top:1px solid var(--line);
          box-shadow:0 -6px 18px rgba(0,0,0,.35)}
  #nowbar.show{display:flex}
  #nowbar .npt{flex:0 1 auto;max-width:30%;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
               color:var(--ink);font-size:14px}
  #nowbar .npt b{color:var(--accent)}
  #nowbar audio{flex:1;min-width:160px;height:36px}
  #nowbar .spd{display:flex;gap:4px;align-items:center;color:var(--muted);font-size:12px;flex:0 0 auto}
  .sbtn{background:var(--panel);border:1px solid var(--line);color:var(--muted);border-radius:6px;
        padding:4px 7px;font-size:12px;cursor:pointer;font-family:inherit}
  .sbtn:hover{color:var(--ink)}
  .sbtn.on{background:var(--accent);color:#1a1410;border-color:var(--accent);font-weight:700}
  @media(max-width:700px){#nowbar .npt{display:none}}
  footer{padding:26px 24px;color:var(--muted);font-size:13px;text-align:center}
  footer a{color:var(--accent)}
  .yi-note{font-size:12px;color:var(--muted);margin-top:6px}
</style>
</head>
<body>
<header><div class="wrap">
  <h1>The <span class="yi">Ruth Rubin</span> Sound Archive — Data Explorer</h1>
  <div class="sub">An interactive view of the YIVO field-recording collection of Yiddish folksong
  gathered by Ruth Rubin (1946–1970s). Click any bar to filter. Press ▶ to listen.</div>
  <div class="yi-note" id="builtline"></div>
</div></header>

<div class="wrap">
  <section>
    <h2>At a glance</h2>
    <div class="cards" id="cards"></div>
  </section>

  <section>
    <h2>Recordings over time</h2>
    <div class="chart"><div id="timeline"></div></div>
  </section>

  <section>
    <h2>Who & what was recorded</h2>
    <div class="charts">
      <div class="chart"><h3>Most-recorded performers</h3><div id="performers"></div></div>
      <div class="chart"><h3>Genres</h3><div id="genres"></div></div>
      <div class="chart"><h3>Where it was recorded</h3><div id="locations"></div></div>
      <div class="chart"><h3>Songs per tape (multi-part reels combined)</h3><div id="tapes"></div></div>
      <div class="chart"><h3>Performer gender</h3><div id="gender"></div></div>
    </div>
  </section>

  <section>
    <h2>Explore every recording</h2>
    <div class="albumbar">
      <div>
        <div class="ab-h">🎼 Trace an album to its field recordings</div>
        <div class="ab-sub">Pick a track from a Ruth Rubin album to surface the archival
          recordings that may have informed it.</div>
      </div>
      <select id="albumSel"></select>
      <select id="songSel"></select>
      <span class="ab-info" id="albumInfo"></span>
    </div>
    <div class="controls">
      <input type="search" id="q" placeholder="Search title, performer, genre, location, lyricist…">
      <select id="fGenre"></select>
      <select id="fLoc"></select>
      <select id="fTape"></select>
      <select id="fGender"></select>
      <select id="fYear"></select>
      <span class="chip" id="fAudio">▶ has audio</span>
      <span class="chip" id="fClear">✕ clear</span>
      <span class="count" id="count"></span>
    </div>
    <div class="tablewrap">
      <table>
        <thead><tr id="head"></tr></thead>
        <tbody id="rows"></tbody>
      </table>
    </div>
  </section>
</div>

<footer>
  Built from <span id="srccount"></span> public item pages at
  <a href="https://ruthrubin.yivo.org/" target="_blank">ruthrubin.yivo.org</a>.
  Data &amp; recordings © YIVO Institute for Jewish Research. Explorer is an unofficial research aid.
</footer>

<div id="nowbar">
  <div class="npt" id="npTitle">—</div>
  <audio id="player" controls preload="none"></audio>
  <div class="spd">Speed:
    <button class="sbtn" data-r="0.5">0.5&times;</button>
    <button class="sbtn" data-r="0.75">0.75&times;</button>
    <button class="sbtn on" data-r="1">1&times;</button>
    <button class="sbtn" data-r="1.25">1.25&times;</button>
    <button class="sbtn" data-r="1.5">1.5&times;</button>
  </div>
</div>
<script>
const SONGS = __SONGS__;
const TOTAL_ITEMS = __NITEMS__;
const ALBUMS = __ALBUMS__;
document.getElementById('srccount').textContent = TOTAL_ITEMS.toLocaleString();

// ---------- helpers ----------
const $ = s => document.querySelector(s);
const norm = s => (s||'').toString().trim();
function tally(field, opt={}){
  const m = new Map();
  for(const r of SONGS){
    let v = norm(r[field]);
    if(!v){ if(opt.includeBlank) v='(unknown)'; else continue; }
    m.set(v,(m.get(v)||0)+1);
  }
  return [...m.entries()].sort((a,b)=>b[1]-a[1]);
}
// each chart shows a default number of bars with a button to expand to the top 50
let CHARTS={}; const expanded={};
function drawChart(elId){
  const c=CHARTS[elId]; const el=$('#'+elId); el.innerHTML='';
  const lim=expanded[elId]?Math.min(50,c.data.length):c.def;
  const top=Math.max(...c.data.map(d=>d[1]),1);
  const list=document.createElement('div');
  for(const [lab,n] of c.data.slice(0,lim)){
    const row=document.createElement('div'); row.className='bar-row';
    row.innerHTML=`<div class="bar-lab" title="${esc(lab)}">${esc(lab)}</div>
      <div class="bar-track"><div class="bar" style="width:${(n/top*100).toFixed(1)}%"></div></div>
      <div class="bar-val">${n}</div>`;
    row.onclick=()=>{ const p = c.kind==='genre'?{genre:lab}
        : c.kind==='loc'?{loc:lab}
        : c.kind==='gender'?{gender:lab}
        : {q:lab};
      update(p); scrollToTable(); };
    list.appendChild(row);
  }
  el.appendChild(list);
  if(c.data.length>c.def){
    const btn=document.createElement('button'); btn.className='expand';
    const cap=Math.min(50,c.data.length);
    btn.textContent=expanded[elId]?`▴ Show top ${c.def}`:`▾ Show top ${cap} of ${c.data.length}`;
    btn.onclick=()=>{expanded[elId]=!expanded[elId];drawChart(elId);};
    el.appendChild(btn);
  }
}
function esc(s){return (s||'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

// ---------- summary cards ----------
const withAudio = SONGS.filter(r=>r.has_audio).length;
const years = SONGS.map(r=>r.year).filter(Boolean);
const cards=[
  ['Recordings', SONGS.length],
  ['With audio', withAudio],
  ['Performers', tally('performer').length],
  ['Genres', tally('genre').length],
  ['Locations', tally('location').length],
  ['Years', years.length? Math.min(...years)+'–'+Math.max(...years):'—'],
];
$('#cards').innerHTML=cards.map(([l,n])=>`<div class="card"><div class="n">${typeof n==='number'?n.toLocaleString():n}</div><div class="l">${l}</div></div>`).join('');

// ---------- timeline ----------
(function(){
  const yc=new Map();
  for(const y of years) yc.set(y,(yc.get(y)||0)+1);
  if(!yc.size){return;}
  const ys=[...yc.keys()].sort((a,b)=>a-b);
  const y0=Math.min(...ys), y1=Math.max(...ys);
  const W=1100,H=260,pad=34,left=40;
  const bw=(W-left-10)/(y1-y0+1);
  const mx=Math.max(...yc.values());
  let s=`<svg viewBox="0 0 ${W} ${H}">`;
  // y gridlines
  for(let g=0;g<=mx;g+=Math.ceil(mx/4)){
    const yy=H-pad-(g/mx)*(H-2*pad);
    s+=`<line class="axis" x1="${left}" y1="${yy}" x2="${W-6}" y2="${yy}"/>`;
    s+=`<text class="axislab" x="2" y="${yy+3}">${g}</text>`;
  }
  for(let y=y0;y<=y1;y++){
    const n=yc.get(y)||0;
    const h=(n/mx)*(H-2*pad);
    const x=left+(y-y0)*bw;
    s+=`<rect class="tl-bar" x="${x+1}" y="${H-pad-h}" width="${Math.max(bw-2,1)}" height="${h}">
        <title>${y}: ${n} recordings</title></rect>`;
    if((y-y0)%5===0||y===y1)
      s+=`<text class="axislab" x="${x+bw/2}" y="${H-pad+14}" text-anchor="middle">${y}</text>`;
  }
  s+=`</svg>`;
  $('#timeline').innerHTML=s;
  $('#timeline').querySelectorAll('rect').forEach((r,i)=>{
    r.onclick=()=>{ const y=r.querySelector('title').textContent.split(':')[0];
      update({year:y}); scrollToTable(); };
  });
})();

// ---------- bar charts ----------
CHARTS={
  performers:{data:tally('performer'),               def:15, kind:'q'},
  genres:    {data:tally('genre'),                   def:15, kind:'genre'},
  locations: {data:tally('location'),                def:50, kind:'loc'},  // only ~16 exist: show all, no expand
  tapes:     {data:tally('tape_group'),              def:15, kind:'tape'},
  gender:    {data:tally('gender',{includeBlank:true}),def:8, kind:'gender'},
};
['performers','genres','locations','tapes','gender'].forEach(drawChart);

// ---------- table + filters (URL-driven, shareable permalinks) ----------
const COLS=[['',''],['title','Title'],['performer','Performer'],['genre','Genre'],
            ['location','Location'],['year','Year'],['tape_name','Tape']];
$('#head').innerHTML=COLS.map(([k,l])=>`<th data-k="${k}">${l}</th>`).join('');
function fillSel(id,field,label,includeBlank){
  const sel=$('#'+id); const opts=tally(field,{includeBlank}).map(d=>d[0]);
  sel.innerHTML=`<option value="">All ${label}</option>`+opts.map(o=>`<option>${esc(o)}</option>`).join('');
}
fillSel('fGenre','genre','genres');
fillSel('fLoc','location','locations');
fillSel('fTape','tape_group','tapes');
fillSel('fGender','gender','genders',true);
(function(){const sel=$('#fYear');const ys=[...new Set(years)].sort((a,b)=>a-b);
  sel.innerHTML='<option value="">All years</option>'+ys.map(y=>`<option>${y}</option>`).join('');})();

function scrollToTable(){$('#q').scrollIntoView({behavior:'smooth',block:'start'});}

// ---- URL hash is the single source of truth for filter/sort state ----
const FIELDS=['q','genre','loc','tape','year','gender','sort','dir'];
function getState(){
  const p=new URLSearchParams(location.hash.slice(1)); const s={};
  for(const k of FIELDS) s[k]=p.get(k)||'';
  s.audio=p.get('audio')==='1';
  return s;
}
function buildHash(s){
  const p=new URLSearchParams();
  for(const k of FIELDS) if(s[k]) p.set(k,s[k]);
  if(s.audio) p.set('audio','1');
  return p.toString();
}
function update(patch,push){
  const s={...getState(),...patch};
  const url=location.pathname+location.search+'#'+buildHash(s);
  if(push===false) history.replaceState(null,'',url); else history.pushState(null,'',url);
  render(s);
}
// back/forward and manual edits to the URL both re-render
window.addEventListener('popstate',()=>render(getState()));
window.addEventListener('hashchange',()=>render(getState()));

// control -> state wiring
const CTRL={fGenre:'genre',fLoc:'loc',fTape:'tape',fGender:'gender',fYear:'year'};
Object.entries(CTRL).forEach(([id,key])=>
  $('#'+id).addEventListener('change',()=>update({[key]:$('#'+id).value})));
$('#q').addEventListener('input',()=>update({q:$('#q').value},false)); // replace, not push
$('#fAudio').onclick=()=>update({audio:!getState().audio});
$('#fClear').onclick=()=>update({q:'',genre:'',loc:'',tape:'',gender:'',year:'',audio:false,sort:'',dir:''});
$('#head').addEventListener('click',e=>{const k=e.target.dataset.k;if(!k)return;
  const s=getState(); const dir=(s.sort===k && s.dir!=='-1')?'-1':'';
  update({sort:k,dir});});

let cur=null;
function render(s){
  s=s||getState();
  // reflect state into the controls
  $('#q').value=s.q; $('#fGenre').value=s.genre; $('#fLoc').value=s.loc;
  $('#fTape').value=s.tape; $('#fGender').value=s.gender; $('#fYear').value=s.year;
  $('#fAudio').classList.toggle('on',!!s.audio);
  syncAlbum(s);  // keep the album/track dropdowns reflecting the actual filter state
  const q=norm(s.q).toLowerCase();
  let rows=SONGS.filter(r=>{
    if(s.genre && norm(r.genre)!==s.genre) return false;
    if(s.loc && norm(r.location)!==s.loc) return false;
    if(s.tape && norm(r.tape_group)!==s.tape) return false;
    if(s.year && String(r.year)!==s.year) return false;
    if(s.gender){ if(s.gender==='(unknown)'){ if(norm(r.gender)) return false; }
                  else if(norm(r.gender)!==s.gender) return false; }
    if(s.audio && !r.has_audio) return false;
    if(q){
      const blob=[r.title,r.performer,r.genre,r.location,r.lyricist,r.composer,r.tape_name]
        .map(norm).join(' ').toLowerCase();
      const terms=q.split('|').map(t=>t.trim()).filter(Boolean);   // "|" = OR
      if(terms.length && !terms.some(t=>blob.includes(t))) return false;
    }
    return true;
  });
  const sortK=s.sort||'title', dir=(s.dir==='-1')?-1:1;
  rows.sort((a,b)=>{
    let av=a[sortK],bv=b[sortK];
    if(sortK==='year'){av=av||0;bv=bv||0;return (av-bv)*dir;}
    return norm(av).localeCompare(norm(bv))*dir;
  });
  // sort arrows in header
  document.querySelectorAll('#head th').forEach(th=>{
    const c=COLS.find(c=>c[0]===th.dataset.k); if(!c)return;
    th.textContent=c[1]+((th.dataset.k===sortK&&c[1])?(dir<0?' ▼':' ▲'):'');
  });
  $('#count').textContent=rows.length.toLocaleString()+' of '+SONGS.length.toLocaleString();
  const tb=$('#rows'); tb.innerHTML='';
  const frag=document.createDocumentFragment();
  for(const r of rows.slice(0,1200)){
    const tr=document.createElement('tr');
    const ptitle=esc((r.title||'')+(r.performer?' — '+r.performer:''));
    const play=r.has_audio?`<button class="play" data-a="${esc(r.audio)}" data-id="${r.id}" data-title="${ptitle}">▶</button>`:'';
    tr.innerHTML=`<td>${play}</td>
      <td><a href="${r.url}" target="_blank">${esc(r.title)||'—'}</a></td>
      <td>${esc(r.performer)||'<span class=muted>—</span>'}</td>
      <td>${esc(r.genre)||'<span class=muted>—</span>'}</td>
      <td>${esc(r.location)||'<span class=muted>—</span>'}</td>
      <td>${r.year||'<span class=muted>—</span>'}</td>
      <td class="muted">${esc(r.tape_name)||'—'}</td>`;
    frag.appendChild(tr);
  }
  tb.appendChild(frag);
  if(rows.length>1200){const tr=document.createElement('tr');
    tr.innerHTML=`<td colspan="7" class="muted">Showing first 1,200 — narrow your search to see more.</td>`;
    tb.appendChild(tr);}
}
const player=$('#player');
let rate=1;
function clearPlayIcons(){document.querySelectorAll('.play.playing').forEach(x=>{x.classList.remove('playing');x.textContent='▶';});}
$('#rows').addEventListener('click',e=>{
  const b=e.target.closest('.play'); if(!b)return;
  clearPlayIcons();
  if(cur===b.dataset.id && !player.paused){player.pause();cur=null;return;}
  player.src=b.dataset.a; player.playbackRate=rate; player.play(); cur=b.dataset.id;
  b.classList.add('playing'); b.textContent='⏸';
  $('#nowbar').classList.add('show');
  $('#npTitle').innerHTML='<b>♪</b> '+(b.dataset.title||'');
});
// keep speed applied after a new source loads (some browsers reset it)
player.addEventListener('loadeddata',()=>{player.playbackRate=rate;});
player.onended=clearPlayIcons;
// native pause/play sync with the row ▶/⏸ icon
player.onpause=()=>{const a=document.querySelector('.play.playing');if(a){a.textContent='▶';}};
player.onplay=()=>{const a=document.querySelector(`.play[data-id="${cur}"]`);if(a){a.classList.add('playing');a.textContent='⏸';}};
// speed control
document.querySelector('.spd').addEventListener('click',e=>{
  const btn=e.target.closest('.sbtn'); if(!btn)return;
  rate=parseFloat(btn.dataset.r); player.playbackRate=rate;
  document.querySelectorAll('.sbtn').forEach(x=>x.classList.toggle('on',x===btn));
});

// ---------- album -> field-recording browser ----------
// The dropdowns are a launcher AND a mirror of state: picking a track sets the
// query; conversely render() re-selects the matching track (or clears it) so the
// dropdowns never disagree with what the table is actually showing.
const albumSel=$('#albumSel'), songSel=$('#songSel'), albumInfo=$('#albumInfo');
albumSel.innerHTML=ALBUMS.map((a,i)=>`<option value="${i}">${esc(a.name)}</option>`).join('');
function loadSongs(){
  const a=ALBUMS[albumSel.value]||ALBUMS[0];
  songSel.innerHTML=['<option value="">— choose a track —</option>']
    .concat(a.songs.map((s,i)=>`<option value="${i}">${esc(s.n+' · '+s.title)}</option>`)).join('');
}
function albumLinks(a){
  if(!a||!a.links) return '';
  return a.links.map(([lab,url])=>`<a href="${url}" target="_blank">${esc(lab)} ↗</a>`).join(' · ');
}
function setAlbumInfo(s,a){
  const links=albumLinks(a);
  albumInfo.innerHTML = s
    ? `<b>${esc(s.title)}</b> · ${esc(s.by)}`+(links?` · ${links}`:'')
    : links;
}
albumSel.addEventListener('change',()=>{loadSongs();setAlbumInfo(null,ALBUMS[albumSel.value]);});
songSel.addEventListener('change',()=>{
  const a=ALBUMS[albumSel.value]; const s=a&&a.songs[songSel.value];
  if(!s) return;  // "— choose a track —" picked: leave current state as-is
  update({q:s.q,genre:'',loc:'',gender:'',year:'',audio:false});
  scrollToTable();
});
// reflect current filter state back into the dropdowns
function syncAlbum(s){
  const onlyQ = s.q && !s.genre && !s.loc && !s.tape && !s.gender && !s.year && !s.audio;
  let ai=-1, si=-1;
  if(onlyQ){
    for(let i=0;i<ALBUMS.length && si<0;i++){
      const j=ALBUMS[i].songs.findIndex(x=>x.q===s.q);
      if(j>=0){ai=i;si=j;}
    }
  }
  if(si>=0){
    if(albumSel.value!==String(ai)){albumSel.value=String(ai);loadSongs();}
    songSel.value=String(si);
    setAlbumInfo(ALBUMS[ai].songs[si],ALBUMS[ai]);
  } else {
    songSel.value='';                       // any other state -> no track selected
    setAlbumInfo(null,ALBUMS[albumSel.value]);
  }
}
loadSongs();
render(getState());  // initial render reflects the URL and syncs the dropdowns
</script>
</body>
</html>"""

out = (HTML.replace("__SONGS__", payload)
           .replace("__NITEMS__", str(len(items)))
           .replace("__ALBUMS__", albumpayload))
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)
print(f"wrote index.html  songs={len(songs)}  total_items={len(items)}")
