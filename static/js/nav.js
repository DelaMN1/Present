(function () {
  const drawer = document.getElementById("lecturer-drawer");
  const openers = document.querySelectorAll("[data-drawer-open]");
  const closers = document.querySelectorAll("[data-drawer-close]");
  if (!drawer) return;

  function openDrawer() {
    drawer.classList.remove("hidden");
    drawer.classList.add("flex");
    document.body.classList.add("overflow-hidden");
    const closeBtn = drawer.querySelector("[data-drawer-close]");
    if (closeBtn) closeBtn.focus();
  }

  function closeDrawer() {
    drawer.classList.add("hidden");
    drawer.classList.remove("flex");
    document.body.classList.remove("overflow-hidden");
  }

  openers.forEach((btn) => btn.addEventListener("click", openDrawer));
  closers.forEach((btn) => btn.addEventListener("click", closeDrawer));
  drawer.addEventListener("click", (event) => {
    if (event.target === drawer) closeDrawer();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !drawer.classList.contains("hidden")) closeDrawer();
  });
})();
