/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2A2356',
        secondary: '#FFD700',
        tertiary: '#E25822',
        neutral: '#F8F9FA',
        dark: '#0A0A0A',
      },
      fontFamily: {
        sans: ['Poppins', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(circle at center, rgba(234, 179, 8, 0.1) 0%, transparent 70%)',
        'gradient-linear': 'linear-gradient(45deg, transparent 48%, rgba(42, 35, 86, 0.1) 50%, transparent 52%)',
      },
    },
  },
  plugins: [],
}