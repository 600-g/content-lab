// aiskillbox 클라이언트
const ACTIVE_JOB_KEY = 'aiskillbox.activeJob.v1';

// ── 완료 알림 권한 (페이지 진입 시 한 번만 요청) ────────
function ensureNotifyPermission() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    Notification.requestPermission().catch(() => {});
  }
}

function notifyDone(title, body) {
  // 1) 브라우저 알림
  try {
    if ('Notification' in window && Notification.permission === 'granted') {
      const n = new Notification(title, { body, icon: '/static/icon-192.png', tag: 'aiskillbox-done' });
      setTimeout(() => n.close(), 6000);
    }
  } catch {}
  // 2) 진동 (모바일)
  try { navigator.vibrate?.([120, 60, 120]); } catch {}
  // 3) 소리 (짧은 beep)
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

const form = document.getElementById('collect-form');
const urlInput = document.getElementById('url');
const submitBtn = document.getElementById('submit-btn');
const jobStatus = document.getElementById('job-status');
const jobBadge = document.getElementById('job-badge');
const jobStage = document.getElementById('job-stage');
const jobDetail = document.getElementById('job-detail');
const jobResult = document.getElementById('job-result');
const recentList = document.getElementById('recent-list');
const recentCount = document.getElementById('recent-count');
const recentEmpty = document.getElementById('recent-empty');

const drawer = document.getElementById('drawer');
const backdrop = document.getElementById('drawer-backdrop');
const drawerToggle = document.getElementById('drawer-toggle');
const drawerClose = document.getElementById('drawer-close');

// ── UA: 모바일 감지 ────────────────────────────────────
const IS_MOBILE = /iPad|iPhone|iPod|Android/i.test(navigator.userAgent)
  || (navigator.maxTouchPoints > 1 && /Mac/i.test(navigator.platform)); // iPadOS 13+

// ── 드로어 ────────────────────────────────────────────
function openDrawer() {
  drawer.classList.add('open');
  drawer.setAttribute('aria-hidden', 'false');
  backdrop.classList.remove('hidden');
  document.body.classList.add('drawer-open');
  document.body.style.overflow = 'hidden';
  loadHealth();
  loadRecent();
  loadActiveJobs();
  // 드로어 열린 동안 활성 잡 5초마다 갱신
  if (!drawer._activeTimer) {
    drawer._activeTimer = setInterval(loadActiveJobs, 5000);
  }
}
function closeDrawer() {
  drawer.classList.remove('open');
  drawer.setAttribute('aria-hidden', 'true');
  backdrop.classList.add('hidden');
  document.body.classList.remove('drawer-open');
  document.body.style.overflow = '';
  if (drawer._activeTimer) {
    clearInterval(drawer._activeTimer);
    drawer._activeTimer = null;
  }
}
drawerToggle.addEventListener('click', () => {
  drawer.classList.contains('open') ? closeDrawer() : openDrawer();
});
drawerClose.addEventListener('click', closeDrawer);
backdrop.addEventListener('click', closeDrawer);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && drawer.classList.contains('open')) closeDrawer();
});

// ── Notion deeplink: 모바일이면 notion:// 시도 + 폴백 ──
function attachNotionHandlers() {
  document.querySelectorAll('a[data-app][data-web]').forEach(a => {
    if (a.dataset.bound) return;
    a.dataset.bound = '1';
    a.addEventListener('click', (e) => {
      const app = a.dataset.app;
      const web = a.dataset.web;
      if (!IS_MOBILE) return; // 데스크톱: 기본 href(web) 그대로 진행
      e.preventDefault();
      // 모바일: notion:// 즉시 시도, 0.9s 안에 페이지가 살아있으면 web으로 폴백
      const t = setTimeout(() => {
        if (!document.hidden) window.location.href = web;
      }, 900);
      // 페이지가 hidden되면 (앱 열린 것) 폴백 취소
      const onVis = () => {
        if (document.hidden) {
          clearTimeout(t);
          document.removeEventListener('visibilitychange', onVis);
        }
      };
      document.addEventListener('visibilitychange', onVis);
      window.location.href = app;
    });
  });
}

