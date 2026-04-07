/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#fff5f4',
          100: '#ffe3de',
          200: '#ffc8c0',
          300: '#ff9f93',
          400: '#ff6a62',
          500: '#ff4655',
          600: '#e13745',
          700: '#b92d38',
          800: '#812129',
          900: '#56161b',
        },
        accent: {
          50: '#fffaee',
          100: '#fdefcf',
          200: '#f6d79c',
          300: '#e7bd67',
          400: '#cfa45e',
          500: '#a98349',
          600: '#896936',
          700: '#67502a',
          800: '#45361d',
          900: '#2b2112',
        },
        neon: {
          pink: '#ff4655',
          'pink-light': '#ff7c71',
          purple: '#8e86b6',
          'purple-light': '#b1a7dd',
          blue: '#82b8ff',
        },
        dark: {
          base: '#070809',
          surface: '#111317',
          elevated: '#1a1d23',
        },
      },
      boxShadow: {
        glow: '0 18px 45px rgba(255, 70, 85, 0.18)',
        'glow-neon': '0 0 20px rgba(255, 70, 85, 0.18)',
        'glow-pink': '0 0 20px rgba(255, 70, 85, 0.2)',
        'glow-purple': '0 0 20px rgba(130, 184, 255, 0.14)',
        panel: '0 30px 90px rgba(0, 0, 0, 0.42)',
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
        shimmer: 'shimmer 8s linear infinite',
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
          '0%, 100%': { boxShadow: '0 0 15px rgba(255, 70, 85, 0.18)' },
          '50%': { boxShadow: '0 0 30px rgba(255, 70, 85, 0.28)' },
        },
        flowLine: {
          '0%': { backgroundPosition: '0% 0%' },
          '100%': { backgroundPosition: '200% 0%' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0%' },
          '100%': { backgroundPosition: '200% 0%' },
        },
      },
    },
  },
  plugins: [],
}
