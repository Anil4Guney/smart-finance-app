// https://nuxt.com/docs/api/configuration/nuxt-config
import Aura from '@primeuix/themes/aura'
import { definePreset } from '@primeuix/themes'
import colors from 'tailwindcss/colors'

// One calm "ink" scale for every surface (page, cards, inputs, dialogs)
const ink = {
  0: '#ffffff',
  50: '#f6f7f9',
  100: '#eceef2',
  200: '#dde1e8',
  300: '#c4cad6',
  400: '#8f98ab',
  500: '#667085',
  600: '#4b5567',
  700: '#343d4f',
  800: '#1a2234',
  900: '#0f1626',
  950: '#090e1a',
}

// Aura with a single emerald accent and the ink surfaces
const SmartFinanceTheme = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{emerald.50}', 100: '{emerald.100}', 200: '{emerald.200}', 300: '{emerald.300}',
      400: '{emerald.400}', 500: '{emerald.500}', 600: '{emerald.600}', 700: '{emerald.700}',
      800: '{emerald.800}', 900: '{emerald.900}', 950: '{emerald.950}',
    },
    colorScheme: {
      light: { surface: ink },
      dark: { surface: ink },
    },
  },
})

// Turkish texts for PrimeVue components (calendar, tables, password hints...)
const trLocale = {
  dayNames: ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'],
  dayNamesShort: ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'],
  dayNamesMin: ['Pz', 'Pt', 'Sa', 'Ça', 'Pe', 'Cu', 'Ct'],
  monthNames: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran', 'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'],
  monthNamesShort: ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara'],
  today: 'Bugün',
  clear: 'Temizle',
  weekHeader: 'Hf',
  firstDayOfWeek: 1,
  dateFormat: 'dd.mm.yy',
  weak: 'Zayıf',
  medium: 'Orta',
  strong: 'Güçlü',
  passwordPrompt: 'Bir şifre yaz',
  emptyMessage: 'Sonuç bulunamadı',
  emptyFilterMessage: 'Sonuç bulunamadı',
  emptySearchMessage: 'Sonuç bulunamadı',
  accept: 'Evet',
  reject: 'Hayır',
  apply: 'Uygula',
  cancel: 'Vazgeç',
  aria: {
    trueLabel: 'Doğru',
    falseLabel: 'Yanlış',
    nullLabel: 'Seçilmedi',
    close: 'Kapat',
    previous: 'Önceki',
    next: 'Sonraki',
    navigation: 'Gezinme',
    chooseDate: 'Tarih seç',
    chooseYear: 'Yıl seç',
    chooseMonth: 'Ay seç',
    chooseDecade: 'On yıl seç',
    prevYear: 'Önceki yıl',
    nextYear: 'Sonraki yıl',
    prevMonth: 'Önceki ay',
    nextMonth: 'Sonraki ay',
    prevDecade: 'Önceki on yıl',
    nextDecade: 'Sonraki on yıl',
    star: '1 yıldız',
    stars: '{star} yıldız',
    selectAll: 'Tümü seçildi',
    unselectAll: 'Seçimler kaldırıldı',
    selectRow: 'Satır seçildi',
    unselectRow: 'Satır seçimi kaldırıldı',
  },
}

// Dark theme is the default; this runs before the first paint so there is no white flash
const themeScript =
  "(function(){try{if(localStorage.getItem('theme')!=='light'){document.documentElement.classList.add('dark')}}catch(e){document.documentElement.classList.add('dark')}})()"

