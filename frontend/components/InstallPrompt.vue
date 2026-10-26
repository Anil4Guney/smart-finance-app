<template>
  <Transition name="sf-slide">
    <div
      v-if="visible"
      role="dialog"
      aria-label="Uygulamayı yükle"
      class="fixed z-40 left-3 right-3 bottom-28 lg:bottom-6 lg:left-auto lg:right-6 lg:w-96 rounded-2xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-2xl p-4"
    >
      <div class="flex items-start gap-3">
        <img src="/pwa-64x64.png" alt="" class="w-12 h-12 rounded-xl shrink-0" />
        <div class="min-w-0 flex-1">
          <p class="font-bold text-gray-900 dark:text-white">SmartFinance'i telefonuna ekle</p>

          <p v-if="!isIos" class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
            Ana ekrandan tek dokunuşla aç, tam ekranda kullan. Bağlantın olmasa da açılır.
          </p>

          <ol v-else class="text-sm text-gray-600 dark:text-gray-400 mt-1 space-y-1 list-decimal list-inside">
            <li>Safari'de alttaki <i class="pi pi-upload mx-0.5"></i> <b>Paylaş</b> simgesine dokun</li>
            <li><b>Ana Ekrana Ekle</b>'yi seç</li>
            <li><b>Ekle</b>'ye dokun</li>
          </ol>

          <div class="flex items-center gap-2 mt-3">
            <button
              v-if="!isIos"
              type="button"
              class="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold transition-colors"
              @click="install"
            >
              Yükle
            </button>
            <button
              type="button"
              class="px-3 py-2 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              @click="dismiss"
            >
              {{ isIos ? 'Tamam' : 'Şimdi değil' }}
            </button>
          </div>
        </div>
        <button type="button" aria-label="Kapat" class="text-gray-400 hover:text-gray-700 dark:hover:text-white p-1 -mr-1" @click="dismiss">
          <i class="pi pi-times text-sm"></i>
        </button>
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
// Suggests installing the app. Android/desktop Chrome: real install button.
// iPhone/iPad Safari cannot install from a button, so it shows the manual steps.
const DISMISS_KEY = 'pwaInstallDismissedAt'
const SNOOZE_DAYS = 14
const SHOW_AFTER_MS = 20_000

const { $pwa } = useNuxtApp() as any

const visible = ref(false)
const isIos = ref(false)
let timer: ReturnType<typeof setTimeout> | undefined

const isStandalone = () =>
  window.matchMedia('(display-mode: standalone)').matches || (navigator as any).standalone === true

const recentlyDismissed = () => {
  try {
    const at = Number(localStorage.getItem(DISMISS_KEY) || 0)
    return at > 0 && Date.now() - at < SNOOZE_DAYS * 24 * 60 * 60 * 1000
  } catch {
    return false
  }
}

const dismiss = () => {
  visible.value = false
  try { localStorage.setItem(DISMISS_KEY, String(Date.now())) } catch { /* private mode */ }
}

const install = async () => {
  try {
    await $pwa?.install()
  } finally {
    visible.value = false
  }
}

onMounted(() => {
  if (isStandalone() || recentlyDismissed()) return

  const ua = navigator.userAgent
  // iPadOS reports itself as a Mac with touch
  const ios = /iphone|ipad|ipod/i.test(ua) || (ua.includes('Macintosh') && navigator.maxTouchPoints > 1)
  const safari = /safari/i.test(ua) && !/crios|fxios|edgios|chrome|android/i.test(ua)
  isIos.value = ios

  timer = setTimeout(() => {
    if (isStandalone()) return
    if (ios) {
      // Only Safari can add to the home screen on iOS
      visible.value = safari
    } else {
      visible.value = !!$pwa?.showInstallPrompt
    }
  }, SHOW_AFTER_MS)
})

onBeforeUnmount(() => clearTimeout(timer))
</script>

<style scoped>
.sf-slide-enter-active,
.sf-slide-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.sf-slide-enter-from,
.sf-slide-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
