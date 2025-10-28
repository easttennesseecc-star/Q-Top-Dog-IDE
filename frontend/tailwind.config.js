/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        slate: {
          '850': '#1a202c',
          '950': '#0f172a',
        }
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(to bottom right, #0f172a, #1a1f2e, #0f172a)',
      }
    },
  },
  plugins: [],
};

