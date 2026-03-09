<template>
    <div class="p-6 max-w-[1400px] mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Settings</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage your application preferences and regional settings.</p>
      </div>
  
      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 min-h-[500px]">
        
        <h2 class="text-xl font-bold mb-6 border-b pb-4 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
          Regional Preferences
        </h2>
        
        <div class="max-w-xl flex flex-col gap-5">
          <div>
            <label class="block font-bold text-gray-700 dark:text-gray-300 mb-3">Display Currency</label>
            <Dropdown 
              v-model="localCurrency" 
              :options="currencyOptions" 
              optionLabel="label" 
              optionValue="value" 
              class="w-full p-fluid"
              @change="updateCurrency"
            />
          </div>
          
          <p class="text-sm text-gray-500 dark:text-gray-400 italic mt-2 bg-gray-50 dark:bg-gray-700/50 p-5 rounded-xl border border-gray-100 dark:border-gray-600 leading-relaxed">
            <i class="pi pi-sync mr-2 text-blue-500"></i> Exchange rates are fetched live. When you change your currency, all your dashboard and transaction amounts will instantly update based on the current global market rate.
          </p>
        </div>
  
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, watch } from 'vue'
  import Dropdown from 'primevue/dropdown'
  import { useCurrency } from '~/composables/useCurrency'
  
  definePageMeta({ layout: 'default' })
  
  const { currentCurrency, setCurrency } = useCurrency()
  
  const localCurrency = ref(currentCurrency.value)
  
  const currencyOptions = [
    { label: '🇺🇸 US Dollar ($)', value: 'USD' },
    { label: '🇪🇺 Euro (€)', value: 'EUR' },
    { label: '🇹🇷 Turkish Lira (₺)', value: 'TRY' },
    { label: '🇵🇱 Polish Złoty (zł)', value: 'PLN' }
  ]
  
  const updateCurrency = () => {
    setCurrency(localCurrency.value)
  }
  
  watch(currentCurrency, (newVal) => {
    localCurrency.value = newVal
  })
  </script>