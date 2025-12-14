document.addEventListener("DOMContentLoaded", () => {

  let activeReminderId = null;

  // ================================
  // SERVICE WORKER
  // ================================
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker
      .register("/static/js/sw.js")
      .then(() => console.log("SW registered"))
      .catch((err) => console.error("SW failed", err));
  }

  // ================================
  // MODAL FUNCTIONS
  // ================================
  window.showReminderModal = function (message, reminderId) {
    const modal = document.getElementById("reminderModal");
    const text = document.getElementById("reminderText");

    if (!modal || !text) {
      console.error("Reminder modal HTML missing");
      return;
    }

    text.innerText = message;
    modal.style.display = "block";
    activeReminderId = reminderId;
  };

  window.closeReminderModal = function () {
    if (activeReminderId === null) return;

    fetch(`/api/mark-delivered/${activeReminderId}/`)
      .then(() => {
        document.getElementById("reminderModal").style.display = "none";
        activeReminderId = null;
      });
  };

  // ================================
  // REMINDER CHECK
  // ================================
  function checkReminders() {
    if (activeReminderId !== null) return;

    fetch("/api/get-reminders/")
      .then((res) => res.json())
      .then((data) => {
        if (!data.length) return;

        const now = new Date();
        const rem = data[0];
        const reminderTime = new Date(rem.time);

        if (!rem.delivered && reminderTime <= now) {
          showReminderModal(
            `Time to take ${rem.medicine}`,
            rem.id
          );

          if (Notification.permission === "granted") {
            new Notification("Medication Reminder", {
              body: `Time to take ${rem.medicine}`,
            });
          }
        }
      });
  }

  setInterval(checkReminders, 30000);
  checkReminders();
});
