// Coffee News of Aroostook — Service Worker
// Provides offline tile caching and faster repeat visits

var CACHE_NAME = 'coffee-news-v2';
var STATIC_URLS = [
  '/coffee-news-map/',
  '/coffee-news-map/index.html',
  '/coffee-news-map/manifest.webmanifest',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
  'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
  'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.css',
  'https://unpkg.com/leaflet.markercluster@1.5.3/dist/MarkerCluster.Default.css',
  'https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
];

// Install: cache static assets
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(STATIC_URLS).catch(function(err) {
        console.log('SW: cache.addAll partial failure (some URLs may be uncachable):', err);
      });
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate: clean old caches
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(
        names.filter(function(n) { return n !== CACHE_NAME; }).map(function(n) { return caches.delete(n); })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch: serve from cache, fall back to network, cache dynamically
self.addEventListener('fetch', function(event) {
  var url = event.request.url;

  // For map tiles: cache-first (fast repeat views), but only cache tiles at zooms 1-16 to limit size
  if (url.indexOf('tile.openstreetmap.org') !== -1) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        return fetch(event.request).then(function(response) {
          if (response && response.status === 200) {
            var copy = response.clone();
            caches.open(CACHE_NAME + '-tiles').then(function(cache) {
              cache.put(event.request, copy);
            });
          }
          return response;
        }).catch(function() {
          // If offline and no cached tile, return a transparent placeholder
          return new Response('', { status: 200, headers: { 'Content-Type': 'image/png' } });
        });
      })
    );
    return;
  }

  // For other requests: network-first with cache fallback
  event.respondWith(
    fetch(event.request).then(function(response) {
      if (response && response.status === 200 && url.indexOf('http') === 0) {
        var copy = response.clone();
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, copy);
        });
      }
      return response;
    }).catch(function() {
      return caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        // For navigation requests, serve the page
        if (event.request.mode === 'navigate') {
          return caches.match('/coffee-news-map/index.html') || caches.match('/coffee-news-map/');
        }
        return new Response('Offline', { status: 503 });
      });
    })
  );
});
