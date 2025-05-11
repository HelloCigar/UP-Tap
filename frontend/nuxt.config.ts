// https://nuxt.com/docs/api/configuration/nuxt-config
import {resolve} from 'pathe'

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
    port: 3000,
    //https: {
		//key: resolve(__dirname, 'localhost-key.pem'),
		//cert: resolve(__dirname, 'localhost.pem')
	//}
  }
})
