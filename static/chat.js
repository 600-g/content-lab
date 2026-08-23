/**
 * aiskillbox 자가 운영 채팅 패널 (Opus 5 · SSE 실시간 스트리밍).
 *
 * - 우측 플로팅 FAB → 사이드 패널 토글.
 * - PIN 0910 1회 입력 → 세션 토큰 localStorage 보관 (30분, 만료는 서버가 거부로 통보).
 * - mutating 도구는 백엔드가 토큰 검증. 토큰 만료 시 reply 에 need_pin 안내.
 */
(function () {
  const $ = (sel) => document.querySelector(sel);
  const fab = $("#chat-fab");
  const panel = $("#chat-panel");
  const backdrop = $("#chat-backdrop");
  const closeBtn = $("#chat-close");
  const closeBottom = $("#chat-close-bottom");
  const form = $("#chat-form");
  const input = $("#chat-input");
  const sendBtn = $("#chat-send");
  const pinBtn = $("#chat-pin-btn");
  const logEl = $("#chat-log");
  const stateText = $("#chat-state-text");
  const stateDot = $("#chat-state-dot");
  const sessionTag = $("#chat-session-tag");
  const stopBtn = $("#chat-stop");
  const newBtn = $("#chat-new");

  if (!fab || !panel) return;

  const IS_NARROW = () => window.innerWidth <= 640;

  function openPanel(focusInput) {
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    if (backdrop) {
      backdrop.classList.add("open");
      backdrop.setAttribute("aria-hidden", "false");
    }
    // 배경 스크롤 락 (모바일 바텀시트 뒤 본문 스크롤/PTR 방지)
    document.body.classList.add("chat-open");
    document.body.style.overflow = "hidden";
    // 열림 상태에서 FAB 를 '닫기' 토글로 변환 (데스크톱 fallback — 모바일에선 CSS 로 숨김).
    fab.classList.add("is-close");
    fab.textContent = "✕";
    fab.setAttribute("aria-label", "채팅 닫기");
    fab.title = "채팅 닫기";
    loadStatus();
    loadHistory();
    logEl.scrollTop = logEl.scrollHeight;
    // 모바일: 자동 포커스 시 키보드가 바로 올라와 로그를 가림 — 명시 요청일 때만 포커스.
    if (focusInput || !IS_NARROW()) input.focus();
  }

  let _historyLoaded = false; // 세션 동안 1회만 렌더 (중복 방지)
  async function loadHistory() {
    if (_historyLoaded) return;
    const token = getToken();
    if (!token) {
      // 첫 방문 — PIN 안내 배너 1회만
      if (!logEl.querySelector(".chat-history-hint")) {
        const hint = document.createElement("div");
        hint.className = "chat-msg system chat-history-hint";
        hint.textContent = "🔐 [PIN 입력] 후 이전 대화를 열람할 수 있어요.";
        logEl.appendChild(hint);
      }
      return;
    }
    try {
      const r = await fetch("/api/chat/history?limit=50", {
        headers: { "X-Session-Token": token },
      });
      if (r.status === 401) {
        // 토큰 만료
        setToken(null);
        return;
      }
      const j = await r.json();
      if (!j.ok || !Array.isArray(j.items) || !j.items.length) {
        _historyLoaded = true;
        return;
      }
      // 초기 안내 메시지 다음에 히스토리 삽입 — 이전 대화 표시
      const divider = document.createElement("div");
      divider.className = "chat-msg system";
      divider.textContent = "─── 이전 대화 (" + j.items.length + "건) ───";
      logEl.appendChild(divider);
      for (const it of j.items) {
        const role = it.role === "user" ? "user"
                   : it.role === "assistant" ? "assistant"
                   : "system";
        const text = typeof it.content === "string"
          ? it.content
          : JSON.stringify(it.content);
        appendMsg(role, text);
      }
      const end = document.createElement("div");
      end.className = "chat-msg system";
      end.textContent = "─── 여기부터 새 대화 ───";
      logEl.appendChild(end);
      logEl.scrollTop = logEl.scrollHeight;
      _historyLoaded = true;
    } catch (e) {
      // 조용히 실패 — 이전 대화 조회 실패로 신규 대화 자체는 막지 않음
    }
  }

  function closePanel() {
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
    if (backdrop) {
      backdrop.classList.remove("open");
      backdrop.setAttribute("aria-hidden", "true");
    }
    document.body.classList.remove("chat-open");
    document.body.style.overflow = "";
    input.blur();
    panel.style.setProperty("--kb", "0px");
    fab.classList.remove("is-close");
    fab.textContent = "💬";
    fab.setAttribute("aria-label", "자가 운영 채팅");
    fab.title = "채팅으로 운영·설정 편집";
  }

  // ── 키보드 가림 대응 — visualViewport 로 시트를 키보드 위로 올림 ──
  const vv = window.visualViewport;
  function adjustForKeyboard() {
    if (!vv) return;
    if (!panel.classList.contains("open")) return;
    const kb = Math.max(0, Math.round(window.innerHeight - vv.height - vv.offsetTop));
    panel.style.setProperty("--kb", kb + "px");
    // 키보드가 올라오면 최신 메시지가 보이게 로그를 바닥으로.
    if (kb > 0) requestAnimationFrame(() => { logEl.scrollTop = logEl.scrollHeight; });
  }
  if (vv) {
    vv.addEventListener("resize", adjustForKeyboard);
    vv.addEventListener("scroll", adjustForKeyboard);
  }
  input.addEventListener("focus", () => {
    setTimeout(adjustForKeyboard, 60);
    setTimeout(adjustForKeyboard, 350); // iOS 키보드 애니메이션 완료 후 재보정
  });
  input.addEventListener("blur", () => {
    setTimeout(() => { if (panel.classList.contains("open")) adjustForKeyboard(); }, 60);
  });

  // ── 스와이프 다운 닫기 (그립/헤더 잡고 아래로) ──
  (function initSwipeClose() {
    const zones = [panel.querySelector(".chat-grip"), panel.querySelector(".chat-header")];
    let startY = null;
    for (const z of zones) {
      if (!z) continue;
      z.addEventListener("touchstart", (ev) => {
        startY = ev.touches[0].clientY;
      }, { passive: true });
      z.addEventListener("touchmove", (ev) => {
        if (startY === null) return;
        if (ev.touches[0].clientY - startY > 70) {
          startY = null;
          closePanel();
        }
      }, { passive: true });
      z.addEventListener("touchend", () => { startY = null; }, { passive: true });
    }
  })();

  function toggle() {
    if (panel.classList.contains("open")) closePanel();
    else openPanel();
  }

  const STORE_KEY = "aiskillbox_chat_session";

  function getToken() {
    try {
      return localStorage.getItem(STORE_KEY) || null;
    } catch (_) {
      return null;
    }
  }

  function setToken(t) {
    try {
      if (t) localStorage.setItem(STORE_KEY, t);
      else localStorage.removeItem(STORE_KEY);
    } catch (_) {}
    refreshSessionTag();
  }

  function refreshSessionTag() {
    if (getToken()) {
      sessionTag.hidden = false;
    } else {
      sessionTag.hidden = true;
    }
  }

  function appendMsg(role, text, extra) {
    const div = document.createElement("div");
    div.className = "chat-msg " + role;
    div.textContent = text;
    if (extra && extra.tool_calls && extra.tool_calls.length) {
      const ul = document.createElement("ul");
      ul.className = "chat-tool-list";
      for (const tc of extra.tool_calls) {
        const li = document.createElement("li");
        li.textContent = (tc.ok ? "✅ " : "⚠️ ") + tc.name + " — " + (tc.summary || "");
        ul.appendChild(li);
      }
      div.appendChild(ul);
    }
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
    return div;
  }

  async function loadStatus() {
    try {
      const r = await fetch("/api/chat/status");
      const j = await r.json();
      if (!j.configured) {
        stateText.textContent = "ADMIN_PIN 미설정";
        stateDot.style.background = "#dc2626";
        return;
      }
      if (!j.key_present) {
        stateText.textContent = "LLM 키 없음 — ⚙️ 설정에서 GEMINI_API_KEY";
        stateDot.style.background = "#f59e0b";
        return;
      }
      stateText.textContent = { claude_cli: (j.model_label || "Opus 5") + " · 실시간", anthropic: "Opus 대기", gemini: "Gemini 2.5 대기", ollama: "로컬 폴백 대기" }[j.provider] || "대기";
      stateDot.style.background = "#3ddc85";
    } catch (e) {
      stateText.textContent = "상태 조회 실패";
      stateDot.style.background = "#dc2626";
    }
  }

  async function askPin() {
    // PIN 값을 UI 에 적지 않는다 — placeholder/힌트로도 노출 X (보안). 사용자가 본인이 알아야.
    const pin = window.prompt("PIN 입력");
    if (!pin) return false;
    const r = await fetch("/api/chat/pin", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pin }),
    });
    const j = await r.json();
    if (j.ok && j.session_token) {
      setToken(j.session_token);
      appendMsg("system", "🔓 세션 활성 — 쓰기 명령 가능 (30분 유지)");
      // 갓 인증됨 → 이전 대화 로드 시도
      _historyLoaded = false;
      loadHistory();
      // PIN 부족으로 막혔던 직전 요청 자동 재전송 — 사용자가 같은 말 반복 안 해도 됨.
      if (_pendingPinText) {
        const retry = _pendingPinText;
        _pendingPinText = "";
        appendMsg("system", "↻ 직전 요청을 다시 실행할게요.");
        sendMessage(retry);
      }
      return true;
    }
    appendMsg("system", "❌ PIN 인증 실패: " + (j.error || ""));
    return false;
  }

  let _sending = false; // 중복 전송 가드 (Enter 연타 / IME 이중 이벤트 / 전송 중 재클릭)
  let _pendingPinText = ""; // PIN 요구로 막힌 마지막 요청 — 인증 성공 시 자동 재전송
  let _abort = null;        // 진행 중 스트림 중단용

  // ── 대화 스레드 id ────────────────────────────────────────
  // 서버가 이 키로 claude CLI 세션(--resume)을 이어준다 → "아까 그거" 가 통한다.
  const CONV_KEY = "aiskillbox_chat_conv";
  function convId() {
    try {
      let c = localStorage.getItem(CONV_KEY);
      if (!c) {
        c = "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
        localStorage.setItem(CONV_KEY, c);
      }
      return c;
    } catch (_) {
      return "c-nostorage";
    }
  }

  async function newConversation() {
    const old = convId();
    try {
      await fetch("/api/chat/reset", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ conv_id: old }),
      });
    } catch (_) {}
    try { localStorage.removeItem(CONV_KEY); } catch (_) {}
    convId();
    appendMsg("system", "🆕 새 대화 — 이전 맥락을 비웠어요.");
  }

  function toolLine(tc) {
    const li = document.createElement("li");
    li.textContent = (tc.ok ? "✅ " : "⚠️ ") + tc.name + " — " + (tc.summary || "");
    return li;
  }

  /** 스트리밍 답변 말풍선 — 상태줄 / 본문 / 도구목록 3층. */
  function streamBubble() {
    const div = document.createElement("div");
    div.className = "chat-msg assistant";
    const status = document.createElement("div");
    status.className = "chat-stream-status";
    status.textContent = "● 연결 중…";
    const body = document.createElement("span");
    body.className = "chat-stream-body";
    const tools = document.createElement("ul");
    tools.className = "chat-tool-list";
    tools.hidden = true;
    div.append(status, body, tools);
    logEl.appendChild(div);
    logEl.scrollTop = logEl.scrollHeight;
    return { div, status, body, tools };
  }

  async function sendMessage(text) {
    if (_sending) return;
    if (!text || !text.trim()) return;
    _sending = true;
    appendMsg("user", text);
    input.value = "";
    sendBtn.disabled = true;
    if (stopBtn) stopBtn.hidden = false;

    const ui = streamBubble();
    let acc = "";          // 지금까지 흘러온 답변
    let toolCalls = [];
    let atBottom = true;

    const stick = () => {
      // 사용자가 위로 올려 읽는 중이면 강제 스크롤하지 않는다.
      if (atBottom) logEl.scrollTop = logEl.scrollHeight;
    };
    const onScroll = () => {
      atBottom = logEl.scrollHeight - logEl.scrollTop - logEl.clientHeight < 60;
    };
    logEl.addEventListener("scroll", onScroll, { passive: true });

    function handle(ev) {
      switch (ev.type) {
        case "status":
          ui.status.textContent = "● " + ev.text;
          break;
        case "delta":
          acc += ev.text;
          ui.body.textContent = acc;
          ui.status.textContent = "● 답하는 중…";
          stick();
          break;
        case "reset":       // 흘린 조각이 도구 라운드였다 — 취소
          acc = "";
          ui.body.textContent = "";
          break;
        case "tool":
          if (ev.phase === "start") {
            ui.status.textContent = "🔧 " + ev.name + " 실행 중…";
          } else {
            toolCalls.push(ev);
            ui.tools.hidden = false;
            ui.tools.appendChild(toolLine(ev));
            stick();
          }
          break;
        case "done":
          ui.status.remove();
          ui.body.textContent = ev.reply || acc || "(빈 응답)";
          if (ev.tool_calls && ev.tool_calls.length && !toolCalls.length) {
            ui.tools.hidden = false;
            for (const tc of ev.tool_calls) ui.tools.appendChild(toolLine(tc));
          }
          if ((ev.tool_calls || toolCalls).some((tc) => !tc.ok && /세션|PIN/.test(tc.summary || ""))) {
            _pendingPinText = text;
            appendMsg("system", "🔐 PIN 1회 입력이 필요해요. [PIN 입력] 버튼을 눌러주세요. 인증되면 방금 요청을 자동으로 다시 실행해요.");
          }
          stick();
          break;
        case "error":
          ui.status.remove();
          ui.body.textContent = "❌ " + (ev.message || "응답 실패") + (ev.hint ? "\n" + ev.hint : "");
          break;
        default:
          break;      // ping 등
      }
    }

    try {
      _abort = new AbortController();
      const r = await fetch("/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, session_token: getToken(), conv_id: convId() }),
        signal: _abort.signal,
      });
      if (!r.ok || !r.body) throw new Error("stream unavailable (" + r.status + ")");

      const reader = r.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      for (;;) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let i;
        while ((i = buf.indexOf("\n\n")) >= 0) {
          const chunk = buf.slice(0, i);
          buf = buf.slice(i + 2);
          if (!chunk.startsWith("data:")) continue;   // ": open" 주석 무시
          try { handle(JSON.parse(chunk.slice(5).trim())); } catch (_) {}
        }
      }
      if (ui.status.isConnected) {
        // done 없이 끊김 — 흘러온 텍스트라도 살린다
        ui.status.remove();
        if (!acc) ui.body.textContent = "❌ 응답이 중간에 끊겼어요. 다시 시도해주세요.";
      }
    } catch (e) {
      if (e && e.name === "AbortError") {
        ui.status.remove();
        ui.body.textContent = (acc ? acc + "\n\n" : "") + "■ 중지했어요.";
      } else {
        // 스트림 미지원/실패 → 기존 단발 API 로 폴백 (구버전 서버 호환)
        try {
          const r2 = await fetch("/api/chat/message", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text, session_token: getToken(), conv_id: convId() }),
          });
          const j = await r2.json();
          handle(j.ok
            ? { type: "done", reply: j.reply, tool_calls: j.tool_calls || [] }
            : { type: "error", message: j.error, hint: j.hint });
        } catch (e2) {
          ui.status.remove();
          ui.body.textContent = "❌ 네트워크 오류: " + e2.message;
        }
      }
    } finally {
      logEl.removeEventListener("scroll", onScroll);
      _abort = null;
      _sending = false;
      sendBtn.disabled = false;
      if (stopBtn) stopBtn.hidden = true;
      if (!IS_NARROW()) input.focus();
    }
  }

  // 채팅 닫는 방법 4가지 — 어떤 환경에서도 한 가지는 작동.
  fab.addEventListener("click", toggle);           // 1) FAB (열림 상태에선 ✕ 로 변신)
  closeBtn.addEventListener("click", closePanel);  // 2) 헤더 우측 [닫기 ✕] 버튼
  if (closeBottom) closeBottom.addEventListener("click", closePanel); // 3) 하단 [나가기] 버튼
  if (backdrop) backdrop.addEventListener("click", closePanel);       // 4) 백드롭 클릭
  document.addEventListener("keydown", (ev) => {                       // 5) ESC 키
    if (ev.key === "Escape" && panel.classList.contains("open")) {
      ev.preventDefault();
      closePanel();
    }
  });
  pinBtn.addEventListener("click", askPin);
  if (stopBtn) stopBtn.addEventListener("click", () => { if (_abort) _abort.abort(); });
  if (newBtn) newBtn.addEventListener("click", newConversation);
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    sendMessage(input.value);
  });
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      // 한글 IME 조합 중 Enter 는 keydown 이 2번 발생 (조합 커밋용 + 실제 입력).
      // 조합 중 이벤트(isComposing / keyCode 229)는 무시 — "엔터 두 번 눌림" 재발 방지.
      if (ev.isComposing || ev.keyCode === 229) return;
      ev.preventDefault();
      sendMessage(input.value);
    }
  });

  refreshSessionTag();

  // 실패 알림 딥링크 — /?diag=<job_id> 진입 시 채팅을 열고 진단 문구 프리필.
  try {
    const params = new URLSearchParams(location.search);
    const diag = params.get("diag");
    if (diag && /^[a-z0-9]{1,32}$/i.test(diag)) {
      openPanel(true);
      input.value = "잡 " + diag + " 실패했어. 원인 진단하고, 코드 수정이 필요하면 escalate_fix 로 고쳐줘.";
      appendMsg("system", "🔔 실패 알림에서 진입 — [전송] 을 누르면 진단을 시작해요. 수정 위임에는 PIN 1회 인증이 필요해요.");
      window.history.replaceState(null, "", location.pathname);
    }
  } catch (_) {}
})();
