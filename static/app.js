// aiskillbox 클라이언트 v4.3
// - 순차 잡 큐: 제출 즉시 입력칸 비움 + 다중 잡 추적
// - Web Push: 백그라운드에서도 완료 알림
// - 설정 창: PIN 보호 API 키 편집

'use strict';

// ── DOM ────────────────────────────────────────────────
const form = document.getElementById('collect-form');
const urlInput = document.getElementById('url');
const submitBtn = document.getElementById('submit-btn');
const jobList = document.getElementById('job-list');
const jobEmpty = document.getElementById('job-empty');
const recentList = document.getElementById('recent-list');
const recentCount = document.getElementById('recent-count');
const recentEmpty = document.getElementById('recent-empty');

const drawer = document.getElementById('drawer');
const backdrop = document.getElementById('drawer-backdrop');
const drawerToggle = document.getElementById('drawer-toggle');
const drawerClose = document.getElementById('drawer-close');

const IS_MOBILE = /iPad|iPhone|iPod|Android/i.test(navigator.userAgent)
  || (navigator.maxTouchPoints > 1 && /Mac/i.test(navigator.platform));

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[c]);
}

// ── 서비스워커 + Web Push ───────────────────────────────
let _swReg = null;

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const raw = atob(base64);
  const out = new Uint8Array(raw.length);
  for (let i = 0; i < raw.length; i++) out[i] = raw.charCodeAt(i);
  return out;
}

async function registerServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  try {
    _swReg = await navigator.serviceWorker.register('/sw.js', {
      scope: '/', updateViaCache: 'none',
    });
  } catch (e) { console.warn('[aiskillbox] SW 등록 실패', e); }
}

// interactive=true 면 사용자 제스처 — 권한 팝업 허용 (iOS 필수)
async function setupPush(interactive) {
  if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
    return 'unsupported';
  }
  const reg = _swReg || await navigator.serviceWorker.ready;
  if (!reg) return 'no-sw';
  let perm = Notification.permission;
  if (perm === 'default') {
    if (!interactive) return 'default';
    try { perm = await Notification.requestPermission(); } catch { return 'error'; }
  }
  if (perm !== 'granted') return perm;
  try {
    let sub = await reg.pushManager.getSubscription();
    let isNew = false;
    if (!sub) {
      const r = await fetch('/api/push/vapid');
      const d = await r.json();
      if (!d.ok || !d.public_key) return 'no-vapid';
      sub = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(d.public_key),
      });
      isNew = true;
    }
    // 새 구독이거나 사용자가 명시적으로 켤 때만 서버 전송 (제출마다 중복 POST 방지)
    if (isNew || interactive) {
      await fetch('/api/push/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sub),
      });
    }
    return 'granted';
  } catch (e) {
    console.warn('[aiskillbox] 푸시 구독 실패', e);
    return 'error';
  }
}

function pushStatusLabel(state) {
  return ({
    granted: '✅ 켜짐 — 백그라운드 알림 동작',
    denied: '❌ 차단됨 — 브라우저/OS 알림 설정에서 허용 필요',
    default: '🔔 알림 켜기를 눌러주세요',
    unsupported: '⚠️ 이 브라우저는 푸시 미지원',
    'no-vapid': '⚠️ 서버 푸시 키 미설정',
    'no-sw': '⚠️ 서비스워커 준비 안 됨',
    error: '⚠️ 구독 실패 — 다시 시도',
  }[state] || state);
}

// ── 포그라운드 피드백 (앱이 열려 있을 때 즉각 반응) ──────
function foregroundFeedback() {
  try { navigator.vibrate?.([120, 60, 120]); } catch {}
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.frequency.value = 880;
    gain.gain.setValueAtTime(0.0001, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.15, ctx.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.4);
    osc.start(); osc.stop(ctx.currentTime + 0.4);
  } catch {}
}

// ── 드로어 ──────────────────────────────────────────────
function openDrawer() {
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
  backdrop.classList.remove('hidden');
  document.body.classList.add('drawer-open');
  document.body.style.overflow = 'hidden';
  loadHealth();
  loadRecent();
}
function closeDrawer() {
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
  backdrop.classList.add('hidden');
  document.body.classList.remove('drawer-open');
  document.body.style.overflow = '';
}
drawerToggle.addEventListener('click', () => {
  drawer.classList.contains('open') ? closeDrawer() : openDrawer();
});
drawerClose.addEventListener('click', closeDrawer);
backdrop.addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && drawer.classList.contains('open')) closeDrawer();
});

