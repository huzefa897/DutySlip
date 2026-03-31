/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js}",  // ← vue instead of jsx
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}