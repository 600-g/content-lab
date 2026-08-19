"""카탈로그 HTML 의 정적 부분 — CSS / JS 엔진 / 페이지 골격.

바탕화면 `스킬박스고도화.zip` (두근 스킬카탈로그 킷, 2026-08-13) 의 catalog_template.html 을 이식.
킷 원칙: 서버·DB·라이브러리·외부 요청 0, 단일 HTML 자체완결, data-text 소문자 검색 인덱스.
확장: 등급칩(data-grade) · AI도구칩(data-tools) · 딥링크(#slug) · CSP nonce.
"""
from __future__ import annotations

CSS = r"""
:root{
  --ink:#07080a; --ink2:#0d1014; --panel:#111419; --panel2:#161a21; --line:#232833;
  --fg:#e8ecf2; --dim:#8b95a6; --faint:#5b6474;
  --lime:#c8f751; --violet:#b28cff; --amber:#ffb95c; --cyan:#6fe3ff; --rose:#ff7aa2; --accent:var(--lime);
  --r:14px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--ink); color:var(--fg);
  font:15px/1.65 "Apple SD Gothic Neo","Pretendard","Helvetica Neue",Helvetica,"Malgun Gothic",sans-serif;
  -webkit-font-smoothing:antialiased;
  background-image:
    radial-gradient(900px 500px at 12% -8%, rgba(200,247,81,.10), transparent 60%),
    radial-gradient(700px 460px at 92% 4%, rgba(178,140,255,.10), transparent 60%);
  background-attachment:fixed;
}
a{color:inherit}
.wrap{padding:0 16px 70px}
.hero{padding:40px 0 22px; border-bottom:1px solid var(--line); max-width:1180px; margin:0 auto}
.kicker{font:600 11px/1 ui-monospace,SFMono-Regular,Menlo,monospace; letter-spacing:.24em;
  color:var(--faint); text-transform:uppercase; display:flex; gap:10px; align-items:center}
.kicker::after{content:""; flex:1; height:1px; background:var(--line)}
h1{font-size:clamp(34px,5.4vw,62px); line-height:.94; margin:14px 0 0; font-weight:800;
  letter-spacing:-.05em; display:flex; align-items:center; flex-wrap:wrap}
h1 .a{color:var(--fg)}
h1 .b{color:var(--lime); text-shadow:0 0 42px rgba(200,247,81,.35)}
h1 .dot{width:10px; height:10px; border-radius:50%; background:var(--violet); margin-left:14px;
  box-shadow:0 0 20px var(--violet)}
.tagline{color:var(--dim); max-width:760px; margin:16px 0 0; font-size:15px}
.tagline b{color:var(--fg); font-weight:600}
.metrics{display:flex; gap:22px; flex-wrap:wrap; margin-top:22px}
.metric{background:var(--panel); border:1px solid var(--line); border-radius:var(--r);
  padding:12px 16px; min-width:150px}
.metric .v{font-size:22px; font-weight:800; color:var(--lime)}
.metric.m2 .v{color:var(--violet)}
.metric.m3 .v{color:var(--amber)}
.metric .l{font-size:12px; color:var(--dim); margin-top:2px}
.bar{position:sticky; top:0; z-index:40; background:rgba(7,8,10,.86);
  backdrop-filter:blur(8px); margin:0 -16px 26px; padding:12px 16px;
  border-bottom:1px solid var(--line)}
.barin{max-width:1180px; margin:0 auto; display:flex; flex-direction:column; gap:10px}
.search{display:flex; align-items:center; gap:10px}
#q{flex:1; background:var(--panel2); border:1px solid var(--line); color:var(--fg);
  border-radius:10px; padding:11px 14px; font-size:16px; outline:none}
#q:focus{border-color:var(--lime)}
.count{font:600 12px ui-monospace,monospace; color:var(--dim); white-space:nowrap}
.count b{color:var(--lime)}
.chips{display:flex; gap:7px; flex-wrap:wrap; align-items:center}
.chips .lbl{font-size:11px; color:var(--faint); margin-right:2px; text-transform:uppercase; letter-spacing:.1em}
.schip,.chip,.gchip,.tchip{border:1px solid var(--line); background:var(--panel); color:var(--dim);
  border-radius:999px; padding:5px 12px; font-size:12.5px; font-weight:600; cursor:pointer;
  transition:.14s; user-select:none}
.schip:hover,.chip:hover,.gchip:hover,.tchip:hover{color:var(--fg); border-color:var(--dim)}
.schip.on{background:var(--fg); color:var(--ink); border-color:var(--fg)}
.chip.on{background:var(--lime); color:var(--ink); border-color:var(--lime)}
.gchip.on{background:var(--amber); color:var(--ink); border-color:var(--amber)}
.tchip.on{background:var(--violet); color:#fff; border-color:var(--violet)}
.domain{max-width:1180px; margin:0 auto 40px}
.dhead{display:flex; align-items:baseline; gap:12px; padding-bottom:6px; border-bottom:1px solid var(--line)}
.dhead .num{font:800 13px ui-monospace,monospace; color:var(--faint)}
.dhead h2{font-size:21px; font-weight:800; margin:0}
.dhead .cnt{font:600 13px ui-monospace,monospace; color:var(--lime); margin-left:auto}
.dblurb{color:var(--dim); font-size:13.5px; margin:10px 0 18px}
.sub{margin:0 0 22px}
.sub .shead{font-size:13px; font-weight:700; color:var(--dim); text-transform:uppercase;
  letter-spacing:.08em; margin:0 0 12px}
.grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px}
.card{background:var(--panel); border:1px solid var(--line); border-radius:var(--r);
  padding:16px; display:flex; flex-direction:column; gap:8px; position:relative;
  animation:rise .4s both; animation-delay:calc(var(--i,0)*18ms); scroll-margin-top:180px}
@keyframes rise{from{opacity:0; transform:translateY(8px)} to{opacity:1; transform:none}}
.card:hover{border-color:var(--dim)}
.card.flash{border-color:var(--lime); box-shadow:0 0 0 2px rgba(200,247,81,.35)}
.chead{display:flex; align-items:center; justify-content:space-between; gap:8px}
.src{font:700 9.5px ui-monospace,monospace; letter-spacing:.12em; padding:3px 7px; border-radius:6px;
  background:rgba(139,149,166,.16); color:var(--dim); text-transform:uppercase}
.s-youtube{background:rgba(255,122,162,.16); color:var(--rose)}
.s-notion{background:rgba(232,236,242,.14); color:var(--fg)}
.s-github{background:rgba(178,140,255,.16); color:var(--violet)}
.s-instagram{background:rgba(255,185,92,.14); color:var(--amber)}
.s-web{background:rgba(200,247,81,.14); color:var(--lime)}
.s-tiktok,.s-twitter{background:rgba(111,227,255,.14); color:var(--cyan)}
.date{font:500 11px ui-monospace,monospace; color:var(--faint)}
.card h3{font-size:15.5px; font-weight:700; margin:2px 0 0; line-height:1.35}
.card h3 a{text-decoration:none}
.card h3 a:hover{color:var(--lime)}
.cmd{font:600 12px ui-monospace,monospace; color:var(--lime); background:var(--ink2);
  border:1px solid var(--line); border-radius:7px; padding:5px 9px; align-self:flex-start; word-break:break-all}
.desc{font-size:13px; color:var(--dim); margin:2px 0 0}
.orig{font:500 11.5px ui-monospace,monospace; color:var(--faint); margin:0}
.who{display:flex; gap:8px; margin-top:2px; flex-wrap:wrap}
.who span{font-size:11px; color:var(--faint)}
.who .au{color:var(--amber); font-weight:700}
.who .tm{color:var(--dim)}
.acts{display:flex; gap:8px; margin-top:10px}
.btn{border:1px solid var(--line); background:var(--panel2); color:var(--fg);
  border-radius:9px; padding:8px 12px; font-size:12.5px; font-weight:600; cursor:pointer;
  transition:.14s; text-decoration:none; display:inline-flex; align-items:center; gap:6px}
.btn:hover{border-color:var(--dim)}
.btn.primary{background:var(--lime); color:var(--ink); border-color:var(--lime)}
.btn.primary:hover{filter:brightness(1.05)}
.btn.copy.done{background:var(--violet); color:#fff; border-color:var(--violet)}
.empty{max-width:1180px; margin:60px auto; text-align:center; color:var(--dim)}
.empty h3{color:var(--fg); font-size:18px}
.hidden{display:none !important}
#toast{position:fixed; left:50%; bottom:28px; transform:translate(-50%,20px); z-index:60;
  background:var(--lime); color:var(--ink); font-weight:600; font-size:13px;
  padding:11px 20px; border-radius:11px; opacity:0; pointer-events:none; transition:.22s;
  box-shadow:0 12px 32px -12px rgba(0,0,0,.8); max-width:90vw; text-align:center}
#toast.on{opacity:1; transform:translate(-50%,0)}
#backdrop{position:fixed; inset:0; z-index:80; background:rgba(0,0,0,.66);
  backdrop-filter:blur(4px); display:none; align-items:flex-start; justify-content:center;
  padding:60px 16px; overflow:auto}
#backdrop.on{display:flex}
.modal{background:var(--panel); border:1px solid var(--line); border-radius:16px;
  max-width:760px; width:100%; padding:26px; position:relative}
.mclose{position:absolute; top:14px; right:14px; background:var(--panel2); border:1px solid var(--line);
  color:var(--fg); width:32px; height:32px; border-radius:8px; cursor:pointer; font-size:16px}
.mbody h3{margin:0 40px 6px 0; font-size:20px}
.mbody .mcmd{font:600 13px ui-monospace,monospace; color:var(--lime); background:var(--ink2);
  border:1px solid var(--line); border-radius:8px; padding:8px 12px; display:block; margin:10px 0; word-break:break-all}
.mbody p,.mbody li{color:var(--dim); font-size:14px}
.mbody h4{color:var(--fg); font-size:13px; margin:16px 0 6px; text-transform:uppercase; letter-spacing:.08em}
.mbody .md h2{font-size:17px; margin:22px 0 8px; color:var(--fg)}
.mbody .md h3{font-size:15px; margin:16px 0 6px; color:var(--fg)}
.mbody .md strong{color:var(--fg)}
.mbody .md code{font:500 12.5px ui-monospace,monospace; background:var(--ink2); border:1px solid var(--line);
  border-radius:5px; padding:1px 5px; color:var(--lime)}
.mbody .md pre{background:var(--ink2); border:1px solid var(--line); border-radius:9px; padding:12px 14px;
  overflow:auto; font-size:12.5px; line-height:1.5}
.mbody .md pre code{border:0; background:transparent; padding:0; color:var(--fg)}
.mbody .md table{border-collapse:collapse; width:100%; font-size:13px; display:block; overflow-x:auto}
.mbody .md th,.mbody .md td{border:1px solid var(--line); padding:6px 9px; text-align:left; color:var(--dim)}
.mbody .md th{color:var(--fg); background:var(--panel2)}
.mbody .md blockquote{border-left:3px solid var(--violet); margin:10px 0; padding:4px 12px; color:var(--dim)}
.mbody .md a{color:var(--cyan)}
.mbody .macts{display:flex; gap:8px; margin:14px 0 6px; flex-wrap:wrap}
.mbody .srcs a{color:var(--cyan); font-size:13px; word-break:break-all}
@media(max-width:640px){
  .wrap{padding:0 12px 70px}
  .grid{grid-template-columns:1fr}
  .metrics{gap:12px}
  #backdrop{padding:24px 10px}
  .modal{padding:18px}
}
"""

