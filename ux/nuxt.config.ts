import svgLoader from 'vite-svg-loader'

export default defineNuxtConfig({
  devtools: { enabled: true },


  app: {
    head: {
      script: [
        { src: 'https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js' },
      ],
    },
    pageTransition: { name: 'page', mode: 'out-in' },
    layoutTransition: { name: 'layout', mode: 'out-in' }, 
  },

  modules: [
    '@pinia/nuxt',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/i18n',
    '@nuxtjs/google-fonts',
    "@nuxt/image"
  ],
  
  i18n: {
    vueI18n: './i18n.config.ts', // if you are using custom path, default 
    defaultLocale: 'es',
    lazy: true,
    strategy: 'no_prefix',
    langDir: './locales',
    locales: [
      { code: 'es', iso: 'es-ES', file: 'es.json', name: 'Español' },
      { code: 'en', iso: 'en-US', file: 'en.json', name: 'English' },
    ],
  },

  pinia: {
  },

  runtimeConfig: {
    public: {
      api: {
        baseUrl: 'http://127.0.0.1:8000',
      },
      version: '0.0.1',
      withDomain: false,
    },
    cyk: 'ctUBG2m9RV8rCSszrmCq6rvuCSwk7xHM9',
  },

  


  googleFonts: {
    families: {
      'IBM Plex Sans': true,
    }
  },

  css: [
    "@/layouts/global.css",
  ],

  vite: {
    css: {
      preprocessorOptions: {
          scss: {
            quietDeps: true,
            additionalData: '@use "@/assets/css/_colors.scss" as *;'
          },
      },
    },
    plugins: [svgLoader()],
  }
})