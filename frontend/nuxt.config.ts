// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  //disable ssr
  ssr: false,

  modules: ['@nuxt/ui', '@pinia/nuxt', 'nuxt-auth-utils', '@nuxt/image'],
  colorMode: {
    preference: 'light'
  },
  build: {
    transpile: ['@vuepic/vue-datepicker']
  },
  devServer: {
    host: '0.0.0.0',
    port: 3000
  }
})