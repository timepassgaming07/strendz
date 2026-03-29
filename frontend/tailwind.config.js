/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#fdf2f8",
          100: "#fce7f3",
          200: "#fbcfe8",
          300: "#f9a8d4",
          400: "#f472b6",
          500: "#ec4899",
          600: "#db2777",
          700: "#be185d",
        },
        accent: {
          50: "#f5f3ff",
          100: "#ede9fe",
          200: "#ddd6fe",
          300: "#c4b5fd",
          400: "#a78bfa",
          500: "#8b5cf6",
          600: "#7c3aed",
          700: "#6d28d9",
        },
      },
      backgroundImage: {
        "gradient-main": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "gradient-card": "linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)",
        "gradient-pink": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "gradient-blue": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "gradient-green": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "gradient-orange": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
      },
    },
  },
  plugins: [],
};
