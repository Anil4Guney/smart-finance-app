<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white transition-colors duration-300 flex">

    <div
      v-if="isMobileMenuOpen"
      @click="isMobileMenuOpen = false"
      class="fixed inset-0 bg-gray-950/60 z-40 lg:hidden backdrop-blur-sm transition-opacity"
    ></div>

    <aside
      :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
      class="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 z-50 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0"
    >
      <div class="h-16 flex items-center justify-between px-6 border-b border-gray-200 dark:border-gray-800 shrink-0">
        <span class="flex items-center gap-2.5 text-xl font-extrabold tracking-tight text-gray-900 dark:text-white">
          <img src="/icon.svg" alt="" class="w-8 h-8 rounded-xl shadow-lg shadow-emerald-900/30" />
          SmartFinance
        </span>
        <button @click="isMobileMenuOpen = false" aria-label="Menüyü kapat" class="lg:hidden text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
          <i class="pi pi-times text-xl"></i>
        </button>
      </div>

      <nav class="flex-1 p-4 space-y-1.5 overflow-y-auto">
        <NuxtLink
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          @click="isMobileMenuOpen = false"
          class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium"
          active-class="!bg-emerald-50 !text-emerald-700 dark:!bg-emerald-500/10 dark:!text-emerald-400"
        >
          <i :class="['pi', item.icon, 'text-lg']" /> <span>{{ item.label }}</span>
        </NuxtLink>
      </nav>

      <p class="px-6 py-4 text-xs text-gray-400 dark:text-gray-500 border-t border-gray-200 dark:border-gray-800">
        Verilerin yalnızca sana aittir.
      </p>
    </aside>

    <header class="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-white/90 dark:bg-gray-950/90 backdrop-blur border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 lg:px-8 z-30">

      <div class="flex items-center gap-3">
        <button @click="isMobileMenuOpen = true" aria-label="Menüyü aç" class="lg:hidden p-2 -ml-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
          <i class="pi pi-bars text-xl"></i>
        </button>
        <span class="text-lg font-bold text-gray-900 dark:text-white tracking-tight lg:hidden">SmartFinance</span>
      </div>

      <div class="flex items-center gap-2 sm:gap-3">

        <button @click="toggleDarkMode" :aria-label="isDark ? 'Açık temaya geç' : 'Koyu temaya geç'" class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-amber-300 shrink-0">
          <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'"></i>
        </button>

        <div class="relative shrink-0">
          <button @click="isNotifOpen = !isNotifOpen" aria-label="Bildirimler" class="relative w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-gray-300">
            <i class="pi pi-bell text-base sm:text-lg"></i>
            <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-2.5 h-2.5 bg-rose-500 rounded-full border-2 border-white dark:border-gray-800 animate-pulse"></span>
          </button>

          <div v-if="isNotifOpen" @click="isNotifOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isNotifOpen" class="absolute right-0 mt-3 w-[min(20rem,calc(100vw-2rem))] bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50 overflow-hidden origin-top-right">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900/50">
              <div class="flex items-center gap-2">
                <h3 class="font-bold text-gray-900 dark:text-white text-sm sm:text-base">Bildirimler</h3>
                <span v-if="unreadCount > 0" class="text-xs bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300 px-2 py-0.5 rounded-md font-bold">{{ unreadCount }} yeni</span>
              </div>
              <button v-if="unreadCount > 0" @click="markAllAsRead" class="text-xs text-gray-500 hover:text-emerald-600 font-medium transition-colors">
                Hepsini okundu yap
              </button>
            </div>

            <div class="max-h-72 overflow-y-auto p-2">
              <div v-if="notifications.length === 0" class="text-center text-gray-500 py-6 text-sm flex flex-col items-center">
                <i class="pi pi-check-circle text-4xl mb-3 text-emerald-500/50"></i>
                <span class="font-medium text-gray-600 dark:text-gray-400">Her şey yolunda, yaklaşan ödeme yok.</span>
              </div>

              <div
                v-for="notif in notifications"
                :key="notif.id"
                class="flex gap-3 p-3 rounded-xl transition-colors group border border-transparent relative mb-1"
                :class="notif.isRead ? 'bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50' : 'bg-emerald-50/60 dark:bg-emerald-500/10 border-emerald-100 dark:border-emerald-500/20'"
              >
                <div v-if="!notif.isRead" class="absolute top-1/2 -translate-y-1/2 left-1 w-1.5 h-1.5 bg-emerald-500 rounded-full"></div>
                <div class="w-8 h-8 sm:w-10 sm:h-10 shrink-0 rounded-full flex items-center justify-center text-base sm:text-lg ml-2" :class="notif.colorClass">
                  <i :class="['pi', notif.icon]"></i>
                </div>
                <div class="flex-1 pr-6">
                  <p class="text-xs sm:text-sm font-bold text-gray-900 dark:text-white">{{ notif.title }}</p>
                  <p class="text-[11px] sm:text-xs text-gray-600 dark:text-gray-400 mt-0.5">{{ notif.message }}</p>
                </div>
                <button @click.stop="dismissNotification(notif.id)" aria-label="Kaldır" class="absolute right-2 top-1/2 -translate-y-1/2 w-7 h-7 flex items-center justify-center rounded-full text-gray-400 hover:text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30 sm:opacity-0 group-hover:opacity-100 transition-all">
                  <i class="pi pi-times text-xs"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="hidden sm:block w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1"></div>

        <div class="relative shrink-0">
          <button class="flex items-center gap-2 sm:gap-3 select-none" @click="isProfileOpen = !isProfileOpen" aria-label="Hesap menüsü">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-emerald-100 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 flex items-center justify-center font-bold uppercase text-sm sm:text-base">
              {{ user?.first_name?.charAt(0) || user?.username?.charAt(0) || '?' }}
            </div>
            <div class="hidden md:block text-left max-w-[140px]">
              <p class="text-sm font-bold text-gray-900 dark:text-white leading-tight truncate">{{ displayName }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ user?.email || 'E-posta eklenmemiş' }}</p>
            </div>
            <i class="hidden sm:block pi pi-angle-down text-gray-500 dark:text-gray-400 transition-transform duration-300" :class="{ 'rotate-180': isProfileOpen }"></i>
          </button>

          <div v-if="isProfileOpen" @click="isProfileOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isProfileOpen" class="absolute right-0 mt-3 w-56 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50 overflow-hidden origin-top-right">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 md:hidden bg-gray-50 dark:bg-gray-900/50">
              <p class="text-sm font-bold text-gray-900 dark:text-white leading-tight truncate">{{ displayName }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ user?.email || 'E-posta eklenmemiş' }}</p>
            </div>
            <div class="p-2">
              <NuxtLink to="/profile" @click="isProfileOpen = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-user text-emerald-500"></i> Profilim
              </NuxtLink>
              <NuxtLink to="/settings" @click="isProfileOpen = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-cog text-gray-400"></i> Ayarlar
              </NuxtLink>
              <div class="h-px bg-gray-100 dark:bg-gray-700 my-1"></div>
              <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-semibold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-colors">
                <i class="pi pi-sign-out"></i> Çıkış yap
              </button>
            </div>
          </div>
        </div>

      </div>
    </header>

    <!-- Offline strip: the app keeps working with the last saved data -->
    <div
      v-if="!isOnline"
      role="status"
      class="fixed top-16 left-0 lg:left-64 right-0 z-20 bg-amber-500 text-amber-950 text-xs sm:text-sm font-semibold text-center px-3 py-1.5 flex items-center justify-center gap-2"
    >
      <i class="pi pi-wifi text-sm"></i>
      Çevrimdışısın. Son kaydedilen veriler gösteriliyor; yeni kayıtlar için bağlantı gerekir.
    </div>

    <main class="app-main ml-0 lg:ml-64 mt-16 p-4 sm:p-6 pb-28 lg:pb-6 w-full overflow-y-auto overflow-x-hidden bg-gray-50 dark:bg-gray-900">
      <slot />
    </main>

    <InstallPrompt />

    <!-- Phones and tablets: thumb-reach navigation with a quick "add" button -->
    <nav
      class="bottom-nav lg:hidden fixed bottom-0 inset-x-0 z-30 bg-white/95 dark:bg-gray-950/95 backdrop-blur border-t border-gray-200 dark:border-gray-800"
      aria-label="Ana menü"
    >
      <div class="grid grid-cols-5 items-end max-w-xl mx-auto px-2 pt-1.5 pb-1.5">
        <NuxtLink
          v-for="item in bottomLeft"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center gap-0.5 py-1.5 text-[11px] font-medium text-gray-500 dark:text-gray-400"
          active-class="!text-emerald-600 dark:!text-emerald-400"
        >
          <i :class="['pi', item.icon, 'text-xl']"></i>
          {{ item.short }}
        </NuxtLink>

        <NuxtLink
          to="/transactions?yeni=1"
          aria-label="Yeni işlem ekle"
          class="flex justify-center -mt-6"
        >
          <span class="w-14 h-14 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 text-white flex items-center justify-center shadow-lg shadow-emerald-700/40 ring-4 ring-white dark:ring-gray-950 active:scale-95 transition-transform">
            <i class="pi pi-plus text-xl"></i>
          </span>
        </NuxtLink>

        <NuxtLink
          v-for="item in bottomRight"
          :key="item.to"
          :to="item.to"
          class="flex flex-col items-center gap-0.5 py-1.5 text-[11px] font-medium text-gray-500 dark:text-gray-400"
          active-class="!text-emerald-600 dark:!text-emerald-400"
        >
          <i :class="['pi', item.icon, 'text-xl']"></i>
          {{ item.short }}
        </NuxtLink>
      </div>
    </nav>

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import ConfirmDialog from 'primevue/confirmdialog'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useSubscriptions } from '~/composables/useSubscriptions'

