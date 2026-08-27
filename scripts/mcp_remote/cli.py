"""python -m scripts.mcp_remote client create|list|delete — 수동 클라이언트 발급.

동적 등록을 끈 채로 커넥터를 붙일 때 쓴다. 발급된 client_id/secret 을 claude.ai
커넥터 추가 화면의 [Advanced settings] 에 넣는다. secret 은 이때 한 번만 보인다.
"""
from __future__ import annotations

import sys

from scripts.mcp_remote.oauth_store import get_store

USAGE = "사용법: python -m scripts.mcp_remote client create <이름> --redirect-uri <URL> [...] | list | delete <client_id>"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or args[0] != "client":
        print(USAGE)
        return 1
    st = get_store()
    action = args[1]

    if action == "list":
        rows = st.list_clients()
        if not rows:
            print("등록된 클라이언트 없음")
            return 0
        for r in rows:
            print(f"{r['client_id']}  {r['name']:<20} [{r['source']}]  {r['created_at']}")
            for u in r["redirect_uris"]:
                print(f"    ↳ {u}")
        return 0

    if action == "create":
        rest = args[2:]
        name = rest[0] if rest and not rest[0].startswith("--") else "manual"
        uris = [rest[i + 1] for i, a in enumerate(rest) if a == "--redirect-uri" and i + 1 < len(rest)]
        if not uris:
            print("--redirect-uri 가 최소 하나 필요합니다")
            print(USAGE)
            return 1
        cid, secret = st.create_client(name, uris, source="manual")
        print(f"client_id     : {cid}")
        print(f"client_secret : {secret}   ← 지금만 보입니다. 저장해두세요")
        for u in uris:
            print(f"redirect_uri  : {u}")
        return 0

    if action == "delete":
        if len(args) < 3:
            print(USAGE)
            return 1
        ok = st.delete_client(args[2])
        print("삭제됨 (관련 토큰도 폐기)" if ok else "그런 client_id 없음")
        return 0 if ok else 1

    print(USAGE)
    return 1


if __name__ == "__main__":
    sys.exit(main())
