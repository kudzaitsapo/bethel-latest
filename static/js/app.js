// Add service worker to app.html

(() => {
	if ('serviceWorker' in navigator) {
		window.addEventListener('load', () => {
			navigator.serviceWorker.register("/sw.js").
			then((registration) => {
				console.log('registered');
				console.log(registration);
			}, (err) => {
				console.log(err);
			});
		});
	} else {
		alert('Service Worker is not supported in this browser!');
	 }
})();