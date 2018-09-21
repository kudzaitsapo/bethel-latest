// Service Worker to cache static files and stuff

self.addEventListener('install', (event) => {
	if (!('caches' in self)) return;
	event.waitUntil(
		caches.open('ver_test2').then((cache) => {
			return cache.addAll(
			  [
				'/static/img/favicon.png',
				'/static/img/icon.png',
				'/static/img/sidebar-1.jpg',
				'/static/css/bootstrap.min.css',
				'/static/css/material-dashboard.css',
				'/static/css/material_icons.css',
				'/static/css/material_icons.woff2',
				'/static/js/bootstrap.min.js',
				'/static/js/bootstrap-notify.js',
				'/static/js/chartist.min.js',
				'/static/js/material.min.js',
				'/static/js/material-dashboard.js',
				'/static/js/jquery-3.1.0.min.js',
				'/'
			  ]
			);
		})
	);
	console.log('caches service worker Installed!', event);
});

self.addEventListener('activate', (event) =>{
	console.log('service worker activated!', event);
});

self.addEventListener('fetch', (event) => {
	event.respondWith(
		caches.match(event.request).then((response) => {
			return response || fetch(event.request);
		})
	);
});