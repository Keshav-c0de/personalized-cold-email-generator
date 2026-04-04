/** @type {import('tailwindcss').Config} */
export default {
  content: ['./popup.html', './src/**/*.{ts,vue}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        ink: '#0f172a',
        mist: '#e2e8f0',
        ember: '#f97316',
        aqua: '#22d3ee',
      },
      boxShadow: {
        glow: '0 20px 80px rgba(15, 23, 42, 0.35)',
      },
    },
  },
  plugins: [],
};