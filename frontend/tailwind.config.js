/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        pharma: {
          50: '#f0f7ff',
          100: '#e0effe',
          500: '#2563eb',
          600: '#1d4ed8',
          700: '#1e40af',
          900: '#1e3a8a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      keyframes: {
        pulseHighlight: {
          '0%, 100%': { borderColor: '#818cf8', boxShadow: '0 0 0 3px rgba(129, 140, 248, 0.35)' },
          '50%': { borderColor: '#6366f1', boxShadow: '0 0 0 5px rgba(99, 102, 241, 0.5)' },
        }
      },
      animation: {
        'pulse-highlight': 'pulseHighlight 1.5s ease-in-out infinite',
      }
    },
  },
  plugins: [],
}
