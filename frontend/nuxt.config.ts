// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  devtools: { enabled: true },

  //disable ssr
  ssr: false,

  modules: ['@nuxt/ui', '@pinia/nuxt', 'nuxt-auth-utils', '@pinegrow/nuxt-module', '@nuxt/image'],
  colorMode: {
    preference: 'light'
  },
  pinegrow: {
    liveDesigner: {
      tailwindcss: {
        /* Please ensure that you update the filenames and paths to accurately match those used in your project. */
        configPath: 'tailwind.config.js',
        cssPath: '@/assets/css/tailwind.css',
        // themePath: false, // Set to false so that Design Panel is not used
        // restartOnConfigUpdate: true,
        restartOnThemeUpdate: true,
      },
    },
  },
})