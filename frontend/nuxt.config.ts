// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@primevue/nuxt-module'],
  
  // --- 1. TAILWIND KARANLIK TEMA MOTORU ---
  tailwindcss: {
    config: {
      darkMode: 'class',
    }
  },

  primevue: {
    options: {
      theme: {
        preset: Aura,
        // --- 2. PRIMEVUE BİLEŞENLERİNİN KARANLIK TEMA MOTORU ---
        options: {
          darkModeSelector: '.dark', 
        }
      },
    },
  },
  
  css: ['primeicons/primeicons.css'],
})