// aiskillbox 서비스워커 — Web Push 백그라운드 알림
// 앱이 백그라운드/종료 상태여도 잡 완료 푸시를 받아 알림을 띄운다.

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// 서버에서 보낸 푸시 수신 → 알림 표시
self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (e) { data = {}; }
  const title = data.title || 'aiskillbox';
  const options = {
    body: data.body || '작업이 완료됐어요',
    icon: '/static/icon-192.png',
    badge: '/static/icon-192.png',
    tag: data.tag || 'aiskillbox-job',
    renotify: true,
    vibrate: [120, 60, 120],
    data: { url: data.url || '/' },
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

// 알림 클릭 → 앱(또는 결과 페이지) 열기/포커스
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  // 푸시 페이로드의 url 은 신뢰 경계 밖 — 자기 출처/Notion 만 허용 (오픈 리다이렉트 차단)
  const raw = (event.notification.data && event.notification.data.url) || '/';
  const target = (raw.startsWith('/')
    || raw.startsWith('https://www.notion.so/')
    || raw.startsWith('notion://')) ? raw : '/';
  event.waitUntil((async () => {
    const wins = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    for (const c of wins) {
      if ('focus' in c) {
        await c.focus();
        if (target && target !== '/' && 'navigate' in c) {
          try { await c.navigate(target); } catch (e) { /* 무시 */ }
        }
        return;
      }
    }
    if (self.clients.openWindow) await self.clients.openWindow(target);
  })());
});
