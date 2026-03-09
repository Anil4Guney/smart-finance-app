<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-surface-900 dark:text-white transition-colors duration-300 flex">
    
    <aside class="fixed left-0 top-0 h-screen w-64 bg-white dark:bg-gray-950 border-r border-gray-200 dark:border-gray-800 z-40 flex flex-col transition-colors duration-300">
      <div class="h-16 flex items-center justify-center border-b border-gray-200 dark:border-gray-800 transition-colors duration-300">
        <span class="text-2xl font-extrabold text-purple-600 dark:text-purple-400">SmartFinance</span>
      </div>

      <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
        <NuxtLink to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-home text-lg" /> <span>Dashboard</span>
        </NuxtLink>
        <NuxtLink to="/transactions" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-wallet text-lg" /> <span>Transactions</span>
        </NuxtLink>
        <NuxtLink to="/savings" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-chart-line text-lg" /> <span>Savings Goals</span>
        </NuxtLink>
        <NuxtLink to="/advisor" class="flex items-center gap-3 px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors font-medium" active-class="!bg-purple-50 !text-purple-600 dark:!bg-purple-900/30 dark:!text-purple-400">
          <i class="pi pi-sparkles text-lg"></i> <span>AI Advisor</span>
        </NuxtLink>
      </nav>
    </aside>

    <header class="fixed top-0 left-64 right-0 h-16 bg-white dark:bg-gray-950 border-b border-gray-200 dark:border-gray-800 grid grid-cols-3 items-center px-8 z-30 transition-colors duration-300">
      <div class="flex items-center justify-start"></div>
      
      <div class="flex items-center justify-center">
        <span class="text-xl font-bold text-gray-900 dark:text-white tracking-wide text-center">SmartFinance</span>
      </div>
      
      <div class="flex items-center justify-end gap-5">
        <button @click="toggleDarkMode" class="p-2 w-10 h-10 rounded-full bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center justify-center text-gray-600 dark:text-yellow-400 shadow-sm">
          <i :class="isDark ? 'pi pi-sun' : 'pi pi-moon'"></i>
        </button>

        <div class="w-px h-8 bg-gray-200 dark:bg-gray-700"></div>

        <div class="relative">
          <div class="flex items-center gap-3 cursor-pointer select-none" @click="isProfileOpen = !isProfileOpen">
            <div class="w-10 h-10 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-300 flex items-center justify-center font-bold border-2 border-transparent hover:border-purple-400 transition-all uppercase">
              {{ user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U' }}
            </div>
            
            <div class="hidden md:block text-left">
              <p class="text-sm font-bold text-gray-900 dark:text-white leading-tight">
                {{ user?.first_name ? `${user.first_name} ${user.last_name || ''}` : (user?.username || 'Loading...') }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                {{ user?.email || 'No email provided' }}
              </p>
            </div>
            <i class="pi pi-angle-down text-gray-500 dark:text-gray-400 transition-transform duration-300" :class="{ 'rotate-180': isProfileOpen }"></i>
          </div>

          <div v-if="isProfileOpen" @click="isProfileOpen = false" class="fixed inset-0 z-40"></div>

          <div v-if="isProfileOpen" class="absolute right-0 mt-3 w-56 bg-white dark:bg-gray-800 rounded-2xl shadow-xl border border-gray-100 dark:border-gray-700 z-50 overflow-hidden transform transition-all duration-200 origin-top-right">
            <div class="p-2">
              <NuxtLink to="/profile" @click="isProfileOpen = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-user text-purple-500"></i> My Profile
              </NuxtLink>
              <NuxtLink to="/settings" @click="isProfileOpen = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700/50 rounded-xl transition-colors">
                <i class="pi pi-cog text-blue-500"></i> Settings
              </NuxtLink>
              <div class="h-px bg-gray-100 dark:bg-gray-700 my-1"></div>
              <button @click="handleLogout" class="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-xl transition-colors">
                <i class="pi pi-sign-out"></i> Logout
              </button>
            </div>
          </div>
        </div>

      </div>
    </header>

    <main class="ml-64 mt-16 p-6 w-full h-[calc(100vh-4rem)] overflow-auto bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      <slot />
    </main>

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import ConfirmDialog from 'primevue/confirmdialog'
import { ref, onMounted } from 'vue'

// YENİ: user değişkenini useAuth içinden çektik!
const { logout, user } = useAuth()
const isProfileOpen = ref(false)
const isDark = ref(false)

const handleLogout = () => {
  logout()
}

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