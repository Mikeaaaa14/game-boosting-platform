/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#ecfeff',
          100: '#cffafe',
          200: '#a5f3fc',
          300: '#67e8f9',
          400: '#22d3ee',
          500: '#06b6d4',
          600: '#0891b2',
          700: '#0e7490',
          800: '#155e75',
          900: '#164e63',
        },
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        neon: {
          pink: '#ff2d6b',
          'pink-light': '#ff6b9d',
          purple: '#b829dd',
          'purple-light': '#d946ef',
          blue: '#00f0ff',
        },
        dark: {
          base: '#0a0a0f',
          surface: '#12121a',
          elevated: '#1a1a2e',
        },
      },
      boxShadow: {
        glow: '0 18px 45px rgba(6, 182, 212, 0.28)',
        'glow-neon': '0 0 20px rgba(0, 240, 255, 0.3)',
        'glow-pink': '0 0 20px rgba(255, 45, 107, 0.3)',
        'glow-purple': '0 0 20px rgba(184, 41, 221, 0.3)',
        panel: '0 24px 70px rgba(2, 6, 23, 0.42)',
      },
      animation: {
        float: 'float 7s ease-in-out infinite',
        'fade-up': 'fadeUp 0.7s ease-out both',
        'pulse-soft': 'pulse 2.4s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        glitch: 'glitch 2s infinite',
        'glitch-once': 'glitch 0.8s ease-out 1',
        'scanline-move': 'scanlineMove 8s linear infinite',
        'neon-pulse': 'neonPulse 2s ease-in-out infinite',
        'flow-line': 'flowLine 3s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(14px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        glitch: {
          '0%, 100%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 2px)' },
          '40%': { transform: 'translate(-2px, -2px)' },
          '60%': { transform: 'translate(2px, 2px)' },
          '80%': { transform: 'translate(2px, -2px)' },
        },
        scanlineMove: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' },
        },
        neonPulse: {
          '0%, 100%': { boxShadow: '0 0 15px rgba(0, 240, 255, 0.3)' },
          '50%': { boxShadow: '0 0 30px rgba(0, 240, 255, 0.6)' },
        },
        flowLine: {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '200% 0%' },
        },
      },
    },
  },
  plugins: [],
}
