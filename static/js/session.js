(function () {
  const root = document.querySelector("[data-session]");
  if (root) {
    const display = root.querySelector("[data-countdown]");
    const classroomToggle = root.querySelector("[data-classroom-toggle]");
    const privateOnly = root.querySelectorAll("[data-private-only]");
    let remaining = Number(root.dataset.durationSeconds || 0);

    function format(seconds) {
      const safe = Math.max(0, seconds);
      const m = String(Math.floor(safe / 60)).padStart(2, "0");
      const s = String(safe % 60).padStart(2, "0");
      return m + ":" + s;
    }

    if (display) display.textContent = format(remaining);

    const timer = window.setInterval(() => {
      remaining -= 1;
      if (display) display.textContent = format(remaining);
      if (remaining <= 0) window.clearInterval(timer);
    }, 1000);

    if (classroomToggle) {
      classroomToggle.addEventListener("click", () => {
        const on = classroomToggle.getAttribute("aria-pressed") === "true";
        classroomToggle.setAttribute("aria-pressed", on ? "false" : "true");
        classroomToggle.textContent = on ? "Classroom mode" : "Exit classroom mode";
        privateOnly.forEach((node) => node.classList.toggle("hidden", !on));
      });
    }
  }

  function setLocationStatus(html) {
    document.querySelectorAll("[data-location-status]").forEach((node) => {
      node.innerHTML = html;
    });
  }

  function requestLocation() {
    if (!navigator.geolocation) {
      setLocationStatus(
        '<span class="text-amber-700">Location unavailable</span><p class="mt-1 text-sm text-slate-500">Students must be in the room when sessions record check-ins.</p>'
      );
      return;
    }
    navigator.geolocation.getCurrentPosition(
      () => {
        setLocationStatus(
          '<span class="text-emerald-600">Ready</span><p class="mt-1 text-sm text-slate-500">This device will set the classroom location when sessions record check-ins.</p>'
        );
      },
      () => {
        setLocationStatus(
          '<span class="text-amber-700">Location needed</span><p class="mt-1 text-sm text-slate-500">Allow location access so students can check in from the room.</p>'
        );
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  }

  document.querySelectorAll("[data-modal]").forEach((el) => {
    el.addEventListener("modal:open", () => {
      if (el.querySelector("[data-location-status]")) requestLocation();
    });
  });
})();
