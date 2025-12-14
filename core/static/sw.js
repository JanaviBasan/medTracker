self.addEventListener("install", () => {
  console.log("Service Worker installed");
  self.skipWaiting();
});

self.addEventListener("activate", () => {
  console.log("Service Worker activated");
});

self.addEventListener("message", function (event) {
  const data = event.data;

  if (data.action === "notify") {
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: "/static/icons/medcia.png",
    });
  }
});
