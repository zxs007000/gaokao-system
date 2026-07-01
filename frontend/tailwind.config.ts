import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/pages/**/*.{js,ts,jsx,tsx,mdx}", "./src/components/**/*.{js,ts,jsx,tsx,mdx}", "./src/app/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        neon: { green: "#00d4aa", red: "#ff6b6b", yellow: "#ffd93d", blue: "#4ecdc4" },
        dark: { 900: "#0a0a0a", 800: "#1a1a2e", 700: "#16213e", 600: "#1f2b47" },
      },
      animation: { "fade-in": "fadeIn 0.3s ease-out" },
      keyframes: {
        fadeIn: { "0%": { opacity: "0", transform: "translateY(-4px)" }, "100%": { opacity: "1", transform: "translateY(0)" } },
      },
    },
  },
  plugins: [],
};
export default config;