// ── Notion 딥링크 (모바일이면 notion:// 시도 + 폴백) ────
function attachNotionHandlers() {
  document.querySelectorAll('a[data-app][data-web]').forEach(a => {
    if (a.dataset.bound) return;
    a.dataset.bound = '1';
    a.addEventListener('click', (e) => {
      const app = a.dataset.app, web = a.dataset.web;
      if (!IS_MOBILE || !app) return;
      e.preventDefault();
      const t = setTimeout(() => { if (!document.hidden) window.location.href = web; }, 900);
      const onVis = () => {
        if (document.hidden) { clearTimeout(t); document.removeEventListener('visibilitychange', onVis); }
      };
      document.addEventListener('visibilitychange', onVis);
      window.location.href = app;
    });
  });
}

// ── 잡 큐 ───────────────────────────────────────────────
let pollTimer = null;
let pollGen = 0;                              // 폴링 루프 세대 — 재호출 시 이전 루프 무효화
const _jobStates = {};                       // id → 직전 status (전이 감지용)
const _dismissed = new Set(                   // 사용자가 닫은 잡 카드
  JSON.parse(sessionStorage.getItem('aiskillbox.dismissed') || '[]'));

function _saveDismissed() {
  try { sessionStorage.setItem('aiskillbox.dismissed', JSON.stringify([..._dismissed])); } catch {}
}

function humanStage(s) {
  return ({
    queued: '큐 대기 중', scraping: '웹 스크래핑 중', running: '처리 중',
    completed: '완료', failed: '실패', interrupted: '중단됨',
  }[s] || s);
}

function jobBadge(item) {
  const r = item.result || {};
  if (item.status === 'queued') {
    return { cls: 'badge', text: item.queue_pos ? `⏳ 대기 ${item.queue_pos}번째` : '⏳ 대기 중' };
  }
  if (item.status === 'running') return { cls: 'badge warn', text: '🔄 ' + humanStage(item.stage) };
  if (item.status === 'interrupted') return { cls: 'badge failed', text: '⏸ 중단됨' };
  if (item.status === 'failed') return { cls: 'badge failed', text: '❌ 실패' };
  // completed
  if (r.partial_ok) return { cls: 'badge warn', text: '⚠️ 부분 성공' };
  if (r.skipped) return { cls: 'badge', text: '⏭ 이미 등록됨' };
  if (r.skill && r.skill.merged) return { cls: 'badge merged', text: '🔀 합병됨' };
  return { cls: 'badge success', text: '✅ 완료' };
}

function isTerminal(status) {
  return status === 'completed' || status === 'failed' || status === 'interrupted';
}

function renderJobCard(item) {
  const b = jobBadge(item);
  const r = item.result || {};
  const skill = r.skill || {};
  const closable = isTerminal(item.status);
  const title = skill.title || skill.name || '';

  let detail = '';
  if (item.status === 'running' || item.status === 'queued') {
    detail = `<span class="job-elapsed">${item.elapsed}초 경과</span>`;
  } else if (item.status === 'completed' && !r.skipped) {
    const web = r.notion_web_url || '';
    const app = web ? web.replace('https://', 'notion://') : '';
    const links = web
      ? `<a class="job-link" data-app="${escapeHtml(app)}" data-web="${escapeHtml(web)}"
            href="${escapeHtml(web)}" target="_blank" rel="noopener">📝 Notion</a>` : '';
    detail = `${title ? `<span class="job-title">${escapeHtml(title)}</span>` : ''}
              ${r.message_ko ? `<span class="job-note">${escapeHtml(r.message_ko)}</span>` : ''}
              ${links}`;
  } else if (item.status === 'completed' && r.skipped) {
    detail = `<span class="job-note">${escapeHtml(r.message_ko || '이미 등록된 스킬')}</span>`;
  } else {
    // failed / interrupted / partial
    const err = r.error_ko || item.error || '오류가 발생했어요';
    const hint = r.hint ? `<span class="job-hint">💡 ${escapeHtml(r.hint)}</span>` : '';
    detail = `<span class="job-err">🚨 ${escapeHtml(err)}</span>${hint}
              <button class="job-retry" data-url="${escapeHtml(item.url)}" type="button">🔄 다시 시도</button>`;
  }

  const id = escapeHtml(item.id);
  return `<li class="job-card" data-id="${id}">
    <div class="job-top">
      <span class="${b.cls}">${b.text}</span>
      ${closable ? `<button class="job-dismiss" data-id="${id}" aria-label="닫기">✕</button>` : ''}
    </div>
    <div class="job-url">${escapeHtml(item.url)}</div>
    <div class="job-detail">${detail}</div>
  </li>`;
}

