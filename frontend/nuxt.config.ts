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

  app: {
    head: {
      htmlAttrs: { lang: 'tr' },
      title: 'SmartFinance',
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, viewport-fit=cover' },
        { name: 'theme-color', content: '#0f1626' },
        { name: 'description', content: 'Gelir, gider, taksit ve faturalarını tek yerden takip et. Ay sonunu önceden gör.' },
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

  css: ['@fontsource-variable/inter', 'primeicons/primeicons.css', '~/assets/css/app.css'],
})
