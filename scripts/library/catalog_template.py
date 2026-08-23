"""카탈로그(게시판) / 게시글 상세 페이지의 정적 부분 — CSS · JS 엔진 · 페이지 골격.

디자인: aiskillbox 메인 사이트의 **픽셀+디지털 레트로** 테마와 통일 (static/style.css 토큰 이식).
본문은 Pretendard (가독성 우선), 픽셀 폰트(Galmuri11)는 라벨·뱃지·숫자에만.
구조/필터 엔진은 바탕화면 킷(두근 스킬카탈로그 킷)에서 이식하되, 상세는 모달 대신 전용 페이지.
"""
from __future__ import annotations

FONT_LINKS = (
    '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/'
    'dist/web/variable/pretendardvariable-dynamic-subset.min.css">'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/galmuri@latest/dist/galmuri.css">'
)

CSP = (
    "default-src 'none'; "
    "style-src 'unsafe-inline' https://cdn.jsdelivr.net; "
    "font-src https://cdn.jsdelivr.net; "
    "img-src 'self' data:; "
    "manifest-src 'self'; "
    "script-src 'nonce-{nonce}'; "
    "base-uri 'none'; form-action 'none'"
)

# ── 공통 (토큰 · 배경 · 톱바 · 버튼 · 뱃지) ────────────────────────
BASE_CSS = r"""
:root{
  --bg:#05070d; --bg-2:#0a0e1a; --surface:#0d1424; --surface-2:#131b30; --surface-3:#1a2440;
  --line:#1e2a45; --line-strong:#2c3d63;
  --text:#e9eef9; --text-soft:#c3cde2; --muted:#7f8aa8;
  --cyan:#3ee6ff; --cyan-deep:#0e7490; --magenta:#ff6bf0; --lime:#b6f04d; --amber:#ffc233;
  --red:#ff5470; --green:#3ddc85;
  --grade-s:#ff5470; --grade-a:#ff9640; --grade-b:#ffd23e; --grade-c:#64748b;
  --r-sm:4px; --r-md:6px; --r-lg:8px;
  --font-body:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
  --font-pixel:"Galmuri11","Pretendard Variable",Pretendard,sans-serif;
  --font-mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  --shadow-hard:4px 4px 0 rgba(0,0,0,.45); --shadow-hard-sm:3px 3px 0 rgba(0,0,0,.4);
  --glow-cyan:0 0 18px rgba(62,230,255,.22);
  /* 노치/홈인디케이터 — viewport-fit=cover 를 쓰므로 필수 (메인 style.css 와 동일 규약) */
  --safe-top:env(safe-area-inset-top,0px); --safe-bottom:env(safe-area-inset-bottom,0px);
  --safe-left:env(safe-area-inset-left,0px); --safe-right:env(safe-area-inset-right,0px);
  /* 스티키 스택 높이 — JS 가 실측해서 덮어쓴다 (필터바 top / 카드 scroll-margin) */
  --topbar-h:52px; --bar-h:0px;
}
*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
html{-webkit-text-size-adjust:100%; scroll-behavior:smooth}
body{
  margin:0; font-family:var(--font-body); background:var(--bg); color:var(--text);
  min-height:100dvh; -webkit-font-smoothing:antialiased; letter-spacing:-.01em;
  font-size:15px; line-height:1.65; position:relative;
  padding-bottom:calc(60px + var(--safe-bottom));
}
a{color:inherit}
.bg-fx{
  position:fixed; inset:0; z-index:-1; pointer-events:none;
  background:
    repeating-linear-gradient(0deg, rgba(255,255,255,.016) 0 1px, transparent 1px 4px),
    radial-gradient(rgba(62,230,255,.05) 1px, transparent 1.6px),
    radial-gradient(900px 520px at 85% -10%, rgba(62,230,255,.09), transparent 60%),
    radial-gradient(720px 440px at 0% 112%, rgba(255,107,240,.07), transparent 60%),
    linear-gradient(180deg, var(--bg) 0%, var(--bg-2) 65%, var(--bg) 100%);
  background-size:auto, 24px 24px, auto, auto, auto;
}
.wrap{max-width:1180px; margin:0 auto; padding:0 16px}

/* 톱바 */
.topbar{
  position:sticky; top:0; z-index:50; display:flex; align-items:center; justify-content:space-between;
  gap:10px; min-height:52px; background:rgba(5,7,13,.9);
  /* 노치/상태바 아래로 — standalone PWA 에서 톱바(= 유일한 뒤로가기)가 잘리던 문제 */
  padding:calc(10px + var(--safe-top)) calc(16px + var(--safe-right)) 10px calc(16px + var(--safe-left));
  backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px); border-bottom:1px solid var(--line);
}
.topbar::after{
  content:""; position:absolute; left:0; right:0; bottom:-2px; height:2px;
  background:linear-gradient(90deg, var(--cyan), var(--magenta) 55%, transparent 90%); opacity:.65;
}
.brand{display:flex; align-items:center; gap:9px; text-decoration:none}
.brand-logo{font-size:20px; filter:drop-shadow(0 0 8px rgba(62,230,255,.55))}
.brand-name{
  font-family:var(--font-pixel); font-size:14px; letter-spacing:.06em;
  background:linear-gradient(90deg,var(--cyan) 0%,var(--magenta) 100%);
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
.topbar-actions{display:flex; align-items:center; gap:8px}
.chip-link{
  display:inline-flex; align-items:center; justify-content:center; gap:6px; padding:9px 13px;
  min-height:40px; background:rgba(62,230,255,.08); border:1px solid rgba(62,230,255,.45);
  border-radius:var(--r-sm); color:var(--cyan); text-decoration:none; font-size:12px;
  font-family:var(--font-pixel); letter-spacing:.06em; touch-action:manipulation;
}
.chip-link:hover{background:rgba(62,230,255,.16); box-shadow:var(--glow-cyan)}
.chip-link:active{transform:translate(1px,1px)}

/* 버튼 */
.btn{
  display:inline-flex; align-items:center; gap:6px; padding:8px 13px;
  background:var(--surface-2); border:1px solid var(--line-strong); border-radius:var(--r-sm);
  color:var(--text); font-size:12.5px; font-weight:600; cursor:pointer; text-decoration:none;
  box-shadow:var(--shadow-hard-sm); transition:transform .08s, box-shadow .08s, background .15s;
}
.btn:hover{background:var(--surface-3)}
.btn:active{transform:translate(2px,2px); box-shadow:1px 1px 0 rgba(0,0,0,.4)}
.btn.primary{background:var(--cyan); color:#04202b; border-color:var(--cyan); box-shadow:3px 3px 0 var(--cyan-deep)}
.btn.primary:hover{filter:brightness(1.06)}
.btn.primary:active{box-shadow:1px 1px 0 var(--cyan-deep)}
.btn.done{background:var(--magenta); color:#2a0723; border-color:var(--magenta); box-shadow:3px 3px 0 #7a1668}
.btn{touch-action:manipulation}
@media(max-width:720px){
  /* 손가락 탭 타겟 — 최소 40px (Apple HIG 44 에 근접) */
  .btn{padding:10px 14px; font-size:13px; min-height:40px}
}

/* 등급/출처 뱃지 */
.grade{
  font-family:var(--font-pixel); font-size:10.5px; letter-spacing:.06em; padding:3px 7px;
  border-radius:var(--r-sm); color:#fff; line-height:1.2;
}
.g-S{background:var(--grade-s)} .g-A{background:var(--grade-a); color:#1c1206}
.g-B{background:var(--grade-b); color:#1e293b} .g-C{background:var(--grade-c)}
.g-{background:var(--surface-3); color:var(--muted)}
.src{
  font-family:var(--font-pixel); font-size:10px; letter-spacing:.06em; padding:3px 7px;
  border-radius:var(--r-sm); background:rgba(127,138,168,.16); color:var(--muted);
}
.s-youtube{background:rgba(255,84,112,.16); color:var(--red)}
.s-notion{background:rgba(233,238,249,.12); color:var(--text-soft)}
.s-github{background:rgba(255,107,240,.16); color:var(--magenta)}
.s-instagram{background:rgba(255,194,51,.16); color:var(--amber)}
.s-web{background:rgba(182,240,77,.14); color:var(--lime)}
.s-tiktok,.s-twitter{background:rgba(62,230,255,.14); color:var(--cyan)}
.date{font-family:var(--font-mono); font-size:11px; color:var(--muted)}

/* 토스트 */
#toast{
  position:fixed; left:50%; bottom:24px; transform:translate(-50%,20px); z-index:80;
  background:var(--cyan); color:#04202b; font-weight:700; font-size:13px; padding:11px 18px;
  border-radius:var(--r-sm); opacity:0; pointer-events:none; transition:.22s;
  box-shadow:var(--shadow-hard); max-width:92vw; text-align:center;
}
#toast.on{opacity:1; transform:translate(-50%,0)}
.hidden{display:none !important}
"""