function renderJobs(items) {
  const visible = items.filter(i => !_dismissed.has(i.id));
  if (visible.length === 0) {
    jobList.innerHTML = '';
    jobEmpty.classList.remove('hidden');
    return;
  }
  jobEmpty.classList.add('hidden');
  jobList.innerHTML = visible.map(renderJobCard).join('');
  attachNotionHandlers();
  jobList.querySelectorAll('.job-dismiss').forEach(btn => {
    btn.addEventListener('click', () => {
      _dismissed.add(btn.dataset.id);
      _saveDismissed();
      btn.closest('.job-card')?.remove();
      if (!jobList.children.length) jobEmpty.classList.remove('hidden');
    });
  });
  jobList.querySelectorAll('.job-retry').forEach(btn => {
    btn.addEventListener('click', () => submitUrl(btn.dataset.url));
  });
}

// 활성 잡이 남았는지 boolean 반환 — startPolling 루프가 지속 여부 판단
async function pollJobs() {
  try {
    const resp = await fetch('/api/jobs/active');
    const d = await resp.json();
    if (!d.ok) return false;
    const items = d.items || [];

    // 완료 전이 감지 → 포그라운드 피드백 + 최근 목록 갱신
    let justFinished = false;
    for (const it of items) {
      const prev = _jobStates[it.id];
      if (prev && !isTerminal(prev) && isTerminal(it.status)) justFinished = true;
      _jobStates[it.id] = it.status;
    }
    renderJobs(items);
    if (justFinished) {
      foregroundFeedback();
      loadRecent();
    }
    return (d.active_count || 0) > 0;
  } catch (e) {
    console.warn(e);
    return true;  // 일시적 네트워크 오류 — 계속 폴 (성공 시 active 0 이면 자동 종료)
  }
}

// 세대(gen) 카운터로 중복/유실 방지 — startPolling 재호출 시 이전 루프는 스스로 종료
function startPolling() {
  const gen = ++pollGen;
  (async function loop() {
    if (gen !== pollGen) return;          // 더 최신 startPolling 에 밀림
    const more = await pollJobs();
    if (gen !== pollGen) return;          // await 중 밀림
    if (more) pollTimer = setTimeout(loop, 2000);
    else pollTimer = null;
  })();
}

