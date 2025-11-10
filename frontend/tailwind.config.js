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
        },
        brand: {
          DEFAULT: '#0ea5e9', // cyan-500 as primary accent
          '50': '#f0f9ff',
          '100': '#e0f2fe',
          '200': '#bae6fd',
          '300': '#7dd3fc',
          '400': '#38bdf8',
          '500': '#0ea5e9',
          '600': '#0284c7',
          '700': '#0369a1',
          '800': '#075985',
          '900': '#0c4a6e'
        },
        surface: {
          light: '#ffffff',
          lightSubtle: '#f5f7fa',
          dark: '#0f172a',
          darkElevated: '#1a2332',
          darkSubtle: '#132030'
        },
        text: {
          light: '#0f172a',
          lightMuted: '#495869',
          dark: '#f1f5f9',
          darkMuted: '#c2c8d0',
          darkLowContrast: '#94a3b8'
        },
        danger: {
          DEFAULT: '#ef4444'
        },
        success: {
          DEFAULT: '#10b981'
        }
      },
      backgroundImage: {
        'gradient-dark': 'linear-gradient(to bottom right, #0f172a, #1a1f2e, #0f172a)',
      }
    },
  },
  plugins: [],
};

