// Service Worker for Four Sided Triangle App
const CACHE_NAME = 'four-sided-triangle-cache-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/about',
  '/offline',
  '/favicon.ico',
  '/manifest.json',
  '/images/logo.png',
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing Service Worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('[Service Worker] All assets cached');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[Service Worker] Cache install error:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating Service Worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== CACHE_NAME) {
              console.log('[Service Worker] Removing old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[Service Worker] Service Worker activated');
        return self.clients.claim();
      })
  );
});

// Special handling for API requests
const handleApiRequest = async (request) => {
  try {
    // Try to fetch from network first
    const response = await fetch(request);
    
    // Clone the response to store in cache while returning the original
    if (response.status === 200) {
      const responseClone = response.clone();
      caches.open(CACHE_NAME)
        .then((cache) => {
          cache.put(request, responseClone);
        });
    }
    
    return response;
  } catch (error) {
    // If network fails, try to return from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // If no cache for this specific API request, return a graceful error response
    return new Response(
      JSON.stringify({
        error: 'You are currently offline. This request requires an internet connection.',
        isOffline: true,
      }),
      {
        status: 503,
        headers: { 'Content-Type': 'application/json' },
      }
    );
  }
};

// Fetch event - network first with cache fallback strategy
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = new URL(request.url);
  
  // Handle API requests (network first, then cache)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(handleApiRequest(request));
    return;
  }
  
  // For other requests, try cache first, then network
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // Return from cache if available
          return cachedResponse;
        }
        
        // Otherwise fetch from network
        return fetch(request)
          .then((response) => {
            // Don't cache non-successful responses
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Cache successful responses
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(request, responseToCache);
              });
            
            return response;
          })
          .catch((error) => {
            // For navigation requests, return the offline page when offline
            if (request.mode === 'navigate') {
              return caches.match('/offline');
            }
            
            // For images, return a placeholder
            if (request.destination === 'image') {
              return caches.match('/images/offline-placeholder.png');
            }
            
            // For other resources, just propagate the error
            throw error;
          });
      })
  );
});

// Handle push notifications
self.addEventListener('push', (event) => {
  const data = event.data.json();
  
  const options = {
    body: data.body || 'New update available',
    icon: '/images/logo.png',
    badge: '/images/badge.png',
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(
      data.title || 'Four Sided Triangle', 
      options
    )
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
