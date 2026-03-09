<template>
    <div class="p-6 max-w-[1400px] mx-auto">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-300">My Profile</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and update your personal account information.</p>
      </div>
  
      <div class="card p-8 rounded-3xl shadow-sm bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 transition-colors duration-300 flex flex-col md:flex-row gap-10 items-start min-h-[500px]">
        
        <div class="flex flex-col items-center gap-6 md:w-1/4 border-r-0 md:border-r border-gray-100 dark:border-gray-700 pr-0 md:pr-8">
          
          <div class="w-40 h-40 rounded-full bg-purple-100 dark:bg-purple-900/40 text-purple-600 dark:text-purple-300 flex items-center justify-center font-bold text-6xl border-4 border-white dark:border-gray-800 shadow-md uppercase overflow-hidden relative">
            <img v-if="photoPreview" :src="photoPreview" alt="Profile" class="w-full h-full object-cover" />
            <span v-else>{{ user?.first_name?.charAt(0) || user?.username?.charAt(0) || 'U' }}</span>
          </div>
          
          <div class="flex flex-col gap-3 w-full max-w-[200px]">
            <Button 
              label="Upload Photo" 
              icon="pi pi-camera" 
              severity="secondary" 
              outlined 
              :loading="isUploading"
              @click="triggerUpload" 
              class="w-full"
            />
            <Button 
              v-if="photoPreview"
              label="Remove Photo" 
              icon="pi pi-trash" 
              severity="danger" 
              text 
              @click="removePhoto" 
              class="w-full"
            />
          </div>
          
          <input 
            type="file" 
            ref="fileInput" 
            class="hidden" 
            accept="image/*" 
            @change="handleFileUpload" 
          />
        </div>
        
        <div class="flex-1 w-full pl-0 md:pl-4">
          <h2 class="text-2xl font-bold mb-8 border-b pb-4 border-gray-100 dark:border-gray-700 text-gray-900 dark:text-white transition-colors duration-300">
            Personal Information
          </h2>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div class="flex flex-col gap-3">
              <label class="text-sm font-bold text-gray-500 dark:text-gray-400">First Name</label>
              <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white font-medium text-lg capitalize">
                {{ user?.first_name || 'Not provided' }}
              </div>
            </div>
            
            <div class="flex flex-col gap-3">
              <label class="text-sm font-bold text-gray-500 dark:text-gray-400">Last Name</label>
              <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white font-medium text-lg uppercase">
                {{ user?.last_name || 'Not provided' }}
              </div>
            </div>
            
            <div class="flex flex-col gap-3 md:col-span-2">
              <label class="text-sm font-bold text-gray-500 dark:text-gray-400">Email Address</label>
              <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-2xl border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white font-medium text-lg">
                {{ user?.email || 'Not provided' }}
              </div>
            </div>
          </div>
  
          <div class="mt-10 pt-6 border-t border-gray-100 dark:border-gray-700 flex justify-end">
             <Button label="Edit Profile Details" icon="pi pi-pencil" size="large" @click="openEditDialog" />
          </div>
        </div>
      </div>
  
      <Dialog v-model:visible="showEditDialog" modal header=" Edit Profile Details" :style="{ width: '450px' }">
        <form @submit.prevent="saveProfile" class="flex flex-col gap-5 pt-4">
          
          <div class="flex flex-col gap-2">
            <label for="editFirstName" class="font-bold text-gray-700 dark:text-gray-300">First Name</label>
            <InputText id="editFirstName" v-model="editForm.first_name" class="w-full" placeholder="Enter your first name" />
          </div>
  
          <div class="flex flex-col gap-2">
            <label for="editLastName" class="font-bold text-gray-700 dark:text-gray-300">Last Name</label>
            <InputText id="editLastName" v-model="editForm.last_name" class="w-full" placeholder="Enter your last name" />
          </div>
  
          <div class="flex flex-col gap-2">
            <label for="editEmail" class="font-bold text-gray-700 dark:text-gray-300">Email Address</label>
            <InputText id="editEmail" v-model="editForm.email" type="email" class="w-full" placeholder="Enter your email" />
          </div>
  
          <div class="flex justify-end gap-3 mt-4">
            <Button type="button" label="Cancel" severity="secondary" text @click="showEditDialog = false" />
            <Button type="submit" label="Save Changes" icon="pi pi-check" :loading="isSavingProfile" />
          </div>
        </form>
      </Dialog>
  
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref } from 'vue'
  import Button from 'primevue/button'
  import Dialog from 'primevue/dialog'
  import InputText from 'primevue/inputtext'
  import { useAuth } from '~/composables/useAuth'
  
  definePageMeta({ layout: 'default' })
  
  // 'user' objesini useAuth'tan alıyoruz.
  const { user } = useAuth()
  
  // --- PROFİL DÜZENLEME İŞLEMLERİ ---
  const showEditDialog = ref(false)
  const isSavingProfile = ref(false)
  const editForm = ref({
    first_name: '',
    last_name: '',
    email: ''
  })
  
  const openEditDialog = () => {
    editForm.value = {
      first_name: user.value?.first_name || '',
      last_name: user.value?.last_name || '',
      email: user.value?.email || ''
    }
    showEditDialog.value = true
  }
  
  // SİHİRLİ GÜNCELLEME FONKSİYONU
  const saveProfile = () => {
    isSavingProfile.value = true
    
    // 1 saniyelik sahte yükleme sonrası veriyi HAFIZADA güncelliyoruz
    setTimeout(() => {
      // BURASI ÖNEMLİ: useAuth'taki user verisini doğrudan güncelliyoruz.
      // Bu sayede sağ üst köşedeki isim ve profil kartındaki veriler anında değişir.
      if (user.value) {
        user.value.first_name = editForm.value.first_name
        user.value.last_name = editForm.value.last_name
        user.value.email = editForm.value.email
      }
      
      isSavingProfile.value = false
      showEditDialog.value = false
      // Eski alert mesajı kaldırıldı!
    }, 800)
  }
  
  // --- FOTOĞRAF İŞLEMLERİ ---
  const fileInput = ref<HTMLInputElement | null>(null)
  const photoPreview = ref<string | null>(null)
  const isUploading = ref(false)
  
  const triggerUpload = () => {
    fileInput.value?.click()
  }
  
  const handleFileUpload = async (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return
  
    photoPreview.value = URL.createObjectURL(file)
    isUploading.value = true
  
    setTimeout(() => {
      isUploading.value = false
    }, 800)
    target.value = '' 
  }
  
  const removePhoto = () => {
    photoPreview.value = null
    if (fileInput.value) {
      fileInput.value.value = '' 
    }
  }
  </script>