async function submitUrl(url) {
  url = (url || '').trim();
  if (!url) return;
  try {
    const resp = await fetch('/api/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error || '요청 실패');
    // 새 잡이 보이도록 닫음 목록에서 혹시 같은 id 있으면 제거 (id 는 신규라 무관)
    startPolling();
  } catch (err) {
    alert('요청 실패: ' + err.message);
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = urlInput.value.trim();
  if (!url) return;

  // 핵심: 제출 즉시 입력칸 비우기 — 기다리지 않고 다음 링크 입력 가능
  urlInput.value = '';
  urlInput.blur();

  // 잠깐 버튼 피드백 (비활성화는 아주 짧게 — 연속 제출 막지 않음)
  const label = submitBtn.querySelector('.btn-label');
  const orig = label.textContent;
  label.textContent = '큐에 추가됨 ✓';
  setTimeout(() => { label.textContent = orig; }, 1100);

  // 권한 미결정일 때만 — 첫 제출에서 1회 권한 요청 (iOS 제스처 정책)
  // 이미 granted/denied 면 제출마다 재호출하지 않음
  if ('Notification' in window && Notification.permission === 'default') {
    setupPush(true).then(updateNotifRow);
  }

  await submitUrl(url);
});

// ── 시스템 상태 (드로어) ────────────────────────────────
async function loadHealth() {
  try {
    const d = await (await fetch('/healthz')).json();
    const set = (id, ok) => {
      const el = document.getElementById(id);
      if (el) { el.textContent = ok ? '✅' : '❌'; el.className = 'dot ' + (ok ? 'ok' : 'bad'); }
    };
    set('health-gemini', d.gemini_configured);
    set('health-notion', d.notion_configured);
    const jobsEl = document.getElementById('health-jobs');
    if (jobsEl) jobsEl.textContent = `${d.active_jobs || 0} / 대기 ${d.queued_jobs || 0}`;
    const recEl = document.getElementById('health-recent');
    if (recEl) recEl.textContent = (d.recent_count || 0) + '건';
    const pushEl = document.getElementById('health-push');
    if (pushEl) pushEl.textContent = d.push_configured
      ? `구독 ${d.push_subscriptions || 0}` : '미설정';
  } catch {}
}
document.getElementById('health-refresh')?.addEventListener('click', loadHealth);

// ── 최근 수집 (드로어) ──────────────────────────────────
const recentSearchInput = document.getElementById('recent-search');
const gradeFiltersEl = document.getElementById('grade-filters');
let _recentCache = [];
let _filterGrade = 'all';
let _searchQuery = '';

async function loadRecent() {
  try {
    const d = await (await fetch('/api/recent')).json();
    _recentCache = d.items || [];
    _renderRecentList();
  } catch {}
}

function _filterRecent(items) {
  const q = _searchQuery.trim().toLowerCase();
  return items.filter(it => {
    if (_filterGrade !== 'all' && (it.grade || '') !== _filterGrade) return false;
    if (!q) return true;
    const hay = [it.skill_title, it.skill_name, it.category].filter(Boolean).join(' ').toLowerCase();
    return hay.includes(q);
  });
}

if (recentSearchInput) {
  recentSearchInput.addEventListener('input', (e) => {
    _searchQuery = e.target.value; _renderRecentList();
  });
}
if (gradeFiltersEl) {
  gradeFiltersEl.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-filter]');
    if (!btn) return;
    _filterGrade = btn.dataset.filter;
    gradeFiltersEl.querySelectorAll('button').forEach(b => b.classList.toggle('active', b === btn));
    _renderRecentList();
  });
}

function _renderRecentList() {
  const filtered = _filterRecent(_recentCache);
  if (recentCount) {
    recentCount.textContent = _recentCache.length > 0
      ? `${filtered.length}/${_recentCache.length}건` : '';
  }
  if (filtered.length === 0) {
    recentList.innerHTML = '';
    recentEmpty?.classList.remove('hidden');
    return;
  }
  recentEmpty?.classList.add('hidden');
  recentList.innerHTML = filtered.slice(0, 30).map(_renderRecentItem).join('');
  attachNotionHandlers();
}

function _renderRecentItem(item) {
  const grade = item.grade || 'C';
  const title = item.skill_title || item.skill_name || '(제목없음)';
  const mergePill = item.source_count > 1
    ? `<span class="merge-pill">🔀 ${item.source_count}</span>` : '';
  const cat = item.category ? `${item.category} · ` : '';
  const notionApp = item.notion_app_url || '';
  const notionWeb = item.notion_web_url || '';
  const notionLink = notionWeb
    ? `<a class="notion notion-deeplink" data-app="${escapeHtml(notionApp)}" data-web="${escapeHtml(notionWeb)}" href="${escapeHtml(notionWeb)}" target="_blank" rel="noopener">📝 Notion</a>`
    : '';
  const originLink = item.url
    ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noopener">🔗 원본</a>` : '';
  return `<li>
    <div class="row1">
      <span class="grade grade-${grade}">${grade}</span>
      <span class="title">${escapeHtml(title)}</span>
      ${mergePill}
    </div>
    <div class="meta">${escapeHtml(cat)}${escapeHtml(item.ts || '')}</div>
    <div class="actions">${notionLink}${originLink}</div>
  </li>`;
}