# ── 카탈로그(게시판 목록) ────────────────────────────────────────
CATALOG_CSS = r"""
.hero{padding:28px 0 18px; border-bottom:1px solid var(--line)}
.kicker{
  font-family:var(--font-pixel); font-size:10.5px; letter-spacing:.18em; color:var(--muted);
  text-transform:uppercase; display:flex; gap:10px; align-items:center;
}
.kicker::after{content:""; flex:1; height:1px; background:var(--line)}
h1{
  font-size:clamp(26px,4.6vw,44px); line-height:1.05; margin:12px 0 0; font-weight:800; letter-spacing:-.04em;
  display:flex; align-items:center; flex-wrap:wrap; gap:2px;
}
h1 .a{color:var(--text)}
h1 .b{
  background:linear-gradient(90deg,var(--cyan),var(--magenta));
  -webkit-background-clip:text; background-clip:text; color:transparent;
}
h1 .cursor{
  display:inline-block; width:11px; height:.82em; background:var(--cyan); margin-left:8px;
  box-shadow:0 0 14px var(--cyan); animation:blink 1.1s steps(1) infinite;
}
@keyframes blink{50%{opacity:0}}
.tagline{color:var(--text-soft); max-width:760px; margin:12px 0 0; font-size:14px}
.tagline b{color:var(--text)}
.tagline code{font-family:var(--font-mono); font-size:12.5px; color:var(--cyan)}
.metrics{display:flex; gap:10px; flex-wrap:wrap; margin-top:18px}
.metric{
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r-sm);
  padding:9px 14px; min-width:112px; box-shadow:var(--shadow-hard-sm);
}
.metric .v{font-family:var(--font-pixel); font-size:19px; color:var(--cyan); line-height:1.2}
.metric.m2 .v{color:var(--magenta)} .metric.m3 .v{color:var(--lime)}
.metric .l{font-size:11px; color:var(--muted); margin-top:3px}

/* 필터바 */
.bar{
  position:sticky; top:var(--topbar-h); z-index:40; background:rgba(5,7,13,.92);
  backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px);
  border-bottom:1px solid var(--line); margin:0 0 22px; padding:10px 0;
}
.barin{max-width:1180px; margin:0 auto; padding:0 16px; display:flex; flex-direction:column; gap:8px}
.search{display:flex; align-items:center; gap:8px}
#q{
  flex:1; background:var(--surface-2); border:1px solid var(--line-strong); color:var(--text);
  border-radius:var(--r-sm); padding:10px 12px; font-size:16px; font-family:var(--font-body); outline:none;
}
#q:focus{border-color:var(--cyan); box-shadow:var(--glow-cyan)}
.count{font-family:var(--font-pixel); font-size:11.5px; color:var(--muted); white-space:nowrap}
.count b{color:var(--cyan)}
/* 필터 접기 — 모바일에서 칩 4줄이 첫 화면을 다 먹던 문제 */
.fbtn{
  display:none; align-items:center; gap:5px; padding:9px 11px; min-height:40px;
  background:var(--surface-2); border:1px solid var(--line-strong); color:var(--text-soft);
  border-radius:var(--r-sm); font-family:var(--font-pixel); font-size:11px; cursor:pointer;
  touch-action:manipulation; white-space:nowrap;
}
.fbtn.active{background:var(--cyan); color:#04202b; border-color:var(--cyan)}
.fbtn .fnum{font-family:var(--font-mono); font-size:10.5px}
.filters{display:flex; flex-direction:column; gap:8px}
.views{display:flex; gap:0}
.vbtn{
  padding:8px 10px; background:var(--surface-2); border:1px solid var(--line-strong); color:var(--muted);
  font-family:var(--font-pixel); font-size:11px; cursor:pointer; letter-spacing:.04em;
}
.vbtn:first-child{border-radius:var(--r-sm) 0 0 var(--r-sm)}
.vbtn:last-child{border-radius:0 var(--r-sm) var(--r-sm) 0; border-left:0}
.vbtn.on{background:var(--cyan); color:#04202b; border-color:var(--cyan)}
.chips{display:flex; gap:6px; flex-wrap:wrap; align-items:center}
.chips .lbl{
  font-family:var(--font-pixel); font-size:10px; color:var(--muted); letter-spacing:.1em;
  text-transform:uppercase; margin-right:2px;
}
.schip,.chip,.gchip,.tchip{
  border:1px solid var(--line); background:var(--surface-2); color:var(--muted);
  border-radius:var(--r-sm); padding:5px 10px; font-size:11.5px; font-weight:600; cursor:pointer;
  transition:.12s; user-select:none; font-family:var(--font-body);
}
.schip:hover,.chip:hover,.gchip:hover,.tchip:hover{color:var(--text); border-color:var(--line-strong)}
.schip.on{background:var(--text); color:var(--bg); border-color:var(--text)}
.chip.on{background:var(--cyan); color:#04202b; border-color:var(--cyan)}
.gchip.on{background:var(--amber); color:#231703; border-color:var(--amber)}
.tchip.on{background:var(--magenta); color:#2a0723; border-color:var(--magenta)}

/* 섹션 */
.domain{margin:0 auto 34px}
.dhead{display:flex; align-items:baseline; gap:10px; padding-bottom:6px; border-bottom:1px solid var(--line)}
.dhead .num{font-family:var(--font-pixel); font-size:12px; color:var(--cyan)}
.dhead h2{font-size:18px; font-weight:800; margin:0; letter-spacing:-.02em}
.dhead .cnt{font-family:var(--font-pixel); font-size:12px; color:var(--muted); margin-left:auto}
.dblurb{color:var(--muted); font-size:12.5px; margin:8px 0 14px}
.sub{margin:0 0 18px}
.sub .shead{
  font-family:var(--font-pixel); font-size:10.5px; color:var(--muted); letter-spacing:.1em;
  margin:0 0 10px; text-transform:uppercase;
}
.grid{display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:12px}

/* 카드 */
.card{
  background:var(--surface); border:1px solid var(--line); border-radius:var(--r-md);
  padding:14px; display:flex; flex-direction:column; gap:7px; position:relative;
  box-shadow:var(--shadow-hard-sm); scroll-margin-top:calc(var(--topbar-h) + var(--bar-h) + 14px);
  animation:rise .35s both; animation-delay:calc(var(--i,0)*14ms);
}
@keyframes rise{from{opacity:0; transform:translateY(6px)} to{opacity:1; transform:none}}
.card:hover{border-color:var(--line-strong)}
.card.flash{border-color:var(--cyan); box-shadow:0 0 0 2px rgba(62,230,255,.35), var(--shadow-hard-sm)}
.chead{display:flex; align-items:center; gap:6px; flex-wrap:wrap}
.chead .date{margin-left:auto}
.card h3{font-size:15px; font-weight:700; margin:2px 0 0; line-height:1.4; letter-spacing:-.02em}
.card h3 .tlink{text-decoration:none}
.card h3 .tlink:hover{color:var(--cyan)}
.desc{font-size:12.5px; color:var(--text-soft); margin:0; line-height:1.55}
.cmeta{font-family:var(--font-mono); font-size:11px; color:var(--muted); margin:0; word-break:break-all}
.acts{display:flex; gap:7px; margin-top:auto; padding-top:8px}

/* 목록(게시판) 모드 */
body.view-list .grid{display:flex; flex-direction:column; gap:0}
body.view-list .card{
  flex-direction:row; align-items:center; gap:10px; padding:9px 10px; border-radius:0;
  border-width:0 0 1px 0; box-shadow:none; animation:none;
}
body.view-list .card:hover{background:var(--surface); border-color:var(--line-strong)}
body.view-list .chead{order:1; flex:0 0 auto; gap:5px}
body.view-list .chead .date{display:none}
body.view-list .card h3{order:2; flex:1; margin:0; font-size:13.5px; font-weight:600;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
body.view-list .desc{display:none}
body.view-list .cmeta{order:3; display:none}
body.view-list .acts{order:4; margin:0; padding:0; flex:0 0 auto}
body.view-list .acts .btn{padding:5px 9px; font-size:11px; box-shadow:none}
body.view-list .acts .btn.primary{display:none}
body.view-list .sub .shead{margin-bottom:6px}
@media(min-width:721px){
  body.view-list .card::after{
    content:attr(data-date); order:5; font-family:var(--font-mono); font-size:11px;
    color:var(--muted); flex:0 0 82px; text-align:right;
  }
}

.empty{margin:56px auto; text-align:center; color:var(--muted)}
.empty h3{color:var(--text); font-size:17px}
@media(max-width:720px){
  .grid{grid-template-columns:1fr}
  .hero{padding:18px 0 14px}
  .tagline{font-size:13px}
  .fbtn{display:inline-flex}
  /* 기본은 접힘 — [필터] 로 펼친다 */
  .filters{display:none}
  .filters.open{display:flex}
  .vbtn{padding:10px 12px; min-height:40px}
  .schip,.chip,.gchip,.tchip{padding:8px 12px; font-size:12px; min-height:36px}
  /* 목록 모드: 제목 줄 자체가 넉넉한 탭 영역이 되게 */
  body.view-list .card{padding:12px 8px}
  body.view-list .card h3{font-size:14px}
  body.view-list .card h3 .tlink{display:block; padding:3px 0}
}
@media(max-width:560px){
  /* 검색창이 눌리지 않게 — 보기 전환/카운트는 아랫줄로 */
  .search{flex-wrap:wrap}
  #q{flex:1 1 100%}
  .views{margin-left:auto}
}
"""