JS = r"""
const cards = [...document.querySelectorAll('.card')];
const cnt = document.getElementById('cnt');
const empty = document.querySelector('.empty');
let src = 'all', dom = null, grade = null, tool = null, q = '';

function apply() {
  let n = 0;
  for (const c of cards) {
    const ok = (src === 'all' || c.dataset.source === src)
      && (!dom || c.dataset.group === dom)
      && (!grade || c.dataset.grade === grade)
      && (!tool || (' ' + c.dataset.tools + ' ').includes(' ' + tool + ' '))
      && (!q || c.dataset.text.includes(q));
    c.classList.toggle('hidden', !ok);
    if (ok) n++;
  }
  const shown = s => [...s.querySelectorAll('.card')].some(c => !c.classList.contains('hidden'));
  for (const s of document.querySelectorAll('.sub')) s.classList.toggle('hidden', !shown(s));
  for (const s of document.querySelectorAll('.domain')) {
    const vis = shown(s);
    s.classList.toggle('hidden', !vis);
    const k = [...s.querySelectorAll('.card')].filter(c => !c.classList.contains('hidden')).length;
    const el = s.querySelector('.dhead .cnt'); if (el) el.textContent = k;
  }
  cnt.textContent = n + '개';
  empty.classList.toggle('hidden', n > 0);
}

const qi = document.getElementById('q');
qi.addEventListener('input', e => { q = e.target.value.trim().toLowerCase(); apply(); });
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== qi) { e.preventDefault(); qi.focus(); }
  if (e.key === 'Escape' && document.activeElement === qi) { qi.value = ''; q = ''; apply(); qi.blur(); }
});
function toggleGroup(sel, prop, attr) {
  for (const b of document.querySelectorAll(sel)) b.addEventListener('click', () => {
    const was = b.classList.contains('on');
    document.querySelectorAll(sel).forEach(x => x.classList.remove('on'));
    const v = was ? null : (b.classList.add('on'), b.dataset[attr]);
    if (prop === 'dom') dom = v; else if (prop === 'grade') grade = v; else tool = v;
    apply();
  });
}
for (const b of document.querySelectorAll('.schip')) b.addEventListener('click', () => {
  document.querySelectorAll('.schip').forEach(x => x.classList.remove('on'));
  b.classList.add('on'); src = b.dataset.src; apply();
});
toggleGroup('.chip', 'dom', 'dom');
toggleGroup('.gchip', 'grade', 'grade');
toggleGroup('.tchip', 'tool', 'tool');

const toast = document.getElementById('toast');
const backdrop = document.getElementById('backdrop');
const mbody = backdrop.querySelector('.mbody');
let tt;

async function copyText(cmd) {
  try { await navigator.clipboard.writeText(cmd); }
  catch (_) {
    const ta = document.createElement('textarea');
    ta.value = cmd; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
  }
}
function showToast(msg) {
  toast.textContent = msg; toast.classList.add('on');
  clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('on'), 2200);
}
function openCard(card) {
  mbody.innerHTML = '';
  mbody.appendChild(card.querySelector('template').content.cloneNode(true));
  backdrop.classList.add('on');
  document.body.style.overflow = 'hidden';
}
function closeModal() { backdrop.classList.remove('on'); document.body.style.overflow = ''; }

document.addEventListener('click', async e => {
  const cp = e.target.closest('.copy');
  if (cp) {
    e.preventDefault();
    let cmd = cp.dataset.cmd;
    if (!cmd && cp.dataset.copyOf) {
      const owner = document.getElementById(cp.dataset.copyOf);
      const ob = owner && owner.querySelector('.copy[data-cmd]');
      cmd = ob ? ob.dataset.cmd : '';
    }
    if (!cmd) return;
    await copyText(cmd);
    cp.classList.add('done');
    showToast('SKILL.md 전문을 복사했습니다 — 다른 기기면 ~/.claude/skills/<슬러그>/SKILL.md 로 저장하세요');
    setTimeout(() => cp.classList.remove('done'), 2000);
    return;
  }
  const lk = e.target.closest('.linkcopy');
  if (lk) {
    e.preventDefault();
    await copyText(location.origin + location.pathname + '#' + lk.dataset.slug);
    showToast('카탈로그 링크를 복사했습니다');
    return;
  }
  const dt = e.target.closest('.detail');
  if (dt) { openCard(dt.closest('.card')); history.replaceState(null, '', '#' + dt.closest('.card').id); return; }
  if (e.target.closest('.mclose') || e.target === backdrop) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && backdrop.classList.contains('on')) closeModal();
});
function openFromHash() {
  const slug = decodeURIComponent((location.hash || '').slice(1));
  if (!slug) return;
  const card = document.getElementById(slug);
  if (!card || !card.classList.contains('card')) return;
  card.scrollIntoView({block: 'center'});
  card.classList.add('flash');
  setTimeout(() => card.classList.remove('flash'), 2400);
  openCard(card);
}
window.addEventListener('hashchange', openFromHash);
openFromHash();
apply();
"""

PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; script-src 'nonce-{nonce}'; img-src data:; base-uri 'none'; form-action 'none'">
<meta name="robots" content="noindex">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">

<header class="hero">
  <div class="kicker">두근컴퍼니 · SKILL LIBRARY · {generated_kst} KST</div>
  <h1><span class="a">두근</span><span class="b">SKILLS</span><i class="dot"></i></h1>
  <p class="tagline">수집한 콘텐츠를 <b>SKILL.md</b> 로 자산화한 도서관입니다. 검색하거나 <b>칩</b>으로 걸러 보고,
  <b>SKILL.md 복사</b>를 누르면 전문이 복사됩니다 (다른 기기의 <code>~/.claude/skills/</code> 에 그대로 저장).
  에이전트는 <code>/api/library/search</code> · MCP <code>search_skills</code> 로 같은 자료를 씁니다.</p>
  <div class="metrics">
    <div class="metric m1"><div class="v">{total}</div><div class="l">등록 스킬</div></div>
    <div class="metric m2"><div class="v">{n_categories}</div><div class="l">카테고리</div></div>
    <div class="metric m3"><div class="v">{last_updated_short}</div><div class="l">마지막 갱신 KST</div></div>
  </div>
</header>

<div class="bar"><div class="barin">
  <div class="search">
    <input id="q" placeholder="스킬 검색  ( / 키로 포커스 · Esc 초기화 )" autocomplete="off">
    <span class="count"><b id="cnt">{total}개</b></span>
  </div>
  <div class="chips"><span class="lbl">출처</span><button class="schip on" data-src="all">전체</button>{source_chips}</div>
  <div class="chips"><span class="lbl">카테고리</span>{category_chips}</div>
  <div class="chips"><span class="lbl">등급</span>{grade_chips}</div>
  <div class="chips"><span class="lbl">AI 도구</span>{tool_chips}</div>
</div></div>

{sections}

<div class="empty hidden">
  <h3>조건에 맞는 스킬이 없어요</h3>
  <p>검색어나 필터를 바꿔보세요. (Esc 로 검색 초기화)</p>
</div>

</div><!-- /wrap -->

<div id="toast"></div>
<div id="backdrop"><div class="modal"><div class="mbody"></div></div></div>

<script nonce="{nonce}">{js}</script>
</body>
</html>
"""