// ── 설정 창 (PIN 보호) ──────────────────────────────────
const settingsModal = document.getElementById('settings-modal');
const settingsBackdrop = document.getElementById('settings-backdrop');
const settingsToggle = document.getElementById('settings-toggle');
const settingsClose = document.getElementById('settings-close');
const pinView = document.getElementById('settings-pin-view');
const fieldsView = document.getElementById('settings-fields-view');
const pinInput = document.getElementById('settings-pin-input');
const pinSubmit = document.getElementById('settings-pin-submit');
const pinError = document.getElementById('settings-pin-error');
const fieldsBox = document.getElementById('settings-fields');
const settingsSave = document.getElementById('settings-save');
const settingsMsg = document.getElementById('settings-msg');
const notifBtn = document.getElementById('notif-toggle');
const notifStatus = document.getElementById('notif-status');

let _pin = '';

function openSettings() {
  settingsModal.classList.remove('hidden');
  settingsBackdrop.classList.remove('hidden');
  document.body.style.overflow = 'hidden';
  pinView.classList.remove('hidden');
  fieldsView.classList.add('hidden');
  pinError.textContent = '';
  pinInput.value = '';
  settingsMsg.textContent = '';
  updateNotifRow();
  setTimeout(() => pinInput.focus(), 100);
}
function closeSettings() {
  settingsModal.classList.add('hidden');
  settingsBackdrop.classList.add('hidden');
  document.body.style.overflow = '';
  _pin = '';
}
settingsToggle?.addEventListener('click', openSettings);
settingsClose?.addEventListener('click', closeSettings);
settingsBackdrop?.addEventListener('click', closeSettings);

function renderSettingsFields(rows) {
  fieldsBox.innerHTML = rows.map(r => {
    const ph = r.kind === 'text'
      ? '' : (r.is_set ? `현재: ${escapeHtml(r.preview)} (바꿀 때만 입력)` : '미설정 — 입력');
    const val = r.kind === 'text' && r.is_set ? `value="${escapeHtml(r.preview)}"` : '';
    const type = r.kind === 'secret' ? 'password' : 'text';
    return `<label class="set-field">
      <span class="set-label">${escapeHtml(r.label)}
        ${r.is_set ? '<span class="set-on">●</span>' : '<span class="set-off">○</span>'}</span>
      <input type="${type}" data-key="${r.key}" data-kind="${r.kind}"
             placeholder="${escapeHtml(ph)}" ${val}
             autocomplete="off" autocapitalize="off" spellcheck="false">
      <span class="set-hint">${escapeHtml(r.hint)}</span>
    </label>`;
  }).join('');
}

async function doPinAuth() {
  const pin = pinInput.value.trim();
  if (!pin) { pinError.textContent = 'PIN 을 입력하세요'; return; }
  pinSubmit.disabled = true;
  try {
    const resp = await fetch('/api/settings/auth', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Admin-Pin': pin },
      body: '{}',
    });
    const d = await resp.json();
    if (!d.ok) { pinError.textContent = d.error || '인증 실패'; return; }
    _pin = pin;
    pinView.classList.add('hidden');
    fieldsView.classList.remove('hidden');
    renderSettingsFields(d.rows || []);
  } catch (e) {
    pinError.textContent = '네트워크 오류';
  } finally {
    pinSubmit.disabled = false;
  }
}
pinSubmit?.addEventListener('click', doPinAuth);
pinInput?.addEventListener('keydown', e => { if (e.key === 'Enter') doPinAuth(); });

async function doSettingsSave() {
  const updates = {};
  let newPin = '';
  fieldsBox.querySelectorAll('input[data-key]').forEach(inp => {
    const v = inp.value.trim();
    if (!v) return;
    updates[inp.dataset.key] = v;
    if (inp.dataset.key === 'ADMIN_PIN') newPin = v;
  });
  if (Object.keys(updates).length === 0) {
    settingsMsg.textContent = '변경할 항목이 없어요';
    return;
  }
  settingsSave.disabled = true;
  settingsMsg.textContent = '저장 중...';
  try {
    const resp = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Admin-Pin': _pin },
      body: JSON.stringify({ updates }),
    });
    const d = await resp.json();
    if (!d.ok) { settingsMsg.textContent = d.error || '저장 실패'; return; }
    if (newPin) _pin = newPin;   // PIN 바꿨으면 세션 PIN 갱신
    settingsMsg.textContent = `✅ 저장됨: ${(d.applied || []).join(', ')}`;
    renderSettingsFields(d.rows || []);
    loadHealth();
  } catch (e) {
    settingsMsg.textContent = '네트워크 오류';
  } finally {
    settingsSave.disabled = false;
  }
}
settingsSave?.addEventListener('click', doSettingsSave);

