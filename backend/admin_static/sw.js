// Q‑IDE Web Push Service Worker
self.addEventListener('push', event => {
  try {
    const data = event.data ? event.data.text() : '{}';
    let payload = {};
    try { payload = JSON.parse(data); } catch { payload = { title: 'Q‑IDE', body: data }; }
    const title = payload.title || 'Q‑IDE';
    const body = payload.body || 'Notification';
    const options = {
      body,
      data: payload.data || {},
      icon: '/assets/icon.png'
    };
    event.waitUntil(self.registration.showNotification(title, options));
  } catch (e) {
    // ignore
  }
});

self.addEventListener('notificationclick', event => {
  const d = event.notification && event.notification.data || {};
  const url = d.approve_link || d.modify_link || '/';
  event.notification.close();
  event.waitUntil(clients.openWindow(url));
});
