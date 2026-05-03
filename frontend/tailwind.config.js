/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'spam-red': '#ef4444',
        'ham-green': '#22c55e',
      }
    },
  },
  plugins: [],
}
