<template>
  <!-- Fills the layout's main area exactly; only the message list scrolls -->
  <div class="max-w-[1400px] mx-auto flex flex-col h-full min-h-0">
    
    <div class="flex items-center gap-4 mb-6 shrink-0">
      <div class="bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-300 p-3 rounded-2xl transition-colors duration-300 shadow-sm">
        <i class="pi pi-sparkles text-2xl"></i>
      </div>
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">AI Financial Advisor</h1>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1 transition-colors duration-300">Your personal AI assistant for budgets and insights.</p>
      </div>
    </div>

    <div class="card flex flex-col flex-1 min-h-0 bg-white dark:bg-gray-800 rounded-3xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden transition-colors duration-300 relative">
      
      <div class="absolute top-0 right-0 w-64 h-64 bg-purple-400 opacity-[0.03] dark:opacity-[0.05] rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>

      <div 
        ref="chatContainer" 
        class="flex-1 min-h-0 overflow-y-auto overscroll-contain p-4 sm:p-6 space-y-6 scroll-smooth z-10"
      >
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          class="flex w-full"
          :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
        >
          <div v-if="msg.role === 'ai'" class="flex max-w-[80%] md:max-w-[70%] items-end gap-2">
            <div class="w-8 h-8 shrink-0 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center border border-purple-200 dark:border-purple-800">
              <i class="pi pi-sparkles text-purple-600 dark:text-purple-400 text-xs"></i>
            </div>
            <div class="p-4 bg-gray-100 dark:bg-gray-700/60 text-gray-800 dark:text-gray-200 rounded-2xl rounded-bl-none shadow-sm text-[0.95rem] leading-relaxed border border-gray-200 dark:border-gray-600 whitespace-pre-wrap">
              {{ msg.content }}
            </div>
          </div>

          <div v-else class="flex max-w-[80%] md:max-w-[70%] items-end gap-2 justify-end">
            <div class="p-4 bg-purple-600 dark:bg-purple-500 text-white rounded-2xl rounded-br-none shadow-sm text-[0.95rem] leading-relaxed">
              {{ msg.content }}
            </div>
          </div>
        </div>

        <div v-if="isTyping" class="flex max-w-[80%] items-end gap-2">
          <div class="w-8 h-8 shrink-0 rounded-full bg-purple-100 dark:bg-purple-900/50 flex items-center justify-center border border-purple-200 dark:border-purple-800">
            <i class="pi pi-sparkles text-purple-600 dark:text-purple-400 text-xs"></i>
          </div>
          <div class="p-4 bg-gray-100 dark:bg-gray-700/60 rounded-2xl rounded-bl-none shadow-sm border border-gray-200 dark:border-gray-600 flex flex-wrap gap-1.5 items-center min-h-[52px]">
            <span class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
            <span class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
            <span class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
            <span v-if="isSlow" class="ml-2 text-xs text-gray-500 dark:text-gray-400">Still thinking… the AI service is slow right now.</span>
          </div>
        </div>
      </div>

      <div class="p-4 bg-gray-50 dark:bg-gray-900/50 border-t border-gray-100 dark:border-gray-700 z-10 shrink-0">
        <form @submit.prevent="sendMessage" class="flex items-center gap-3 max-w-4xl mx-auto relative">
          <input 
            v-model="userInput" 
            type="text" 
            placeholder="Ask about your spending, budgets, or financial advice..." 
            class="flex-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white rounded-full pl-6 pr-12 py-3.5 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all shadow-sm"
            :disabled="isTyping"
          />
          <button 
            type="submit" 
            :disabled="!userInput.trim() || isTyping"
            class="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 flex items-center justify-center rounded-full bg-purple-600 hover:bg-purple-700 text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <i class="pi pi-send text-sm -ml-0.5 mt-0.5"></i>
          </button>
        </form>
        <p class="text-center text-xs text-gray-500 dark:text-gray-400 mt-3">
          AI Advisor can make mistakes. Consider verifying important financial information.
        </p>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onBeforeUnmount, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'

definePageMeta({ layout: 'default' })

const { user, token } = useAuth()
const { API_BASE } = useApiBase()

// The profile may load after the page; keep the greeting's name up to date
const greeting = () => {
  const name = user.value?.first_name || user.value?.username || 'there'
  return `Hi ${name}! 👋 I'm your SmartFinance AI Assistant.\n\nI can look at your budgets, transactions and recurring payments, or answer general money questions. What would you like to know today?`
}

// Sohbet Geçmişi State'i
const messages = ref([{ role: 'ai', content: greeting() }])
watch(user, () => { messages.value[0].content = greeting() })

const userInput = ref('')
const isTyping = ref(false)
const isSlow = ref(false) // shows a hint when the AI takes long
let slowTimer: ReturnType<typeof setTimeout> | undefined
const chatContainer = ref<HTMLElement | null>(null)

onBeforeUnmount(() => clearTimeout(slowTimer))

// Ekranı otomatik olarak en aşağı kaydıran fonksiyon
const scrollToBottom = async () => {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

// Mesaj Gönderme Fonksiyonu
const sendMessage = async () => {
  if (!userInput.value.trim() || isTyping.value) return

  // 1. Kullanıcının mesajını ekle
  const query = userInput.value
  messages.value.push({ role: 'user', content: query })
  userInput.value = '' // Input'u temizle
  scrollToBottom()

  // 2. Yapay Zekayı "Düşünüyor" moduna al
  isTyping.value = true
  isSlow.value = false
  slowTimer = setTimeout(() => { isSlow.value = true }, 8000)
  scrollToBottom()

  // 3. Soruyu backend'e gönder (Gemini + kullanıcının kendi verileri)
  try {
    const response = await $fetch<{ reply: string }>(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token.value}` },
      body: { prompt: query },
    })
    messages.value.push({ role: 'ai', content: response.reply })
  } catch (error: any) {
    const status = error?.response?.status
    let reply = error?.data?.error || 'The AI assistant is unavailable right now. Please try again later.'
    if (status === 429) reply = "You've reached the hourly question limit. Please try again a bit later. ⏳"
    messages.value.push({ role: 'ai', content: reply })
  } finally {
    clearTimeout(slowTimer)
    isTyping.value = false
    isSlow.value = false
    scrollToBottom()
  }
}

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 10px;
}
.dark ::-webkit-scrollbar-thumb {
  background: #475569;
}
::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>