// ── 활성 잡 리스트 (드로어) ───────────────────────────
const activeList = document.getElementById('active-list');
const activeEmpty = document.getElementById('active-empty');
const activeCount = document.getElementById('active-count');

async function loadActiveJobs() {
  try {
    const resp = await fetch('/api/jobs/active');
    const d = await resp.json();
    if (!d.ok) return;
    const items = (d.items || []).filter(i => i.status === 'queued' || i.status === 'running');
    activeCount.textContent = items.length > 0 ? `${items.length}건` : '';
    if (items.length === 0) {
      activeList.innerHTML = '';
      activeEmpty?.classList.remove('hidden');
      return;
    }
    activeEmpty?.classList.add('hidden');
    activeList.innerHTML = items.map(j => `
      <li>
        <span class="url">${escapeHtml(j.url)}</span>
        <div class="meta-row">
          <span class="pulse"></span>
          <span>${escapeHtml(humanStage(j.stage || j.status))}</span>
          <span class="elapsed">${j.elapsed}초 경과</span>
        </div>
      </li>
    `).join('');
  } catch {}
}

// ── 시스템 상태 ────────────────────────────────────────
async function loadHealth() {
  try {
    const resp = await fetch('/healthz');
    const d = await resp.json();
    const gem = document.getElementById('health-gemini');
    const not = document.getElementById('health-notion');
    gem.textContent = d.gemini_configured ? '✅' : '❌';
    gem.className = 'dot ' + (d.gemini_configured ? 'ok' : 'bad');
    not.textContent = d.notion_configured ? '✅' : '❌';
    not.className = 'dot ' + (d.notion_configured ? 'ok' : 'bad');
    document.getElementById('health-jobs').textContent = d.active_jobs + '건';
    document.getElementById('health-recent').textContent = d.recent_count + '건';
  } catch {}
}
document.getElementById('health-refresh').addEventListener('click', loadHealth);

// ── 수집 폼 ────────────────────────────────────────────
let pollTimer = null;

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = urlInput.value.trim();
  if (!url) return;

  submitBtn.disabled = true;
  submitBtn.querySelector('.btn-label').textContent = '시작 중...';
  jobStatus.classList.remove('hidden');
  jobDetail.classList.add('hidden');
  jobBadge.className = 'badge';
  jobBadge.textContent = '대기 중';
  jobStage.innerHTML = '큐 대기';
  urlInput.blur();

  try {
    const resp = await fetch('/api/collect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const data = await resp.json();
    if (!data.ok) throw new Error(data.error || '요청 실패');
    try { localStorage.setItem(ACTIVE_JOB_KEY, data.job_id); } catch {}
    pollJob(data.job_id);
  } catch (err) {
    showError('요청 실패: ' + err.message, '인터넷 또는 서버 상태 확인');
    submitBtn.disabled = false;
    submitBtn.querySelector('.btn-label').textContent = '수집 시작';
  }
});

// 페이지 로드 시 — 진행 중 잡 있으면 자동 폴링 재개
(async function resumeActiveJob() {
  let jobId = '';
  try { jobId = localStorage.getItem(ACTIVE_JOB_KEY) || ''; } catch {}
  if (!jobId) return;
  try {
    const resp = await fetch(`/api/status/${jobId}`);
    const data = await resp.json();
    if (!data.ok) {
      // 잡 없음 — 만료
      try { localStorage.removeItem(ACTIVE_JOB_KEY); } catch {}
      return;
    }
    const job = data.job;
    submitBtn.disabled = true;
    submitBtn.querySelector('.btn-label').textContent = '진행 중 (이어서)...';
    jobStatus.classList.remove('hidden');
    jobBadge.className = 'badge warn';
    jobBadge.textContent = '🔄 이어서 추적 중';
    jobStage.innerHTML = `<b>${humanStage(job.stage || job.status)}</b>`;
    if (job.status === 'completed' || job.status === 'failed') {
      // 이미 끝남
      renderResult(job);
      submitBtn.disabled = false;
      submitBtn.querySelector('.btn-label').textContent = '수집 시작';
      try { localStorage.removeItem(ACTIVE_JOB_KEY); } catch {}
    } else {
      pollJob(jobId);
    }
  } catch {
    try { localStorage.removeItem(ACTIVE_JOB_KEY); } catch {}
  }
})();

