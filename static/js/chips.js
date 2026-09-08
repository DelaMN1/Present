(function () {
  document.querySelectorAll("[data-chip-group]").forEach((group) => {
    const input = group.querySelector("input[type='hidden']");
    const chips = group.querySelectorAll("[data-chip]");
    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        chips.forEach((item) => item.classList.remove("chip-active"));
        chip.classList.add("chip-active");
        if (input) input.value = chip.dataset.chip;
      });
    });
  });
})();