const { logout, user } = useAuth()
const { notifications, unreadCount, dismissNotification, markAllAsRead } = useSubscriptions()

const navItems = [
  { to: '/', icon: 'pi-home', label: 'Panel', short: 'Panel' },
  { to: '/transactions', icon: 'pi-wallet', label: 'İşlemler', short: 'İşlemler' },
  { to: '/savings', icon: 'pi-chart-line', label: 'Birikim Hedefleri', short: 'Birikim' },
  { to: '/subscriptions', icon: 'pi-calendar-clock', label: 'Tekrarlayanlar', short: 'Tekrarlayan' },
  { to: '/advisor', icon: 'pi-sparkles', label: 'Yapay Zekâ Asistanı', short: 'Asistan' },
]
const bottomLeft = [navItems[0], navItems[1]]
const bottomRight = [navItems[3], navItems[4]]

const isMobileMenuOpen = ref(false)
const isProfileOpen = ref(false)
const isNotifOpen = ref(false)
const isDark = ref(true)
const isOnline = ref(true)
const syncOnline = () => { isOnline.value = navigator.onLine }

const displayName = computed(() =>
  user.value?.first_name
    ? `${user.value.first_name} ${user.value.last_name || ''}`.trim()
    : (user.value?.username || '...'))

const handleLogout = () => { logout() }

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  document.documentElement.classList.toggle('dark', isDark.value)
  try { localStorage.setItem('theme', isDark.value ? 'dark' : 'light') } catch { /* private mode */ }
}

// The head script already applied the saved theme (dark by default); just mirror it
onMounted(() => {
  isDark.value = document.documentElement.classList.contains('dark')
  syncOnline()
  window.addEventListener('online', syncOnline)
  window.addEventListener('offline', syncOnline)
})

onBeforeUnmount(() => {
  window.removeEventListener('online', syncOnline)
  window.removeEventListener('offline', syncOnline)
})
</script>