function pollJob(jobId) {
  clearInterval(pollTimer);
  pollTimer = setInterval(async () => {
    try {
      const resp = await fetch(`/api/status/${jobId}`);
      const data = await resp.json();
      if (!data.ok) throw new Error('상태 조회 실패');
      const job = data.job;
      jobStage.innerHTML = `<b>${humanStage(job.stage || job.status)}</b>`;
      if (job.status === 'completed' || job.status === 'failed') {
        clearInterval(pollTimer);
        renderResult(job);
        submitBtn.disabled = false;
        submitBtn.querySelector('.btn-label').textContent = '수집 시작';
        try { localStorage.removeItem(ACTIVE_JOB_KEY); } catch {}
        // 완료 알림
        const r = job.result || {};
        const skill = r.skill || {};
        if (job.status === 'completed') {
          const tag = r.partial_ok ? '⚠️ 부분 성공' : r.skipped ? '⏭ 스킵' : skill.merged ? '🔀 합병됨' : '✅ 완료';
          notifyDone(`aiskillbox · ${tag}`, skill.title || skill.name || job.url);
          if (!r.skipped) {
            urlInput.value = '';
            loadRecent();
          }
        } else {
          notifyDone('aiskillbox · ❌ 실패', r.error_ko || '오류 발생');
        }
      }
    } catch (err) { console.error(err); }
  }, 1500);
}

function renderResult(job) {
  const r = job.result || {};
  const partial = r.partial_ok;
  const merged = r.skill?.merged;

  if (job.status === 'completed') {
    if (partial) { jobBadge.className = 'badge warn'; jobBadge.textContent = '⚠️ 부분 성공'; }
    else if (r.skipped) { jobBadge.className = 'badge'; jobBadge.textContent = '⏭ 스킵'; }
    else if (merged) { jobBadge.className = 'badge merged'; jobBadge.textContent = '🔀 합병됨'; }
    else { jobBadge.className = 'badge success'; jobBadge.textContent = '✅ 완료'; }
  } else {
    jobBadge.className = 'badge failed';
    jobBadge.textContent = '❌ 실패';
  }

  const stages = r.stages || {};
  const stageRows = Object.entries(stages).map(([key, st]) => {
    const ok = st?.ok;
    const icon = ok === true ? '✅' : ok === false ? '❌' : '⏳';
    const name = st?.stage || key;
    const note = st?.error_ko || st?.action || st?.note || '';
    return `<div class="stage-row">
      <span class="stage-icon">${icon}</span>
      <span class="stage-name">${escapeHtml(name)}</span>
      ${note ? `<span class="stage-note">${escapeHtml(note)}</span>` : ''}
    </div>`;
  }).join('');

  let hintBlock = '';
  if (r.error_ko || r.hint) {
    hintBlock = `<div class="error-card">
      <div class="error-title">🚨 ${escapeHtml(r.error_ko || '오류')}</div>
      ${r.hint ? `<div class="error-hint">💡 ${escapeHtml(r.hint)}</div>` : ''}
    </div>`;
  }
  const msgBlock = r.message_ko ? `<div class="success-msg">${escapeHtml(r.message_ko)}</div>` : '';
  jobStage.innerHTML = `${msgBlock}${hintBlock}<div class="stages">${stageRows}</div>`;
  jobResult.textContent = JSON.stringify(job.result || { error: job.error }, null, 2);
  jobDetail.classList.remove('hidden');
}

