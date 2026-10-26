// frontend/composables/useCurrency.ts
import { ref } from 'vue'

// Küresel (Global) değişkenler: Tüm sayfalar aynı veriyi kullanacak
const currentCurrency = ref('TRY') // Turkish users first; they can switch in Ayarlar
// Approximate rates shown until the live ones arrive (also used if the rate service is down),
// so amounts are never displayed 1:1 in the wrong currency.
const FALLBACK_RATES: Record<string, number> = { USD: 1, EUR: 0.92, TRY: 45, GBP: 0.79, PLN: 3.98 }
const rates = ref<Record<string, number>>({ ...FALLBACK_RATES })
const isReady = ref(false)

// Uygulamada seçilebilen para birimleri
const CURRENCY_OPTIONS = [
  { label: '🇹🇷 Türk Lirası (₺)', short: '₺ TRY', value: 'TRY' },
  { label: '🇺🇸 ABD Doları ($)', short: '$ USD', value: 'USD' },
  { label: '🇪🇺 Euro (€)', short: '€ EUR', value: 'EUR' },
  { label: '🇬🇧 İngiliz Sterlini (£)', short: '£ GBP', value: 'GBP' },
  { label: '🇵🇱 Polonya Zlotisi (zł)', short: 'zł PLN', value: 'PLN' },
]

export const useCurrency = () => {
  // Gerçek Zamanlı Kur API'sinden verileri çeken fonksiyon
  const fetchRates = async () => {
    // Eğer kurları zaten çektiysek, API'yi tekrar yormamak için durdur
    if (isReady.value) return

    try {
      // Tamamen ücretsiz ve şifre gerektirmeyen küresel kur API'si (Merkez: USD)
      const response = await $fetch<any>('https://open.er-api.com/v6/latest/USD')
      rates.value = { ...FALLBACK_RATES, ...response.rates }
      isReady.value = true
    } catch (error) {
      console.error('❌ Kur çekme hatası:', error)
      // İnternet koparsa veya API çökerse diye "Güvenlik Ağı" (Fallback) kurları
      rates.value = { ...FALLBACK_RATES }
      isReady.value = true
    }
  }

  // Tarayıcı açıldığında kullanıcının son seçtiği para birimini hatırla ve kurları çek
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('preferredCurrency')
    if (saved) currentCurrency.value = saved
    fetchRates()
  }

  // Yeni para birimi seçildiğinde bunu sisteme kaydet
  const setCurrency = (currency: string) => {
    currentCurrency.value = currency
    localStorage.setItem('preferredCurrency', currency)
  }

  // Rakamı al, canlı kura göre çarp ve o ülkenin formatında (nokta/virgül) ekrana yaz!
  const formatCurrency = (value: number | string) => {
    const num = typeof value === 'number' ? value : Number(value)
    if (Number.isNaN(num)) return formatCurrency(0)

    // Veritabanındaki parayı (USD) seçilen para birimiyle çarp
    const rate = rates.value[currentCurrency.value] || 1
    const convertedAmount = num * rate

    // Her ülkenin kendi para birimi gösterim stili (Örn: Türkiye için 1.000,00 ₺)
    const locales: Record<string, string> = {
      USD: 'en-US',
      EUR: 'de-DE',
      TRY: 'tr-TR',
      GBP: 'en-GB',
      PLN: 'pl-PL'
    }

    return new Intl.NumberFormat(locales[currentCurrency.value] || 'en-US', {
      style: 'currency',
      currency: currentCurrency.value,
    }).format(convertedAmount)
  }


  // O an seçili olan dövizin USD karşılığını (çarpanını) döndürür
  const getRate = () => {
    return rates.value[currentCurrency.value] || 1
  }

  // Herhangi bir dövizin USD çarpanı (1 USD = ? birim)
  const getRateFor = (code: string) => rates.value[code] || 1

  // Tutarlar veritabanında USD olarak, 2 basamakla saklanır (backend fazlasını reddeder)
  const toUSD = (amount: number, code: string = currentCurrency.value) =>
    Math.round((amount / getRateFor(code)) * 100) / 100

  // USD tutarı seçilen dövize çevirir (form alanlarını doldurmak için)
  const fromUSD = (amount: number | string, code: string = currentCurrency.value) =>
    Math.round(Number(amount) * getRateFor(code) * 100) / 100

  return {
    currentCurrency,
    currencyOptions: CURRENCY_OPTIONS,
    setCurrency,
    formatCurrency,
    getRate,
    getRateFor,
    toUSD,
    fromUSD,
    isReady
  }
}

