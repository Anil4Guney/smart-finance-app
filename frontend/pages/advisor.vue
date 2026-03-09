<template>
  <div class="p-6 max-w-[1400px] mx-auto flex flex-col">
    
    <div class="flex items-center gap-4 mb-8">
      <div class="bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-300 p-4 rounded-3xl transition-colors duration-300">
        <i class="pi pi-sparkles text-3xl"></i>
      </div>
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">AI Financial Advisor</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1 transition-colors duration-300">Smart, structured insights powered by Gemini AI</p>
      </div>
    </div>

    <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 relative overflow-hidden flex flex-col min-h-[550px] transition-colors duration-300">
      
      <div class="absolute top-0 right-0 w-64 h-64 bg-purple-400 opacity-[0.03] dark:opacity-[0.05] rounded-full blur-3xl -mr-20 -mt-20"></div>

      <div v-if="pending" class="flex flex-col items-center justify-center flex-grow py-20">
        <i class="pi pi-spin pi-spinner text-6xl text-purple-500 dark:text-purple-400 mb-6"></i>
        <h3 class="text-xl font-bold text-gray-700 dark:text-gray-200">Analyzing your finances...</h3>
      </div>

      <div v-else-if="error" class="text-center flex-col justify-center flex-grow py-16">
        <i class="pi pi-exclamation-triangle text-5xl text-red-500 dark:text-red-400 mb-4"></i>
        <h3 class="text-xl font-bold text-gray-700 dark:text-gray-200">Connection Failed</h3>
        <p class="text-gray-500 dark:text-gray-400 mt-2">{{ error }}</p>
        <Button label="Try Again" icon="pi pi-refresh" class="mt-6" severity="secondary" @click="fetchAdvice" />
      </div>

      <div v-else class="flex flex-col flex-grow z-10">
        
        <div class="mb-10 pb-6 border-b border-gray-100 dark:border-gray-700 transition-colors duration-300">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white transition-colors duration-300">Hey there, superstar! 👋</h2>
          <p class="text-gray-600 dark:text-gray-300 mt-2 text-lg transition-colors duration-300">Here are 3 structured steps to supercharge your financial journey:</p>
        </div>

        <div v-if="adviceArray.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
          
          <div 
            v-for="tip in adviceArray" 
            :key="tip.id" 
            class="flex flex-col p-6 bg-purple-50/50 dark:bg-gray-700/50 rounded-3xl border border-purple-100 dark:border-gray-600 shadow-sm hover:shadow-md transition-all duration-300 group"
          >
            <div class="flex items-center gap-3 mb-4">
              <i class="pi pi-check-circle text-purple-600 dark:text-purple-400 text-xl flex-shrink-0"></i>
              <h4 class="font-bold text-lg text-gray-900 dark:text-white group-hover:text-purple-700 dark:group-hover:text-purple-300 transition-colors duration-300">
                {{ tip.title }}
              </h4>
            </div>
            
            <p class="text-gray-600 dark:text-gray-300 leading-relaxed text-[1.05rem] flex-grow transition-colors duration-300">
              {{ tip.content }}
            </p>
          </div>
        </div>
        
        <div v-else class="text-center py-12 text-gray-500 dark:text-gray-400 flex-grow flex flex-col justify-center items-center">
           <i class="pi pi-inbox text-4xl mb-3"></i>
           <p>No suggestions available at the moment.</p>
        </div>

        <div class="mt-auto pt-6 border-t border-gray-100 dark:border-gray-700 flex items-center justify-between gap-4 transition-colors duration-300">
          <p class="text-gray-600 dark:text-gray-300 font-medium">Keep up the fantastic work! You're doing great! 👍</p>
          <Button label="Get Fresh Advice" icon="pi pi-refresh" severity="help" rounded @click="fetchAdvice" />
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Button from 'primevue/button'

definePageMeta({ layout: 'default' })

const { token } = useAuth()
const API_BASE = 'http://127.0.0.1:8000/api'

// JSON verisini tutacak yeni ref (dizi)
const adviceArray = ref([])
const pending = ref(true)
const error = ref(null)

// API'den tavsiye çeken fonksiyon
const fetchAdvice = async () => {
  pending.value = true
  error.value = null
  adviceArray.value = [] // Önceki tavsiyeleri temizle
  
  try {
    const response = await $fetch(`${API_BASE}/advisor/`, {
      headers: { Authorization: `Bearer ${token.value}` }
    })
    
    try {
      adviceArray.value = JSON.parse(response.advice)
    } catch (parseError) {
      console.error("Yapay zeka geçerli bir JSON döndürmedi:", response.advice)
      error.value = "Yapay zeka yanıtını ayrıştırırken bir hata oluştu. Lütfen tekrar deneyin."
    }
    
  } catch (err) {
    error.value = "Yapay zekaya bağlanırken bir sorun oluştu. API anahtarını kontrol et."
    console.error(err)
  } finally {
    pending.value = false
  }
}

// Sayfa yüklendiğinde analizi başlat
fetchAdvice()
</script>