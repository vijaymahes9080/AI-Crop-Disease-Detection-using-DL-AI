/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        slate: {
          950: 'hsl(222, 47%, 6%)',
          900: 'hsl(222, 47%, 11%)',
          800: 'hsl(217, 33%, 17%)',
          700: 'hsl(215, 25%, 27%)',
          400: 'hsl(215, 20%, 65%)',
          50: 'hsl(210, 40%, 98%)',
        },
        emerald: {
          500: 'hsl(142, 70%, 45%)',
          600: 'hsl(142, 76%, 36%)',
        },
        mint: {
          400: 'hsl(158, 64%, 52%)',
        },
      },
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