function showError(title, hint) {
  jobStatus.classList.remove('hidden');
  jobBadge.className = 'badge failed';
  jobBadge.textContent = '❌ 실패';
  jobStage.innerHTML = `<div class="error-card">
    <div class="error-title">🚨 ${escapeHtml(title)}</div>
    ${hint ? `<div class="error-hint">💡 ${escapeHtml(hint)}</div>` : ''}
  </div>`;
}

function humanStage(s) {
  return ({
    'queued': '큐 대기 중',
    'scraping': '웹 스크래핑 중',
    'running': '처리 중',
    'completed': '완료',
    'failed': '실패',
  }[s] || s);
}

// 검색/필터 상태
const recentSearchInput = document.getElementById('recent-search');
const gradeFiltersEl = document.getElementById('grade-filters');
let _recentCache = [];
let _filterGrade = 'all';
let _searchQuery = '';

function _filterRecent(items) {
  const q = _searchQuery.trim().toLowerCase();
  return items.filter(it => {
    if (_filterGrade !== 'all' && (it.grade || '') !== _filterGrade) return false;
    if (!q) return true;
    const hay = [
      it.skill_title, it.skill_name, it.category,
      ...(it.tags || []),
    ].filter(Boolean).join(' ').toLowerCase();
    return hay.includes(q);
  });
}

if (recentSearchInput) {
  recentSearchInput.addEventListener('input', (e) => {
    _searchQuery = e.target.value;
    _renderRecentList();
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
  recentCount.textContent = _recentCache.length > 0
    ? `${filtered.length}/${_recentCache.length}건` : '';
  if (filtered.length === 0) {
    recentList.innerHTML = '';
    recentEmpty?.classList.remove('hidden');
    return;
  }
  recentEmpty?.classList.add('hidden');
  recentList.innerHTML = filtered.slice(0, 30).map(_renderRecentItem).join('');
  attachNotionHandlers();
}

// _renderRecentItem 은 위 새 정의 사용 (중복 제거됨)

function escapeHtml(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  })[c]);
}

// 초기 바인딩 (정적 deeplink: db 칩 + 통합 페이지 카드)
attachNotionHandlers();
// db 칩도 app/web 둘 다 있으면 바인딩
(function bindChip() {
  const chip = document.getElementById('db-chip');
  if (chip) {
    const appUrl = chip.getAttribute('data-app');
    if (appUrl && !chip.dataset.bound) {
      chip.dataset.bound = '1';
      chip.addEventListener('click', (e) => {
        const web = chip.getAttribute('data-web');
        if (!IS_MOBILE) return;
        e.preventDefault();
        const t = setTimeout(() => { if (!document.hidden) window.location.href = web; }, 900);
        document.addEventListener('visibilitychange', () => {
          if (document.hidden) clearTimeout(t);
        }, { once: true });
        window.location.href = appUrl;
      });
    }
  }
})();

// ── 위→아래 드래그 새로고침 (Pull-to-Refresh) ─────────
(function initPullToRefresh() {
  let startY = 0;
  let pulling = false;
  let triggered = false;
  const THRESHOLD = 80;

  const indicator = document.createElement('div');
  indicator.id = 'ptr-indicator';
  indicator.innerHTML = '<span class="ptr-icon">⟳</span> <span class="ptr-text">당겨서 새로고침</span>';
  document.body.appendChild(indicator);

  document.addEventListener('touchstart', (e) => {
    if (document.body.classList.contains('drawer-open')) return;
    if (window.scrollY > 4) return;
    startY = e.touches[0].clientY;
    pulling = true;
    triggered = false;
  }, { passive: true });

  document.addEventListener('touchmove', (e) => {
    if (!pulling) return;
    const dy = e.touches[0].clientY - startY;
    if (dy <= 0) {
      indicator.style.transform = '';
      indicator.classList.remove('visible', 'ready');
      return;
    }
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
      Promise.all([loadRecent(), loadHealth(), loadActiveJobs()])
        .finally(() => {
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

ensureNotifyPermission();
