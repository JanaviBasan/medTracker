// Register service worker
if ("serviceWorker" in navigator) {
  navigator.serviceWorker
    .register("/static/sw.js")
    .then((reg) => console.log("SW registered", reg))
    .catch((err) => console.error("SW failed", err));
}

// Ask for notification permission
if (Notification.permission !== "granted") {
  Notification.requestPermission();
}

// Poll reminders every 30 seconds
function checkReminders() {
  fetch("/api/get-reminders/")
    .then((response) => response.json())
    .then((data) => {
      const now = new Date();

      data.forEach((rem) => {
        const reminderTime = new Date(rem.time);

        if (!rem.delivered && reminderTime <= now) {
          // Send message to service worker
          navigator.serviceWorker.ready.then((reg) => {
            reg.active.postMessage({
              action: "notify",
              title: "Medication Reminder",
              body: `Time to take ${rem.medicine}!`,
            });
          });

          // Mark reminder as delivered in Django
          fetch(`/api/mark-delivered/${rem.id}/`);
        }
      });
    });
}

// Check reminders every 30 seconds
setInterval(checkReminders, 30000);

// Run immediately
checkReminders();
