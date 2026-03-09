import { useState } from '#app'
import { computed } from 'vue'
import { useAuth } from '~/composables/useAuth'

export const useSubscriptions = () => {
  const { token } = useAuth()
  const API_BASE = 'http://127.0.0.1:8000/api'

  const subscriptions = useState<any[]>('global_subscriptions', () => [])
  const dismissedNotifs = useState<number[]>('dismissed_notifs', () => [])
  const readNotifs = useState<number[]>('read_notifs', () => [])

  const loadSubscriptions = async () => {
    if (!token.value) return
    try {
      const data = await $fetch<any[]>(`${API_BASE}/subscriptions/`, {
        headers: { Authorization: `Bearer ${token.value}` }
      })
      subscriptions.value = data.map(sub => ({
        id: sub.id,
        name: sub.name,
        amount: Number(sub.amount),
        dueDate: new Date(sub.due_date),
        icon: sub.icon,
        colorClass: sub.color_class
      }))
    } catch (error) {
      console.error("Abonelikler yüklenirken hata oluştu:", error)
    }
  }

  const addSubscription = async (sub: any) => {
    try {
      const newSub = await $fetch<any>(`${API_BASE}/subscriptions/`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token.value}` },
        body: {
          name: sub.name,
          amount: sub.amount,
          due_date: sub.dueDate.toISOString().split('T')[0],
          icon: sub.icon,
          color_class: sub.colorClass,
          is_active: true
        }
      })
      subscriptions.value.push({
        id: newSub.id,
        name: newSub.name,
        amount: Number(newSub.amount),
        dueDate: new Date(newSub.due_date),
        icon: newSub.icon,
        colorClass: newSub.color_class
      })
    } catch (error) {
      console.error("Abonelik kaydedilemedi:", error)
    }
  }

  // YENİ EKLENEN GÜNCELLEME (EDIT) FONKSİYONU
  const updateSubscription = async (id: number, sub: any) => {
    try {
      const updatedSub = await $fetch<any>(`${API_BASE}/subscriptions/${id}/`, {
        method: 'PATCH', // Sadece değişenleri güncellemek için PATCH kullanırız
        headers: { Authorization: `Bearer ${token.value}` },
        body: {
          name: sub.name,
          amount: sub.amount,
          due_date: sub.dueDate.toISOString().split('T')[0]
        }
      })
      
      // Frontend'deki listeyi anında güncelle
      const index = subscriptions.value.findIndex(s => s.id === id)
      if (index !== -1) {
        subscriptions.value[index] = {
          ...subscriptions.value[index], // İkon gibi değişmeyen verileri koru
          name: updatedSub.name,
          amount: Number(updatedSub.amount),
          dueDate: new Date(updatedSub.due_date)
        }
      }
    } catch (error) {
      console.error("Abonelik güncellenemedi:", error)
      alert("Abonelik güncellenirken bir sorun oluştu.")
    }
  }

  const deleteSubscription = async (id: number) => {
    try {
      await $fetch(`${API_BASE}/subscriptions/${id}/`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token.value}` }
      })
      subscriptions.value = subscriptions.value.filter(s => s.id !== id)
    } catch (error) {
      console.error("Abonelik silinemedi:", error)
    }
  }

  const getDaysLeft = (targetDate: string | Date) => {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    const target = new Date(targetDate)
    target.setHours(0, 0, 0, 0)
    const diffTime = target.getTime() - today.getTime()
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  }

  const getRelativeDateString = (date: string | Date) => {
    const days = getDaysLeft(date)
    if (days === 0) return 'Due Today'
    if (days === 1) return 'Due Tomorrow'
    if (days < 0) return `Overdue by ${Math.abs(days)} days`
    return `In ${days} days`
  }

  const notifications = computed(() => {
    return subscriptions.value
      .filter(sub => getDaysLeft(sub.dueDate) <= 1)
      .filter(sub => !dismissedNotifs.value.includes(sub.id))
      .map(sub => ({
        id: sub.id,
        title: `${sub.name} Payment`,
        message: `Your ${sub.name} bill of $${sub.amount} is ${getRelativeDateString(sub.dueDate).toLowerCase()}!`,
        icon: sub.icon,
        colorClass: sub.colorClass,
        isRead: readNotifs.value.includes(sub.id)
      }))
  })

  const unreadCount = computed(() => notifications.value.filter(n => !n.isRead).length)

  const dismissNotification = (id: number) => {
    if (!dismissedNotifs.value.includes(id)) dismissedNotifs.value.push(id)
  }

  const markAllAsRead = () => {
    notifications.value.forEach(notif => {
      if (!readNotifs.value.includes(notif.id)) readNotifs.value.push(notif.id)
    })
  }

  return {
    subscriptions,
    notifications,
    unreadCount,
    getDaysLeft,
    getRelativeDateString,
    loadSubscriptions,
    addSubscription,
    updateSubscription, // DIŞARI AKTARDIK
    deleteSubscription,
    dismissNotification,
    markAllAsRead
  }
}