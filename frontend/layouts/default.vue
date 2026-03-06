<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Fixed Sidebar -->
    <aside
      class="fixed left-0 top-0 h-screen w-64 bg-gray-900 text-white z-40 flex flex-col"
    >
      <!-- Logo area (same height as header) -->
      <div class="h-16 flex items-center justify-center border-b border-gray-800">
        <span class="text-xl font-semibold">SmartFinance</span>
      </div>

      <!-- Navigation -->
      <nav class="flex-1 p-4 space-y-1 overflow-y-auto">
        <NuxtLink
          to="/"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-200 hover:bg-gray-800 transition-colors"
          active-class="!bg-gray-800 !text-white"
        >
          <i class="pi pi-home" />
          <span>Dashboard</span>
        </NuxtLink>
        <NuxtLink
          to="/transactions"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-200 hover:bg-gray-800 transition-colors"
          active-class="!bg-gray-800 !text-white"
        >
          <i class="pi pi-wallet" />
          <span>Transactions</span>
        </NuxtLink>
        <NuxtLink
          to="/savings"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-gray-200 hover:bg-gray-800 transition-colors"
          active-class="!bg-gray-800 !text-white"
        >
          <i class="pi pi-chart-line" />
          <span>Savings Goals</span>
        </NuxtLink>
      </nav>
      <div class="p-4 border-t border-gray-800">
        <button
          @click="handleLogout"
          class="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-200 hover:bg-gray-800 transition-colors"
        >
          <i class="pi pi-sign-out" />
          <span>Logout</span>
        </button>
      </div>
    </aside>

    <!-- Header (top bar) -->
    <header
      class="fixed top-0 left-64 right-0 h-16 bg-white shadow flex items-center justify-between px-6 z-30"
    >
      <div class="flex items-center gap-3">
        <span class="text-sm text-gray-500">SmartFinance</span>
      </div>
      <div class="flex items-center gap-3">
        <!-- Placeholder for future actions / profile -->
      </div>
    </header>

    <!-- Main content -->
    <main class="ml-64 mt-16 p-6 h-[calc(100vh-4rem)] overflow-auto">
      <slot />
    </main>

    <ConfirmDialog />
  </div>
</template>

<script setup lang="ts">
import ConfirmDialog from 'primevue/confirmdialog'
const { logout } = useAuth()

const handleLogout = () => {
  logout()
}
</script>
