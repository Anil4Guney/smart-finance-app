<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-surface-900 dark:text-white transition-colors duration-300 flex">
    
    <div 
      v-if="isMobileMenuOpen" 
      @click="isMobileMenuOpen = false" 
      class="fixed inset-0 bg-gray-900/50 dark:bg-black/60 z-40 lg:hidden backdrop-blur-sm transition-opacity"
    ></div>

    <aside 
      :class="isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'"
      class="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 z-50 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0"
    >
      <div class="h-16 flex items-center justify-between px-6 border-b border-gray-200 dark:border-gray-800 transition-colors duration-300 shrink-0">
        <span class="text-2xl font-extrabold text-purple-600 dark:text-purple-400">SmartFinance</span>
        <button @click="isMobileMenuOpen = false" class="lg:hidden text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">
          <i class="pi pi-times text-xl"></i>
        </button>
      </div>

      <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
        <NuxtLink @click="isMobileMenuOpen = false" to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-home text-lg" /> <span>Dashboard</span>
        </NuxtLink>
        <NuxtLink @click="isMobileMenuOpen = false" to="/transactions" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-wallet text-lg" /> <span>Transactions</span>
        </NuxtLink>
        <NuxtLink @click="isMobileMenuOpen = false" to="/savings" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-chart-line text-lg" /> <span>Savings Goals</span>
        </NuxtLink>
        <NuxtLink @click="isMobileMenuOpen = false" to="/subscriptions" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-calendar-clock text-lg"></i> <span>Subscriptions</span>
        </NuxtLink>
        <NuxtLink @click="isMobileMenuOpen = false" to="/advisor" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-sparkles text-lg"></i> <span>AI Advisor</span>
        </NuxtLink>
      </nav>
    </aside>

    <header class="fixed top-0 left-0 lg:left-64 right-0 h-16 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4 lg:px-8 z-30 transition-all duration-300">
      
      <div class="flex items-center gap-4">
        <button @click="isMobileMenuOpen = true" class="lg:hidden p-2 -ml-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors">
          <i class="pi pi-bars text-xl"></i>
        </button>
        <span class="text-xl font-bold text-gray-900 dark:text-white tracking-wide lg:hidden">SmartFinance</span>
      </div>
      
      <div class="hidden lg:flex items-center justify-center absolute left-1/2 -translate-x-1/2">
        <span class="text-xl font-bold text-gray-900 dark:text-white tracking-wide text-center">SmartFinance</span>
      </div>
      
      <div class="flex items-center gap-2 sm:gap-4">
        
        <button @click="toggleDarkMode" class="p-2 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-yellow-400 shadow-sm shrink-0">
          <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'"></i>
        </button>

        <div class="relative shrink-0">
          <button @click="isNotifOpen = !isNotifOpen" class="relative p-2 w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-gray-300 shadow-sm">
            <i class="pi pi-bell text-base sm:text-lg"></i>
            <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-2.5 h-2.5 sm:w-3 sm:h-3 bg-red-500 rounded-full border-2 border-white dark:border-gray-800 animate-pulse"></span>
          </button>

          <div v-if="isNotifOpen" @click="isNotifOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isNotifOpen" class="absolute right-0 sm:-right-2 mt-3 w-[280px] sm:w-80 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50 overflow-hidden transform transition-all duration-200 origin-top-right">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center bg-gray-50 dark:bg-gray-900/50">
              <div class="flex items-center gap-2">
                <h3 class="font-bold text-gray-900 dark:text-white text-sm sm:text-base">Notifications</h3>
                <span v-if="unreadCount > 0" class="text-xs bg-purple-100 text-purple-600 px-2 py-0.5 rounded-md font-bold">{{ unreadCount }} New</span>
              </div>
              <button v-if="unreadCount > 0" @click="markAllAsRead" class="text-xs text-gray-500 hover:text-purple-600 font-medium transition-colors">
                Mark all read
              </button>
            </div>
            
            <div class="max-h-72 overflow-y-auto p-2">
              <div v-if="notifications.length === 0" class="text-center text-gray-500 py-6 text-sm flex flex-col items-center">
                <i class="pi pi-check-circle text-4xl mb-3 text-green-500/50"></i>
                <span class="font-medium text-gray-600 dark:text-gray-400">You're all caught up!</span>
              </div>
              
              <div 
                v-for="notif in notifications" 
                :key="notif.id" 
                class="flex gap-3 p-3 rounded-xl transition-colors group border border-transparent relative mb-1"
                :class="notif.isRead ? 'bg-transparent hover:bg-gray-50 dark:hover:bg-gray-700/50' : 'bg-purple-50/50 dark:bg-purple-900/10 border-purple-100 dark:border-purple-800/30'"
              >
                <div v-if="!notif.isRead" class="absolute top-1/2 -translate-y-1/2 left-1 w-1.5 h-1.5 bg-purple-500 rounded-full"></div>
                <div class="w-8 h-8 sm:w-10 sm:h-10 shrink-0 rounded-full flex items-center justify-center text-base sm:text-lg ml-2" :class="notif.colorClass">
                  <i :class="['pi', notif.icon]"></i>
                </div>
                <div class="flex-1 pr-6">
                  <p class="text-xs sm:text-sm font-bold text-gray-900 dark:text-white" :class="!notif.isRead ? 'opacity-100' : 'opacity-80'">{{ notif.title }}</p>
                  <p class="text-[10px] sm:text-xs text-gray-600 dark:text-gray-400 mt-0.5" :class="!notif.isRead ? 'font-medium' : ''">{{ notif.message }}</p>
                </div>
                <button @click.stop="dismissNotification(notif.id)" class="absolute right-2 top-1/2 -translate-y-1/2 w-6 h-6 sm:w-8 sm:h-8 flex items-center justify-center rounded-full text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 opacity-0 group-hover:opacity-100 transition-all">
                  <i class="pi pi-times text-[10px] sm:text-xs font-bold"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="hidden sm:block w-px h-6 bg-gray-200 dark:bg-gray-700 mx-1"></div>

        <div class="relative shrink-0">
          <div class="flex items-center gap-2 sm:gap-3 cursor-pointer select-none" @click="isProfileOpen = !isProfileOpen">
            <div class="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-300 flex items-center justify-center font-bold border-2 border-transparent hover:border-purple-400 transition-all uppercase text-sm sm:text-base">
              {{ user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U' }}
            </div>
            <div class="hidden md:block text-left max-w-[120px] truncate">
              <p class="text-sm font-bold text-gray-900 dark:text-white leading-tight truncate">
                {{ user?.first_name ? `${user.first_name} ${user.last_name || ''}` : (user?.username || 'Loading...') }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ user?.email || 'No email provided' }}</p>
            </div>
            <i class="hidden sm:block pi pi-angle-down text-gray-500 dark:text-gray-400 transition-transform duration-300" :class="{ 'rotate-180': isProfileOpen }"></i>
          </div>

          <div v-if="isProfileOpen" @click="isProfileOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isProfileOpen" class="absolute right-0 mt-3 w-48 sm:w-56 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50 overflow-hidden transform transition-all duration-200 origin-top-right">
            <div class="p-4 border-b border-gray-100 dark:border-gray-700 md:hidden bg-gray-50 dark:bg-gray-900/50">
               <p class="text-sm font-bold text-gray-900 dark:text-white leading-tight truncate">
                {{ user?.first_name ? `${user.first_name} ${user.last_name || ''}` : (user?.username || 'Loading...') }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate mt-0.5">{{ user?.email || 'No email provided' }}</p>
            </div>
            <div class="p-2">
              <NuxtLink to="/profile" @click="isProfileOpen = false" class="flex items-center gap-3 px-3 py-2 sm:px-4 sm:py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-user text-purple-500"></i> My Profile
              </NuxtLink>
              <NuxtLink to="/settings" @click="isProfileOpen = false" class="flex items-center gap-3 px-3 py-2 sm:px-4 sm:py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-cog text-blue-500"></i> Settings
              </NuxtLink>
              <div class="h-px bg-gray-100 dark:bg-gray-700 my-1"></div>
              <button @click="handleLogout" class="w-full flex items-center gap-3 px-3 py-2 sm:px-4 sm:py-2.5 text-sm font-bold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors">
                <i class="pi pi-sign-out"></i> Logout
              </button>
            </div>
          </div>
        </div>

      </div>
    </header>

    <main class="ml-0 lg:ml-64 mt-16 p-4 sm:p-6 w-full h-[calc(100vh-4rem)] overflow-y-auto overflow-x-hidden bg-gray-50 dark:bg-gray-900 transition-all duration-300">
      <slot />
    </main>

    <Toast />
    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import ConfirmDialog from 'primevue/confirmdialog'
import { ref, onMounted } from 'vue'
import { useSubscriptions } from '~/composables/useSubscriptions'

const { logout, user } = useAuth()
const { notifications, unreadCount, dismissNotification, markAllAsRead } = useSubscriptions() 

const isMobileMenuOpen = ref(false)

const isProfileOpen = ref(false)
const isNotifOpen = ref(false)
const isDark = ref(false)

const handleLogout = () => { logout() }

const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  if (localStorage.getItem('theme') === 'dark') {
    isDark.value = true
    document.documentElement.classList.add('dark')
  }
})
</script>