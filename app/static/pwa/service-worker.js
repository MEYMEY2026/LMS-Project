const CACHE_NAME = 'lms-cache-v1';

self.addEventListener('install', (event) => {
    self.skipWaiting();
});

self.addEventListener('fetch', (event) => {
    // យើងមិនធ្វើ Cache ទិន្នន័យ Dynamic ទេ ដើម្បីកុំឱ្យវាបង្ហាញទិន្នន័យចាស់
    event.respondWith(fetch(event.request));
});