# ── 게시글 상세 ─────────────────────────────────────────────────
PAGE_CSS = r"""
.post{
  max-width:820px; margin:0 auto;
  padding:18px calc(16px + var(--safe-right)) calc(96px + var(--safe-bottom)) calc(16px + var(--safe-left));
}
/* 톱바 왼쪽 = 뒤로가기 (standalone PWA 는 브라우저 뒤로가기 버튼이 없다) */
.back-chip{
  background:var(--cyan); color:#04202b; border-color:var(--cyan);
  box-shadow:3px 3px 0 var(--cyan-deep); font-weight:700;
}
.back-chip:hover{background:var(--cyan); filter:brightness(1.06); box-shadow:3px 3px 0 var(--cyan-deep)}
.back-chip:active{transform:translate(2px,2px); box-shadow:1px 1px 0 var(--cyan-deep)}
.topbar .brand-name{font-size:12px}
/* 스크롤 내려가면 뜨는 플로팅 뒤로가기 — 긴 글 끝에서 위로 안 올라가도 된다 */
.fabs{
  position:fixed; z-index:60; left:calc(14px + var(--safe-left)); right:calc(14px + var(--safe-right));
  bottom:calc(14px + var(--safe-bottom)); display:flex; justify-content:space-between;
  pointer-events:none; opacity:0; transform:translateY(14px); transition:opacity .18s, transform .18s;
}
.fabs.on{opacity:1; transform:none}
.fabs.on > *{pointer-events:auto}
.fab{
  display:inline-flex; align-items:center; justify-content:center; gap:6px; min-height:46px;
  padding:11px 16px; border-radius:999px; text-decoration:none; cursor:pointer;
  font-family:var(--font-pixel); font-size:11.5px; letter-spacing:.06em;
  background:var(--cyan); color:#04202b; border:1px solid var(--cyan);
  box-shadow:var(--shadow-hard); touch-action:manipulation;
}
.fab.ghost{background:var(--surface-2); color:var(--text-soft); border-color:var(--line-strong)}
.fab:active{transform:translate(2px,2px); box-shadow:1px 1px 0 rgba(0,0,0,.4)}
/* 글 끝 — 다음 행동(목록/맨 위)을 손 닿는 곳에 */
.post-end{display:flex; gap:8px; margin-top:30px; padding-top:18px; border-top:1px solid var(--line)}
.post-end .btn{flex:1; justify-content:center; min-height:46px}
.post h1{
  font-size:clamp(22px,4vw,32px); line-height:1.28; margin:0 0 10px; font-weight:800; letter-spacing:-.03em;
}
.pmeta{display:flex; align-items:center; gap:7px; flex-wrap:wrap; margin-bottom:14px}
.pmeta .tag{
  font-size:11.5px; color:var(--muted); background:var(--surface-2); border:1px solid var(--line);
  border-radius:var(--r-sm); padding:3px 8px;
}
.slugline{
  font-family:var(--font-mono); font-size:11.5px; color:var(--cyan); background:var(--surface);
  border:1px solid var(--line); border-radius:var(--r-sm); padding:7px 10px; margin:0 0 14px;
  word-break:break-all;
}
.pacts{display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px}
.callout{
  background:rgba(62,230,255,.07); border:1px solid rgba(62,230,255,.3); border-left:3px solid var(--cyan);
  border-radius:var(--r-sm); padding:12px 14px; margin:0 0 20px; color:var(--text-soft); font-size:13.5px;
}
.md{font-size:15px; line-height:1.78; color:var(--text-soft)}
.md h2{
  font-size:19px; color:var(--text); margin:30px 0 10px; padding-bottom:6px;
  border-bottom:1px solid var(--line); letter-spacing:-.02em; font-weight:800;
}
.md h3{font-size:16px; color:var(--text); margin:22px 0 8px; font-weight:700}
.md h4{font-size:14px; color:var(--text); margin:18px 0 6px}
.md p{margin:0 0 14px}
.md strong{color:var(--text)}
.md ul,.md ol{padding-left:20px; margin:0 0 14px}
.md li{margin:4px 0}
.md code{
  font-family:var(--font-mono); font-size:13px; background:var(--surface-2); border:1px solid var(--line);
  border-radius:var(--r-sm); padding:1px 5px; color:var(--cyan);
}
.md pre{
  background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--magenta);
  border-radius:var(--r-sm); padding:13px 15px; overflow-x:auto; font-size:13px; line-height:1.6;
  box-shadow:var(--shadow-hard-sm);
}
.md pre code{border:0; background:transparent; padding:0; color:var(--text-soft)}
.md table{border-collapse:collapse; width:100%; font-size:13.5px; display:block; overflow-x:auto; margin:0 0 16px}
.md th,.md td{border:1px solid var(--line); padding:7px 10px; text-align:left}
.md th{color:var(--text); background:var(--surface-2); font-family:var(--font-pixel); font-size:11.5px}
.md blockquote{border-left:3px solid var(--magenta); margin:0 0 14px; padding:4px 14px; color:var(--muted)}
.md a{color:var(--cyan)}
.md hr{border:0; border-top:1px dashed var(--line); margin:22px 0}
.psec{margin-top:34px; padding-top:16px; border-top:1px solid var(--line)}
.psec h2{
  font-family:var(--font-pixel); font-size:12px; color:var(--muted); letter-spacing:.1em;
  text-transform:uppercase; margin:0 0 10px;
}
.srcs a{color:var(--cyan); font-size:13px; word-break:break-all; display:block; margin:5px 0}
.related{list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:0}
.related li{border-bottom:1px solid var(--line)}
.related a{
  display:flex; align-items:center; gap:8px; padding:9px 2px; text-decoration:none; font-size:13.5px;
  color:var(--text-soft);
}
.related a:hover{color:var(--cyan)}
.related .rt{flex:1; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
"""

