/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./**/templates/**/*.html"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Source Serif 4",
          "Iowan Old Style",
          "Palatino Linotype",
          "ui-serif",
          "serif",
        ],
        ui: [
          "Source Sans 3",
          "Segoe UI",
          "system-ui",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
