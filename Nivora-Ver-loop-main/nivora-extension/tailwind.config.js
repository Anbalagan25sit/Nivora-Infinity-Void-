/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        foreground: '#e5e5e5',
        primary: {
          DEFAULT: '#2dd4bf',
          hover: '#14b8a6',
        },
        secondary: '#9333ea',
        muted: {
          DEFAULT: '#252547',
          foreground: '#a1a1aa',
        },
        accent: '#1a1a2e',
        destructive: '#ef4444',
        border: 'rgba(255, 255, 255, 0.1)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
