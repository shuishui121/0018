/** @type {import('tailwindcss').Config} */

export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,vue}'],
  theme: {
    container: {
      center: true,
      padding: { DEFAULT: '1.25rem', md: '2rem', lg: '3rem' },
    },
    extend: {
      colors: {
        ink: {
          DEFAULT: '#1A1714',
          50: '#F7F5F1',
          100: '#EDE9E1',
          200: '#D9D2C5',
          300: '#B8AE9C',
          400: '#8C8273',
          500: '#6B6258',
          600: '#4A4339',
          700: '#332E27',
          800: '#241F1A',
          900: '#1A1714',
        },
        paper: {
          DEFAULT: '#F5F1E8',
          warm: '#EFE9DA',
          deep: '#E7DFCB',
        },
        vermilion: {
          DEFAULT: '#9E2B25',
          light: '#C0443C',
          dark: '#7A1F1B',
        },
        gold: {
          DEFAULT: '#B8893B',
          light: '#D4A85A',
          dark: '#8C661F',
        },
        celadon: {
          DEFAULT: '#5C7A6B',
          light: '#7E9A8B',
        },
      },
      fontFamily: {
        serif: ['"Noto Serif SC"', 'serif'],
        sans: ['"Noto Sans SC"', 'sans-serif'],
        seal: ['"Ma Shan Zheng"', 'cursive'],
      },
      boxShadow: {
        paper: '0 1px 2px rgba(26,23,20,0.06), 0 4px 16px rgba(26,23,20,0.06)',
        lifted: '0 8px 30px rgba(26,23,20,0.12)',
        inset: 'inset 0 1px 3px rgba(26,23,20,0.12)',
      },
      backgroundImage: {
        'paper-grain':
          "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E\")",
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in': {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        'seal-stamp': {
          '0%': { opacity: '0', transform: 'scale(1.4) rotate(-8deg)' },
          '60%': { opacity: '0.95' },
          '100%': { opacity: '1', transform: 'scale(1) rotate(-4deg)' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.5s ease-out both',
        'slide-in': 'slide-in 0.35s cubic-bezier(0.22,1,0.36,1) both',
        'seal-stamp': 'seal-stamp 0.5s cubic-bezier(0.22,1,0.36,1) both',
      },
    },
  },
  plugins: [],
}
