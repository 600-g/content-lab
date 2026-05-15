#!/bin/bash
# aiskillbox Flask 서버 시작 래퍼.
# venv 활성 + .env 로드 + app.py 실행.

set -e
cd /Users/600mac/Developer/my-company/content-lab

if [ ! -d venv ]; then
  echo "[aiskillbox] venv 없음 → 자동 생성"
  /opt/homebrew/bin/python3 -m venv venv
  ./venv/bin/pip install -q --upgrade pip
  ./venv/bin/pip install -q -r requirements.txt
  ./venv/bin/playwright install chromium >/dev/null 2>&1 || true
fi

# .env 로드 (있을 때만)
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

export PYTHONUNBUFFERED=1
exec ./venv/bin/python app.py
