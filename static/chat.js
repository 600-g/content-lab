/**
 * aiskillbox 자가 운영 채팅 패널 (Opus 4.8).
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

  if (!fab || !panel) return;

  function openPanel() {
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
    if (backdrop) {
      backdrop.classList.add("open");
      backdrop.setAttribute("aria-hidden", "false");
    }
    // 열림 상태에서 FAB 를 '닫기' 토글로 변환 (닫기 버튼이 안 보이거나 작아서 못 찾는 fallback).
    fab.classList.add("is-close");
    fab.textContent = "✕";
    fab.setAttribute("aria-label", "채팅 닫기");
    fab.title = "채팅 닫기";
    loadStatus();
    input.focus();
  }

  function closePanel() {
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
    if (backdrop) {
      backdrop.classList.remove("open");
      backdrop.setAttribute("aria-hidden", "true");
    }
    fab.classList.remove("is-close");
    fab.textContent = "💬";
    fab.setAttribute("aria-label", "자가 운영 채팅");
    fab.title = "채팅으로 운영·설정 편집";
  }

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
        stateText.textContent = "Anthropic 키 없음 — .env 설정";
        stateDot.style.background = "#f59e0b";
        return;
      }
      stateText.textContent = "Opus 4.8 대기";
      stateDot.style.background = "#22c55e";
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
      return true;
    }
    appendMsg("system", "❌ PIN 인증 실패: " + (j.error || ""));
    return false;
  }

  async function sendMessage(text) {
    if (!text || !text.trim()) return;
    appendMsg("user", text);
    input.value = "";
    sendBtn.disabled = true;
    const placeholder = appendMsg("assistant", "…");
    try {
      const token = getToken();
      const r = await fetch("/api/chat/message", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, session_token: token }),
      });
      const j = await r.json();
      if (!j.ok) {
        placeholder.textContent = "❌ " + (j.error || "응답 실패") + (j.hint ? "\n" + j.hint : "");
      } else {
        placeholder.textContent = j.reply || "(빈 응답)";
        if (j.tool_calls && j.tool_calls.length) {
          const ul = document.createElement("ul");
          ul.className = "chat-tool-list";
          for (const tc of j.tool_calls) {
            const li = document.createElement("li");
            li.textContent = (tc.ok ? "✅ " : "⚠️ ") + tc.name + " — " + (tc.summary || "");
            ul.appendChild(li);
          }
          placeholder.appendChild(ul);
        }
        // 토큰 만료를 모델이 알린 경우 — 사용자 안내.
        const needPin = (j.tool_calls || []).some(
          (tc) => !tc.ok && /세션|PIN/.test(tc.summary || "")
        );
        if (needPin) {
          appendMsg("system", "🔐 PIN 1회 입력이 필요해요. [PIN 입력] 버튼을 눌러주세요.");
        }
      }
    } catch (e) {
      placeholder.textContent = "❌ 네트워크 오류: " + e.message;
    } finally {
      sendBtn.disabled = false;
      input.focus();
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
  form.addEventListener("submit", (ev) => {
    ev.preventDefault();
    sendMessage(input.value);
  });
  input.addEventListener("keydown", (ev) => {
    if (ev.key === "Enter" && !ev.shiftKey) {
      ev.preventDefault();
      sendMessage(input.value);
    }
  });

  refreshSessionTag();
})();
