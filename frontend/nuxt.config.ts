// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura'

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },
  modules: ['@nuxtjs/tailwindcss', '@primevue/nuxt-module'],

  // Backend address. Override at runtime with NUXT_PUBLIC_API_BASE.
  // Defaults: local Django in development, the Render backend in production builds.
  runtimeConfig: {
    public: {
      apiBase: process.env.NODE_ENV === 'production'
        ? 'https://smart-finance-app-6lgi.onrender.com'
        : 'http://localhost:8000',
    },
  },

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