// 알림 행 — 설정 창 안에 같이 노출
async function updateNotifRow() {
  if (!notifStatus) return;
  let state = 'unsupported';
  if ('Notification' in window) {
    state = Notification.permission;
    if (state === 'granted') {
      // 구독이 실제로 살아있는지 가볍게 확인
      try {
        const reg = _swReg || await navigator.serviceWorker.ready;
        const sub = reg && await reg.pushManager.getSubscription();
        state = sub ? 'granted' : 'default';
      } catch {}
    }
  }
  notifStatus.textContent = pushStatusLabel(state);
  if (notifBtn) notifBtn.classList.toggle('hidden', state === 'granted' || state === 'unsupported');
}
notifBtn?.addEventListener('click', async () => {
  notifBtn.disabled = true;
  const state = await setupPush(true);
  notifBtn.disabled = false;
  await updateNotifRow();
  if (state !== 'granted') {
    notifStatus.textContent = pushStatusLabel(state);
  }
});

// ── Pull-to-Refresh ─────────────────────────────────────
(function initPullToRefresh() {
  let startY = 0, pulling = false, triggered = false;
  const THRESHOLD = 80;
  const indicator = document.createElement('div');
  indicator.id = 'ptr-indicator';
  indicator.innerHTML = '<span class="ptr-icon">⟳</span> <span class="ptr-text">당겨서 새로고침</span>';
  document.body.appendChild(indicator);

  document.addEventListener('touchstart', (e) => {
    if (document.body.classList.contains('drawer-open')) return;
    if (!settingsModal.classList.contains('hidden')) return;
    if (window.scrollY > 4) return;
    startY = e.touches[0].clientY; pulling = true; triggered = false;
  }, { passive: true });

  document.addEventListener('touchmove', (e) => {
    if (!pulling) return;
    const dy = e.touches[0].clientY - startY;
    if (dy <= 0) { indicator.style.transform = ''; indicator.classList.remove('visible', 'ready'); return; }
    const pull = Math.min(dy, 120);
    indicator.style.transform = `translate(-50%, ${pull - 40}px)`;
    indicator.classList.add('visible');
    if (pull >= THRESHOLD) {
      indicator.classList.add('ready');
      indicator.querySelector('.ptr-text').textContent = '놓으면 새로고침';
      triggered = true;
    } else {
      indicator.classList.remove('ready');
      indicator.querySelector('.ptr-text').textContent = '당겨서 새로고침';
      triggered = false;
    }
  }, { passive: true });

  document.addEventListener('touchend', () => {
    if (!pulling) return;
    pulling = false;
    if (triggered) {
      indicator.classList.add('loading');
      indicator.querySelector('.ptr-text').textContent = '새로고침 중...';
      Promise.all([loadRecent(), loadHealth(), pollJobs()]).finally(() => {
        setTimeout(() => {
          indicator.classList.remove('visible', 'ready', 'loading');
          indicator.style.transform = '';
        }, 400);
      });
    } else {
      indicator.classList.remove('visible', 'ready');
      indicator.style.transform = '';
    }
  });
})();

// 앱이 다시 보일 때 잡 상태 즉시 갱신 + 폴링 재개 (백그라운드 복귀)
document.addEventListener('visibilitychange', () => {
  if (!document.hidden) { startPolling(); }
});

// ── 초기화 ──────────────────────────────────────────────
attachNotionHandlers();
registerServiceWorker().then(() => setupPush(false));  // 권한 이미 있으면 조용히 재구독
startPolling();  // 즉시 1회 폴 + 활성 잡 있으면 2초 간격 유지 (없으면 pollJobs 가 자동 중단)
console.log('[aiskillbox] v4.3 ready · Notification:', ('Notification' in window) ? Notification.permission : 'unsupported');