CATALOG_JS = r"""
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
    s.classList.toggle('hidden', !shown(s));
    const k = [...s.querySelectorAll('.card')].filter(c => !c.classList.contains('hidden')).length;
    const el = s.querySelector('.dhead .cnt'); if (el) el.textContent = k;
  }
  cnt.textContent = n + '개';
  empty.classList.toggle('hidden', n > 0);
  if (typeof refreshFbtn === 'function') refreshFbtn();
}

const qi = document.getElementById('q');
qi.addEventListener('input', e => { q = e.target.value.trim().toLowerCase(); apply(); });
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== qi) { e.preventDefault(); qi.focus(); }
  if (e.key === 'Escape' && document.activeElement === qi) { qi.value = ''; q = ''; apply(); qi.blur(); }
});
function toggleGroup(sel, setter) {
  for (const b of document.querySelectorAll(sel)) b.addEventListener('click', () => {
    const was = b.classList.contains('on');
    document.querySelectorAll(sel).forEach(x => x.classList.remove('on'));
    if (was) { setter(null); } else { b.classList.add('on'); setter(b.dataset.dom || b.dataset.grade || b.dataset.tool); }
    apply();
  });
}
for (const b of document.querySelectorAll('.schip')) b.addEventListener('click', () => {
  document.querySelectorAll('.schip').forEach(x => x.classList.remove('on'));
  b.classList.add('on'); src = b.dataset.src; apply();
});
toggleGroup('.chip', v => { dom = v; });
toggleGroup('.gchip', v => { grade = v; });
toggleGroup('.tchip', v => { tool = v; });

/* 보기 전환 (카드 ⇄ 목록) — 선택은 기기에 기억 */
const VIEW_KEY = 'aiskillbox-catalog-view';
function setView(v) {
  document.body.classList.toggle('view-list', v === 'list');
  document.querySelectorAll('.vbtn').forEach(b => b.classList.toggle('on', b.dataset.view === v));
  try { localStorage.setItem(VIEW_KEY, v); } catch (_) {}
}
document.querySelectorAll('.vbtn').forEach(b => b.addEventListener('click', () => setView(b.dataset.view)));
let saved = 'card';
try { saved = localStorage.getItem(VIEW_KEY) || 'card'; } catch (_) {}
setView(saved);

/* 스티키 스택 실측 — 톱바/필터바 높이를 CSS 변수로 (하드코딩 52/48px 제거) */
const topbarEl = document.querySelector('.topbar');
const barEl = document.querySelector('.bar');
function measureSticky() {
  const r = document.documentElement.style;
  if (topbarEl) r.setProperty('--topbar-h', Math.round(topbarEl.getBoundingClientRect().height) + 'px');
  if (barEl) r.setProperty('--bar-h', Math.round(barEl.getBoundingClientRect().height) + 'px');
}
measureSticky();
addEventListener('resize', measureSticky);
addEventListener('orientationchange', () => setTimeout(measureSticky, 220));
if (window.ResizeObserver) {
  const ro = new ResizeObserver(measureSticky);
  if (topbarEl) ro.observe(topbarEl);
  if (barEl) ro.observe(barEl);
}

/* 필터 접기 (모바일) — 첫 화면을 칩 4줄이 먹지 않게 */
const filtersEl = document.getElementById('filters');
const fbtn = document.getElementById('fbtn');
function activeFilterCount() {
  return (src !== 'all' ? 1 : 0) + (dom ? 1 : 0) + (grade ? 1 : 0) + (tool ? 1 : 0);
}
function refreshFbtn() {
  if (!fbtn) return;
  const n = activeFilterCount();
  fbtn.classList.toggle('active', n > 0);
  fbtn.querySelector('.fnum').textContent = n ? ' ' + n : '';
  fbtn.setAttribute('aria-expanded', filtersEl.classList.contains('open') ? 'true' : 'false');
}
if (fbtn && filtersEl) {
  fbtn.addEventListener('click', () => {
    filtersEl.classList.toggle('open');
    refreshFbtn();
    measureSticky();
  });
}

/* 목록 ⇄ 글 왕복 — 검색어·필터·보기·스크롤 위치를 되살린다 (뒤로가기 체감의 핵심) */
const STATE_KEY = 'aiskillbox-catalog-state';
function saveState() {
  try {
    sessionStorage.setItem(STATE_KEY, JSON.stringify({
      q: qi.value, src, dom, grade, tool,
      list: document.body.classList.contains('view-list'),
      y: window.scrollY, open: filtersEl ? filtersEl.classList.contains('open') : false,
    }));
  } catch (_) {}
}
function pressChip(sel, attr, value) {
  if (!value) return;
  for (const b of document.querySelectorAll(sel)) {
    if (b.dataset[attr] === value) b.classList.add('on');
    else b.classList.remove('on');
  }
}
/* 목표 위치까지 여러 프레임에 걸쳐 되돌린다 — 첫 프레임엔 문서가 아직 짧아서
   scrollTo 가 최대 스크롤로 잘린다 (실측: 1635 요청 → 1300 착지). */
function restoreScroll(y, tries) {
  tries = tries === undefined ? 12 : tries;
  window.scrollTo({ top: y, behavior: 'auto' });   // html{scroll-behavior:smooth} 무시 — 복귀는 즉시
  if (tries <= 0 || Math.abs(window.scrollY - y) < 4) return;
  requestAnimationFrame(() => restoreScroll(y, tries - 1));
}
function restoreState() {
  let st = null;
  try { st = JSON.parse(sessionStorage.getItem(STATE_KEY) || 'null'); } catch (_) {}
  if (!st) return false;
  qi.value = st.q || '';
  q = (st.q || '').trim().toLowerCase();
  src = st.src || 'all'; dom = st.dom || null; grade = st.grade || null; tool = st.tool || null;
  for (const b of document.querySelectorAll('.schip')) b.classList.toggle('on', b.dataset.src === src);
  pressChip('.chip', 'dom', dom);
  pressChip('.gchip', 'grade', grade);
  pressChip('.tchip', 'tool', tool);
  if (filtersEl && st.open) filtersEl.classList.add('open');
  apply();
  refreshFbtn();
  if (typeof st.y === 'number' && st.y > 0 && !location.hash) restoreScroll(st.y);
  return true;
}
addEventListener('pagehide', saveState);
addEventListener('beforeunload', saveState);
for (const a of document.querySelectorAll('.card a')) a.addEventListener('click', saveState);

/* 이전 버전 딥링크(/catalog#slug) 호환 — 해당 글로 스크롤 + 강조 */
function flashFromHash() {
  const slug = decodeURIComponent((location.hash || '').slice(1));
  if (!slug) return;
  const card = document.getElementById(slug);
  if (!card) return;
  card.scrollIntoView({ block: 'center' });
  card.classList.add('flash');
  setTimeout(() => card.classList.remove('flash'), 2600);
}
window.addEventListener('hashchange', flashFromHash);
if (!restoreState()) apply();
flashFromHash();
measureSticky();
"""

