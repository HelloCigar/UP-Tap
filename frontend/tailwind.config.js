/** @type {import('tailwindcss').Config} */
export default {
  content: [],
  theme: {
    extend: {
      colors: {
        red: {
          '50': '#fff1f1',
          '100': '#ffdfe0',
          '200': '#ffc5c6',
          '300': '#ff9c9e',
          '400': '#ff6366',
          '500': '#ff3236',
          '600': '#ef1317',
          '700': '#c90c10',
          '800': '#a60e11',
          '900': '#7b1113',
          '950': '#4b0405',
        }
      },
    },
  },
  plugins: [require('@pinegrow/tailwindcss-plugin').default,],
  get content() {
    const _content = [
      '{.,app,*-layer}/components/**/*.{js,vue,ts}',
      '{.,app,*-layer}/layouts/**/*.vue',
      '{.,app,*-layer}/pages/**/*.vue',
      '{.,app,*-layer}/plugins/**/*.{js,ts}',
      '{.,app,*-layer}/app.vue',
      '{.,app,*-layer}/*.{mjs,js,ts}',
      '{.,*-layer}/nuxt.config.{js,ts}',
    ]
    return process.env.NODE_ENV === 'production'
      ? _content
      : [..._content, './_pginfo/**/*.{html,js}'] // used by Vue Designer Desginer for live-designing during development
  },
}

