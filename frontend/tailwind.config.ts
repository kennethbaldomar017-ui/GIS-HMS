import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        muted: "#667085",
        panel: "#f8fafc",
        brand: "#0f766e",
        danger: "#dc2626",
        warn: "#d97706"
      }
    },
  },
  plugins: [],
};
export default config;