PAGE_JS = r"""
/* ── 뒤로가기 동선 ─────────────────────────────────────────
   목록에서 들어왔으면 history.back() — 카탈로그의 스크롤/필터가 그대로 살아난다.
   직접 링크로 들어왔거나 standalone PWA 첫 화면이면 /catalog 로 이동. */
function cameFromCatalog() {
  try {
    if (!document.referrer) return false;
    const u = new URL(document.referrer);
    return u.origin === location.origin
      && (u.pathname === '/catalog' || u.pathname === '/catalog.html');
  } catch (_) { return false; }
}
function goBack(ev) {
  if (ev) ev.preventDefault();
  if (cameFromCatalog() && history.length > 1) history.back();
  else location.href = '/catalog';
}
for (const el of document.querySelectorAll('[data-back]')) el.addEventListener('click', goBack);

for (const el of [document.getElementById('to-top'), document.getElementById('to-top-fab')]) {
  if (el) el.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* 조금이라도 내려가면 플로팅 [목록]/[위로] 노출 */
const fabs = document.getElementById('fabs');
let _fabTick = false;
function syncFabs() {
  _fabTick = false;
  if (fabs) fabs.classList.toggle('on', window.scrollY > 260);
}
addEventListener('scroll', () => {
  if (_fabTick) return;
  _fabTick = true;
  requestAnimationFrame(syncFabs);
}, { passive: true });
syncFabs();

/* 왼쪽 가장자리 스와이프 → 목록 (PWA 에는 브라우저 뒤로가기 제스처가 없다).
   코드블록/표의 가로 스크롤을 방해하지 않도록 시작 지점을 32px 이내로 제한. */
(function edgeSwipeBack() {
  let sx = null, sy = null, blocked = false;
  addEventListener('touchstart', (e) => {
    if (e.touches.length !== 1) { sx = null; return; }
    const t = e.touches[0];
    if (t.clientX > 32) { sx = null; return; }
    sx = t.clientX; sy = t.clientY;
    blocked = !!(e.target.closest && e.target.closest('pre, table, .md table'));
  }, { passive: true });
  addEventListener('touchend', (e) => {
    if (sx === null || blocked) { sx = null; return; }
    const t = e.changedTouches[0];
    if (t.clientX - sx > 72 && Math.abs(t.clientY - sy) < 56) goBack();
    sx = null;
  }, { passive: true });
})();

const toast = document.getElementById('toast');
let tt;
function showToast(msg) {
  toast.textContent = msg; toast.classList.add('on');
  clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('on'), 2400);
}
async function copyText(text) {
  try { await navigator.clipboard.writeText(text); }
  catch (_) {
    const ta = document.createElement('textarea');
    ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.appendChild(ta); ta.select(); document.execCommand('copy'); ta.remove();
  }
}
document.addEventListener('click', async e => {
  const cp = e.target.closest('#copy-md');
  if (cp) {
    e.preventDefault();
    await copyText(document.getElementById('raw-md').textContent);
    cp.classList.add('done');
    showToast('SKILL.md 전문을 복사했습니다 — 다른 기기면 ~/.claude/skills/<슬러그>/SKILL.md 로 저장');
    setTimeout(() => cp.classList.remove('done'), 2000);
    return;
  }
  const lk = e.target.closest('#copy-link');
  if (lk) {
    e.preventDefault();
    await copyText(location.origin + location.pathname);
    showToast('이 글의 링크를 복사했습니다');
  }
});
"""

