(function () {
  const openers = document.querySelectorAll("[data-modal-open]");
  const closers = document.querySelectorAll("[data-modal-close]");

  function panel(id) {
    return document.getElementById(id);
  }

  function openModal(id) {
    const el = panel(id);
    if (!el) return;
    el.classList.remove("hidden");
    el.classList.add("flex");
    const backdrop = el.querySelector(".modal-backdrop");
    if (backdrop) requestAnimationFrame(() => backdrop.classList.add("is-open"));
    const focusable = el.querySelector("button, [href], input, select, textarea");
    if (focusable) focusable.focus();
    document.body.classList.add("overflow-hidden");
    el.dispatchEvent(new CustomEvent("modal:open", { bubbles: true }));
  }

  function closeModal(id) {
    const el = panel(id);
    if (!el) return;
    el.classList.add("hidden");
    el.classList.remove("flex");
    const backdrop = el.querySelector(".modal-backdrop");
    if (backdrop) backdrop.classList.remove("is-open");
    document.body.classList.remove("overflow-hidden");
  }

  window.PresentModal = { open: openModal, close: closeModal };

  openers.forEach((btn) => {
    btn.addEventListener("click", () => {
      const id = btn.getAttribute("data-modal-open");
      if (btn.dataset.courseCode) {
        document.querySelectorAll("[data-session-code]").forEach((node) => {
          node.textContent = btn.dataset.courseCode;
        });
      }
      if (btn.dataset.courseName) {
        document.querySelectorAll("[data-session-name]").forEach((node) => {
          node.textContent = btn.dataset.courseName;
        });
      }
      if (btn.dataset.sessionUrl) {
        const form = document.getElementById("start-session-form");
        if (form) form.setAttribute("action", btn.dataset.sessionUrl);
      }
      openModal(id);
    });
  });

  closers.forEach((btn) => {
    btn.addEventListener("click", () => closeModal(btn.getAttribute("data-modal-close")));
  });

  document.querySelectorAll("[data-modal]").forEach((el) => {
    el.addEventListener("click", (event) => {
      if (event.target === el || event.target.classList.contains("modal-backdrop")) {
        closeModal(el.id);
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape") return;
    document.querySelectorAll("[data-modal]:not(.hidden)").forEach((el) => closeModal(el.id));
  });
})();
