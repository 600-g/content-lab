"""디지몬 진화 도감(digicord.600g.net) 읽기 도구 — 같은 MCP 서버(stdio + 원격 커넥터)에 얹힌다.

자료는 같은 맥의 디지몬 매크로 서버(`~/discordbot`, :9876)가 만든 공용 백과사전 `GET /api/encyclo` 와
루트 탐색 `GET /api/evo/route` 다. 여기서는 **읽기만** 하고, 숫자는 봇 화면에서 읽은 값과 사이트 값을
구분해 보여 준다 (사이트 값은 '검증 전'). 네트워크 실패는 isError 로 — 스킬 도구에 영향 없음.

DIGICORD_URL 환경변수로 백엔드를 바꿀 수 있다 (기본 http://127.0.0.1:9876). 테스트는 `set_fetcher` 로 가짜를 꽂는다.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Optional

BASE_URL = os.environ.get("DIGICORD_URL", "http://127.0.0.1:9876").rstrip("/")
PUBLIC_URL = "https://digicord.600g.net"
HTTP_TIMEOUT = float(os.environ.get("DIGICORD_TIMEOUT", "8"))
CACHE_TTL = 600.0
MAX_ROUTES = 12

TOOLS: list[dict] = [
    {
        "name": "digimon_search",
        "description": (
            "디지몬 진화 도감(디지펫 바이탈 디스코드 봇 기준)에서 디지몬 이름이나 DIM 이름을 찾습니다. "
            "이름이 정확하지 않을 때 먼저 호출 — 결과: 종 이름·단계·속성·소속 DIM, 또는 DIM 이름·획득처."
        ),
        "inputSchema": {"type": "object", "properties": {"query": {"type": "string", "description": "디지몬 또는 DIM 이름 일부 (2자 이상)"}},
                        "required": ["query"]},
    },
    {
        "name": "digimon_species",
        "description": (
            "디지몬 한 종의 도감 정보: 기본 스탯(체력·전투력·속도), 단계·속성, 소속 DIM, 이전/다음 진화와 조건. "
            "조건 숫자는 봇 화면에서 읽은 값이 기본이고, 봇 기록이 없는 곳만 사이트 값을 '검증 전' 으로 붙입니다."
        ),
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string", "description": "디지몬 이름 (예: 파피몬, 오메가몬 X)"}},
                        "required": ["name"]},
    },
    {
        "name": "digimon_route",
        "description": "목표 디지몬까지의 진화 루트(알 → … → 목표)와 단계별 조건을 짧은 순으로 보여 줍니다. '이거 어떻게 만들어?' 에 씁니다.",
        "inputSchema": {"type": "object", "properties": {"name": {"type": "string", "description": "목표 디지몬 이름"},
                                                         "limit": {"type": "integer", "minimum": 1, "maximum": MAX_ROUTES, "description": "루트 수 (기본 5)"}},
                        "required": ["name"]},
    },
    {
        "name": "digimon_rank",
        "description": "단계별 스탯 순위: 봇 도감에서 스탯이 확인된 종을 같은 단계끼리 총합(체력+전투력+속도) 또는 체력/전투력/속도 높은 순으로. "
                       "등급은 같은 단계 안 상위 35% S · 70% A · 90% B · 나머지 C · 꼴찌 D. '성숙기에서 체력 제일 높은 애?' 에 씁니다.",
        "inputSchema": {"type": "object", "properties": {"stage": {"type": "string", "description": "단계 (성장기|성숙기|완전체|궁극체|초궁극체 — 유년기는 순위 밖). 비우면 전 단계 상위만"},
                                                         "sort": {"type": "string", "description": "total|hp|atk|spd (기본 total)"},
                                                         "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "표시 수 (기본 10)"}},
                        "required": []},
    },
    {
        "name": "digimon_dim",
        "description": "DIM 하나의 진화 트리 전체: 획득처, 단계(열)별 디지몬 이름, 진화선(부모 → 자식), 아직 이름을 모르는 칸 수. 추정·사이트 근거는 표시합니다.",
        "inputSchema": {"type": "object", "properties": {"dim": {"type": "string", "description": "DIM 이름 (예: 파피몬 EX, 에인션트 워리어즈)"}},
                        "required": ["dim"]},
    },
]

_fetch: Optional[Callable[[str], dict]] = None
_cache: dict[str, tuple[float, dict]] = {}


def set_fetcher(fn: Optional[Callable[[str], dict]]) -> None:
    """테스트용: path → dict 를 돌려주는 가짜. None 이면 HTTP."""
    global _fetch
    _fetch = fn
    _cache.clear()


def _http(path: str) -> dict:
    req = urllib.request.Request(BASE_URL + path, headers={"Accept": "application/json", "User-Agent": "aiskillbox-mcp/1"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as f:
        return json.loads(f.read().decode("utf-8"))


def _get(path: str, ttl: float = CACHE_TTL) -> dict:
    hit = _cache.get(path)
    if hit and time.monotonic() - hit[0] < ttl:
        return hit[1]
    data = (_fetch or _http)(path)
    if not isinstance(data, dict) or not data.get("ok", True):
        raise RuntimeError(str((data or {}).get("error") or "도감 응답이 비었습니다"))
    _cache[path] = (time.monotonic(), data)
    return data


def _enc() -> dict:
    return _get("/api/encyclo")


def _norm(s: str) -> str:
    return re.sub(r"[\s()\-·:_]", "", str(s or "")).lower().replace("x항체", "x")


def find_species(enc: dict, name: str) -> Optional[str]:
    sp = enc.get("species") or {}
    key = _norm(name)
    if not key:
        return None
    if name in sp:
        return name
    exact = [n for n in sp if _norm(n) == key]
    if exact:
        return exact[0]
    starts = sorted((n for n in sp if _norm(n).startswith(key)), key=len)
    if starts:
        return starts[0]
    contains = sorted((n for n in sp if key in _norm(n)), key=len)
    return contains[0] if contains else None


def find_dim(enc: dict, name: str) -> Optional[str]:
    dims = enc.get("dims") or {}
    key = _norm(name)
    if not key:
        return None
    if name in dims:
        return name
    for n in dims:
        if _norm(n) == key:
            return n
    cands = sorted((n for n in dims if key in _norm(n) or _norm(n).startswith(key)), key=len)
    return cands[0] if cands else None


# ── 표시 ────────────────────────────────────────────────────────────
_COND_LABEL = [("vital", "바이탈"), ("pp", "PP"), ("battle", "배틀"), ("winrate", "승률"), ("evotime_h", "진화시간"),
               ("evotime", "진화시간"), ("dungeon", "던전"), ("jogress", "조그레스"), ("item", "아이템"), ("items", "아이템")]


def cond_text(cond: dict | None) -> str:
    if not cond:
        return "조건 미확인"
    parts = []
    for k, label in _COND_LABEL:
        if k not in cond or cond[k] in (None, "", "-", []):
            continue
        v = cond[k]
        if k == "winrate":
            parts.append(f"{label} {v}%+" if str(v).replace(".", "").isdigit() else f"{label} {v}")
        elif k == "evotime_h":
            parts.append(f"{label} {v}시간")
        elif k == "dungeon" and str(v).isdigit():
            parts.append(f"{label} {'★' * int(v)}")
        elif k in ("vital", "pp", "battle") and str(v).replace(",", "").isdigit():
            parts.append(f"{label} {v}+")
        else:
            parts.append(f"{label} {v if not isinstance(v, list) else ', '.join(map(str, v))}")
    extra = {k: v for k, v in cond.items() if k not in dict(_COND_LABEL) and v not in (None, "", "-")}
    parts += [f"{k} {v}" for k, v in extra.items()]
    return " · ".join(parts) if parts else "조건 미확인"


def _rel_lines(s: dict, key: str, site_key: str, arrow: str) -> list[str]:
    out = []
    seen = set()
    for x in s.get(key) or []:
        n = x.get("name") or "???"
        seen.add(n)
        tag = ""
        if x.get("kind") == "measured" or x.get("observed"):
            tag = " (봇 기록)"
        out.append(f"  {arrow} {n}: {cond_text(x.get('cond'))}{tag}")
    for x in s.get(site_key) or []:
        n = x.get("name") or "???"
        if n in seen:
            continue
        out.append(f"  {arrow} {n}: {cond_text(x.get('cond'))} (사이트 값 · 검증 전)")
    return out


def fmt_species(enc: dict, name: str) -> str:
    s = (enc.get("species") or {})[name]
    st = s.get("stats") or {}
    lines = [f"# {name}", f"단계 {s.get('stage') or '?'} · 속성 {s.get('attr') or '?'}"]
    if st:
        lines.append(f"기본 스탯: 체력 {st.get('hp', '?')} · 전투력 {st.get('atk', '?')} · 속도 {st.get('spd', '?')} (봇 도감 실측)")
        r = s.get("rank")
        if r:
            lines.append(f"등급 {r['grade']} — {r['stage']} 총합 {r['total']} · {r['pos']}위/{r['n']} (같은 단계 안 상위 35% S·70% A·90% B·꼴찌 D)")
    else:
        lines.append("기본 스탯: 봇 도감 기록 없음")
    dims = list(s.get("dims") or []) + [f"{d}(추정)" for d in (s.get("dims_est") or [])]
    lines.append("소속 DIM: " + (", ".join(dims) if dims else "미확인"))
    prev = _rel_lines(s, "from", "site_from", "←")
    nxt = _rel_lines(s, "to", "site_to", "→")
    lines.append("이전 진화:" if prev else "이전 진화: 기록 없음")
    lines += prev
    lines.append("다음 진화:" if nxt else "다음 진화: 기록 없음 (최종 단계이거나 미해금)")
    lines += nxt
    if s.get("report"):
        lines.append("※ 이 종의 상세는 사용자 제보 글 기준")
    agree = enc.get("site_agree") or {}
    n = (agree.get("match") or 0) + (agree.get("mismatch") or 0)
    if n:
        lines.append(f"※ '사이트 값' 은 digipetdex 자료로 봇 기록과 {round(agree['match'] / n * 100)}% 일치 — 확정 아님")
    lines.append(f"{PUBLIC_URL}/?q={urllib.parse.quote(name)}")
    return "\n".join(lines)


def fmt_dim(enc: dict, dim: str) -> str:
    d = (enc.get("dims") or {})[dim]
    L = d.get("layout") or {}
    tiles = L.get("tiles") or []
    lines = [f"# DIM {dim}", f"획득처 {d.get('region') or '?'} · 공식 {d.get('total') or '?'}종 + 알"]
    if not tiles:
        lines.append("봇 도감 카드가 아직 없어 트리를 모릅니다.")
        return "\n".join(lines)
    check = L.get("check") or {}
    lines.append(f"이름 확인 {check.get('named', 0)}/{check.get('tiles', len(tiles))}칸" + (f" · 모순 {check.get('bad')}" if check.get("bad") else ""))
    sp = enc.get("species") or {}
    by_col: dict[int, list[str]] = {}
    for t in tiles:
        n = t.get("name")
        if n:
            basis = t.get("basis")
            tag = " (추정)" if basis in ("shape", "elim") else (" (사이트)" if basis == "site" else "")
            by_col.setdefault(t["col"], []).append(n + tag)
        else:
            by_col.setdefault(t["col"], []).append("???")
    stage_of = {}
    for c, names in by_col.items():
        sts = [sp.get(n.split(" (")[0], {}).get("stage") for n in names if n != "???"]
        sts = [x for x in sts if x]
        stage_of[c] = max(set(sts), key=sts.count) if sts else ("알" if c == 0 else "?")
    for c in sorted(by_col):
        lines.append(f"- {stage_of[c]}: " + ", ".join(by_col[c]))
    edges = []
    for a, b in L.get("lines") or []:
        edges.append(f"{tiles[a].get('name') or '???'} → {tiles[b].get('name') or '???'}")
    for a, b in L.get("site_lines") or []:
        edges.append(f"{tiles[a].get('name') or '???'} → {tiles[b].get('name') or '???'} (사이트에만 있는 선)")
    if edges:
        lines.append("진화선: " + " / ".join(edges))
    lines.append(f"{PUBLIC_URL}/?dim={urllib.parse.quote(dim)}")
    return "\n".join(lines)


def fmt_search(enc: dict, query: str) -> str:
    key = _norm(query)
    sp = enc.get("species") or {}
    dims = enc.get("dims") or {}
    hits = sorted((n for n in sp if key in _norm(n) and not n.endswith("알")), key=len)[:15]
    dhits = sorted((n for n in dims if key in _norm(n)), key=len)[:10]
    if not hits and not dhits:
        return f"'{query}' 에 맞는 디지몬·DIM 이 없습니다 (도감 {len(sp)}종 · {len(dims)} DIM)."
    out = []
    for n in hits:
        s = sp[n]
        dd = ", ".join(s.get("dims") or []) or "DIM 미확인"
        out.append(f"- {n} · {s.get('stage') or '?'} · {s.get('attr') or '?'} · {dd}")
    for n in dhits:
        out.append(f"- [DIM] {n} · 획득처 {dims[n].get('region') or '?'}")
    return "\n".join(out)


def _stat(sp: dict, n: str, k: str) -> int:
    st = sp[n]["stats"]
    return st["hp"] + st["atk"] + st["spd"] if k == "total" else st[k]


def fmt_rank(enc: dict, stage: str, sort: str, limit: int) -> str:
    ranks, sp = enc.get("ranks") or {}, enc.get("species") or {}
    if not ranks:
        return "순위 자료가 아직 없습니다 (도감 재빌드 전)."
    label = {"total": "총합", "hp": "체력", "atk": "전투력", "spd": "속도"}[sort]
    stages = [s for s in ranks if not stage or _norm(s) == _norm(stage) or _norm(stage) in _norm(s)]
    if not stages:
        return f"'{stage}' 단계가 없습니다. 있는 단계: " + ", ".join(ranks)
    out = []
    for stg in stages:
        names = sorted(ranks[stg], key=lambda n: (-_stat(sp, n, sort), -_stat(sp, n, "total"), n))[: (limit if stage else 3)]
        out.append(f"# {stg} — {label} 높은 순 (스탯 확인 {len(ranks[stg])}종)")
        for i, n in enumerate(names, 1):
            st, r = sp[n]["stats"], sp[n].get("rank") or {}
            out.append(f"{i}. {n} [{r.get('grade', '?')}] 체력 {st['hp']} · 전투력 {st['atk']} · 속도 {st['spd']} · 총합 {st['hp'] + st['atk'] + st['spd']}")
    return "\n".join(out)


def call(name: str, args: dict) -> tuple[str, bool]:
    """(text, is_error). 이름이 이 모듈 것이 아니면 (None, …) 대신 '알 수 없는 도구'."""
    try:
        if name == "digimon_search":
            q = str(args.get("query", "")).strip()
            if len(q) < 2:
                return "query 는 2자 이상이어야 합니다.", True
            return fmt_search(_enc(), q), False
        if name == "digimon_species":
            enc = _enc()
            found = find_species(enc, str(args.get("name", "")))
            if not found:
                return f"'{args.get('name')}' 를 도감에서 찾지 못했습니다 — digimon_search 로 이름을 확인하세요.", True
            return fmt_species(enc, found), False
        if name == "digimon_dim":
            enc = _enc()
            found = find_dim(enc, str(args.get("dim", "")))
            if not found:
                return f"'{args.get('dim')}' DIM 이 없습니다. 있는 DIM: " + ", ".join(sorted(enc.get("dims") or {})), True
            return fmt_dim(enc, found), False
        if name == "digimon_rank":
            sort = str(args.get("sort") or "total").lower()
            if sort not in ("total", "hp", "atk", "spd"):
                return "sort 는 total|hp|atk|spd 중 하나입니다.", True
            try:
                limit = max(1, min(50, int(args.get("limit") or 10)))
            except (TypeError, ValueError):
                limit = 10
            return fmt_rank(_enc(), str(args.get("stage") or "").strip(), sort, limit), False
        if name == "digimon_route":
            enc = _enc()
            found = find_species(enc, str(args.get("name", "")))
            if not found:
                return f"'{args.get('name')}' 를 도감에서 찾지 못했습니다 — digimon_search 로 이름을 확인하세요.", True
            try:
                limit = max(1, min(MAX_ROUTES, int(args.get("limit") or 5)))
            except (TypeError, ValueError):
                limit = 5
            r = _get(f"/api/evo/route?name={urllib.parse.quote(found)}&limit={limit}", ttl=60)
            routes = r.get("routes") or []
            if not routes:
                return f"{found} 까지의 루트를 찾지 못했습니다 (봇 진화 기록이 아직 없음).", False
            body = "\n".join(f"{i + 1}. {x.get('text') or ' → '.join(x.get('names') or [])}" for i, x in enumerate(routes))
            return f"# {found} 진화 루트 ({len(routes)}개, 짧은 순)\n{body}\n{PUBLIC_URL}/?q={urllib.parse.quote(found)}", False
        return f"알 수 없는 도구: {name}", True
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return f"디지몬 도감 서버에 연결하지 못했습니다 ({e}). 잠시 후 다시 시도하세요.", True
    except Exception as e:  # noqa: BLE001
        return f"디지몬 도구 실행 실패: {e}", True


TOOL_NAMES = frozenset(t["name"] for t in TOOLS)