CATALOG_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="theme-color" content="#05070d">
<meta name="robots" content="noindex">
<meta name="format-detection" content="telephone=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="aiskillbox">
<link rel="manifest" href="/static/manifest.json">
<link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
<title>{title}</title>
{fonts}
<style>{css}</style>
</head>
<body>
<div class="bg-fx" aria-hidden="true"></div>

<header class="topbar">
  <a class="brand" href="/"><span class="brand-logo">🧠</span><span class="brand-name">aiskillbox</span></a>
  <div class="topbar-actions">
    <a class="chip-link" href="/">＋ 수집</a>
  </div>
</header>

<div class="wrap">
  <header class="hero">
    <div class="kicker">두근컴퍼니 · SKILL LIBRARY · {generated_kst} KST</div>
    <h1><span class="a">스킬</span><span class="b">도서관</span><i class="cursor"></i></h1>
    <p class="tagline">수집한 콘텐츠를 <b>SKILL.md</b> 로 자산화한 게시판입니다.
    제목을 누르면 <b>사이트 안에서</b> 전문을 읽고, 원본이 필요할 때만 <b>원본 ↗</b> 로 나갑니다.
    AI 는 같은 자료를 <code>/api/library/search</code> · MCP <code>search_skills</code> 로 씁니다.</p>
    <div class="metrics">
      <div class="metric m1"><div class="v">{total}</div><div class="l">등록 스킬</div></div>
      <div class="metric m2"><div class="v">{n_categories}</div><div class="l">카테고리</div></div>
      <div class="metric m3"><div class="v">{last_updated_short}</div><div class="l">마지막 갱신</div></div>
    </div>
  </header>
