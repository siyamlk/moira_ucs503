/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        parchment: "#f5f1e8",
        parchmentDark: "#eee7d8",
        ink: "#1c2333",
        moss: "#5c7a5c",
        mossLight: "#dce6da",
        sticky: "#f4e4a8",
        rose: "#e8b4ac",
        clay: "#c96f5c",
      },
      fontFamily: {
        serif: ["Georgia", "Iowan Old Style", "Times New Roman", "serif"],
        mono: ["JetBrains Mono", "Consolas", "monospace"],
        hand: ["Segoe Print", "Comic Sans MS", "cursive"],
      },
      backgroundImage: {
        dotgrid:
          "radial-gradient(circle, rgba(28,35,51,0.14) 1px, transparent 1px)",
      },
      backgroundSize: {
        dotgrid: "18px 18px",
      },
    },
  },
  plugins: [],
};