export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: false }, // DevTools has an unauthenticated RPC (command execution) while the dev server runs
  modules: ['@nuxtjs/tailwindcss', '@primevue/nuxt-module', '@vite-pwa/nuxt'],

  // The app lives behind a login and talks to a separate API, so it runs fully in the browser.
  // That also lets the installed app open offline from its cached shell.
  ssr: false,
  // Emit the app shell (index.html) so the service worker can open the app offline
  nitro: { prerender: { routes: ['/'] } },

  // Backend address. Override at runtime with NUXT_PUBLIC_API_BASE.
  // Defaults: local Django in development, the Render backend in production builds.
  runtimeConfig: {
    public: {
      apiBase: process.env.NODE_ENV === 'production'
        ? 'https://smart-finance-app-6lgi.onrender.com'
        : 'http://localhost:8000',
    },
  },

  app: {
    head: {
      htmlAttrs: { lang: 'tr' },
      title: 'SmartFinance',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#0f1626' },
        { name: 'description', content: 'Gelir, gider, taksit ve faturalarını tek yerden takip et. Ay sonunu önceden gör.' },
        { name: 'mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-capable', content: 'yes' },
        { name: 'apple-mobile-web-app-title', content: 'SmartFinance' },
      ],
      link: [
        { rel: 'manifest', href: '/manifest.webmanifest' },
        { rel: 'icon', href: '/favicon.ico', sizes: '48x48' },
        { rel: 'icon', href: '/icon.svg', type: 'image/svg+xml', sizes: 'any' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon-180x180.png' },
      ],
      script: [{ innerHTML: themeScript, tagPosition: 'head' }],
    },
  },

  tailwindcss: {
    config: {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['"Inter Variable"', 'Inter', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
          },
          colors: {
            // The old purple accent becomes the emerald accent everywhere
            purple: colors.emerald,
            gray: ink,
          },
        },
      },
    },
  },

  primevue: {
    options: {
      locale: trLocale,
      theme: {
        preset: SmartFinanceTheme,
        options: {
          darkModeSelector: '.dark',
        },
      },
    },
  },

  // Installable app (manifest + service worker)
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'SmartFinance',
      short_name: 'SmartFinance',
      description: 'Gelir, gider, taksit ve faturalarını tek yerden takip et.',
      lang: 'tr',
      dir: 'ltr',
      start_url: '/',
      scope: '/',
      id: '/',
      display: 'standalone',
      orientation: 'portrait',
      theme_color: '#0f1626',
      background_color: '#0f1626',
      categories: ['finance', 'productivity'],
      icons: [
        { src: 'pwa-64x64.png', sizes: '64x64', type: 'image/png' },
        { src: 'pwa-192x192.png', sizes: '192x192', type: 'image/png' },
        { src: 'pwa-512x512.png', sizes: '512x512', type: 'image/png' },
        { src: 'maskable-icon-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
      ],
      shortcuts: [
        { name: 'Yeni işlem', short_name: 'Yeni işlem', url: '/transactions?yeni=1', icons: [{ src: 'pwa-192x192.png', sizes: '192x192' }] },
        { name: 'Yapay zekâ asistanı', short_name: 'Asistan', url: '/advisor', icons: [{ src: 'pwa-192x192.png', sizes: '192x192' }] },
      ],
    },
    workbox: {
      navigateFallback: '/',
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}'],
      cleanupOutdatedCaches: true,
      runtimeCaching: [
        {
          // The user's own data: fresh when online, last known copy when offline.
          // This cache is deleted on logout (see useAuth).
          urlPattern: ({ request, url }: { request: Request; url: URL }) =>
            request.method === 'GET' && /^\/api\/(transactions|subscriptions|savings-goals|budgets|forecast)\/$/.test(url.pathname),
          handler: 'NetworkFirst',
          options: {
            cacheName: 'sf-api',
            networkTimeoutSeconds: 4,
            expiration: { maxEntries: 30, maxAgeSeconds: 60 * 60 * 24 * 7 },
            cacheableResponse: { statuses: [200] },
          },
        },
        {
          // Exchange rates
          urlPattern: /^https:\/\/open\.er-api\.com\/.*/i,
          handler: 'StaleWhileRevalidate',
          options: { cacheName: 'sf-rates', expiration: { maxEntries: 2, maxAgeSeconds: 60 * 60 * 24 } },
        },
      ],
    },
    client: { installPrompt: true },
    devOptions: { enabled: false },
  },

  css: ['@fontsource-variable/inter', 'primeicons/primeicons.css', '~/assets/css/app.css'],
})