</div>

<div class="bar"><div class="barin">
  <div class="search">
    <input id="q" placeholder="스킬 검색  ( / 포커스 · Esc 초기화 )" autocomplete="off">
    <button class="fbtn" id="fbtn" type="button" aria-expanded="false" aria-controls="filters">필터<span class="fnum"></span></button>
    <div class="views">
      <button class="vbtn" data-view="card">카드</button>
      <button class="vbtn" data-view="list">목록</button>
    </div>
    <span class="count"><b id="cnt">{total}개</b></span>
  </div>
  <div class="filters" id="filters">
    <div class="chips"><span class="lbl">출처</span><button class="schip on" data-src="all">전체</button>{source_chips}</div>
    <div class="chips"><span class="lbl">카테고리</span>{category_chips}</div>
    <div class="chips"><span class="lbl">등급</span>{grade_chips}</div>
    <div class="chips"><span class="lbl">AI 도구</span>{tool_chips}</div>
  </div>
</div></div>

<div class="wrap">
{sections}
<div class="empty hidden">
  <h3>조건에 맞는 스킬이 없어요</h3>
  <p>검색어나 필터를 바꿔보세요. (Esc 로 검색 초기화)</p>
</div>
</div>

<script nonce="{nonce}">{js}</script>
</body>
</html>
"""

SKILL_PAGE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<meta http-equiv="Content-Security-Policy" content="{csp}">
<meta name="theme-color" content="#05070d">
<meta name="robots" content="noindex">
<meta name="format-detection" content="telephone=no">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="aiskillbox">
<link rel="manifest" href="/static/manifest.json">
<link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
<title>{title} · 두근 스킬 도서관</title>
{fonts}
<style>{css}</style>
</head>
<body>
<div class="bg-fx" aria-hidden="true"></div>

<header class="topbar">
  <a class="chip-link back-chip" href="/catalog" data-back>← 목록</a>
  <div class="topbar-actions">
    <a class="brand" href="/"><span class="brand-logo">🧠</span><span class="brand-name">aiskillbox</span></a>
  </div>
</header>

<article class="post">
  <h1>{title}</h1>
  <div class="pmeta">{meta_chips}</div>
  <p class="slugline">~/.claude/skills/{slug}/SKILL.md</p>
  <div class="pacts">
    <button class="btn primary" id="copy-md">SKILL.md 복사</button>
    {origin_button}
    <button class="btn" id="copy-link">링크 복사</button>
  </div>
  {callout}
  <div class="md">{body_html}</div>

  <section class="psec">
    <h2>원본 출처</h2>
    <div class="srcs">{sources_html}</div>
  </section>
  {related_html}

  <div class="post-end">
    <a class="btn primary" href="/catalog" data-back>← 목록으로</a>
    <button class="btn" id="to-top" type="button">↑ 맨 위로</button>
  </div>
</article>

<div class="fabs" id="fabs">
  <a class="fab" href="/catalog" data-back>← 목록</a>
  <button class="fab ghost" type="button" id="to-top-fab" aria-label="맨 위로">↑</button>
</div>

<pre id="raw-md" class="hidden">{raw_md}</pre>
<div id="toast"></div>
<script nonce="{nonce}">{js}</script>
</body>
</html>
"""
