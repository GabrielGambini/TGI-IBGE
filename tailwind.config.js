export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: { extend: {
    colors: { bg: "#080D18", card: "#111B2B", brand: "#3B82F6", up: "#22C55E", down: "#EF4444" },
    fontFamily: { sans: ["Inter", "system-ui", "sans-serif"] }
  } },
  plugins: []
};
