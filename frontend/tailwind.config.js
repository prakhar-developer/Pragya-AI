/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#F8FAFC",
        card: "#FFFFFF",
        border: "#E2E8F0",
        body: "#1E293B",
        muted: "#64748B",
        violet: {
          DEFAULT: "#6D28D9",
          50: "#F5F3FF",
          100: "#EDE9FE",
          200: "#DDD6FE",
          600: "#7C3AED",
          700: "#6D28D9",
          800: "#5B21B6",
        },
        teal: {
          DEFAULT: "#0F766E",
          50: "#F0FDFA",
          100: "#CCFBF1",
          600: "#0D9488",
          700: "#0F766E",
        },
        rose: {
          DEFAULT: "#9F1239",
          50: "#FFF1F2",
          100: "#FFE4E6",
          600: "#E11D48",
          700: "#9F1239",
        },
        amber: {
          DEFAULT: "#B45309",
          50: "#FFFBEB",
          100: "#FEF3C7",
          600: "#D97706",
          700: "#B45309",
          800: "#92400E",
        },
        slatenavy: "#1E3A5F",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        sm: "0 1px 2px 0 rgba(30, 41, 59, 0.06), 0 1px 3px 0 rgba(30, 41, 59, 0.05)",
        card: "0 4px 20px -4px rgba(30, 41, 59, 0.08)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        pulseSoft: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.5" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.3s ease-out",
        "pulse-soft": "pulseSoft 1.5s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
