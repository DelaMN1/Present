/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.html", "./static/js/**/*.js"],
  theme: {
    extend: {
      colors: {
        canvas: "#F8FAFC",
        surface: "#FFFFFF",
        muted: "#F1F5F9",
        ink: {
          DEFAULT: "#111827",
          secondary: "#64748B",
          muted: "#94A3B8",
        },
        line: "#E2E8F0",
        brand: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          500: "#4F46E5",
          600: "#4338CA",
          700: "#3730A3",
        },
        sidebar: "#0F172A",
      },
      fontFamily: {
        sans: ["Inter", "Segoe UI", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 16px rgba(15, 23, 42, 0.04)",
      },
      borderRadius: {
        card: "12px",
        control: "10px",
      },
      maxWidth: {
        content: "1400px",
      },
    },
  },
  plugins: [],
};
