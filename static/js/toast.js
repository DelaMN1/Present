(function () {
  const root = document.getElementById("toast-root");
  if (!root) return;

  function dismiss(toast) {
    toast.classList.add("opacity-0", "translate-y-1");
    window.setTimeout(() => toast.remove(), 200);
  }

  root.querySelectorAll("[data-toast]").forEach((toast) => {
    const timeout = Number(toast.dataset.timeout || 5000);
    const closer = toast.querySelector("[data-toast-close]");
    if (closer) closer.addEventListener("click", () => dismiss(toast));
    if (timeout > 0) window.setTimeout(() => dismiss(toast), timeout);
  });
})();
