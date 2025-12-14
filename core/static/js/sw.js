
self.addEventListener("message", function (event) {
  if (event.data.action === "notify") {
    self.registration.showNotification(event.data.title, {
      body: event.data.body,
      // icon: "/static/icon.png", // optional
      vibrate: [200, 100, 200],
    });
  }
});
