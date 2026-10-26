<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200">
    <header class="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
      <div class="max-w-3xl mx-auto px-4 h-16 flex items-center justify-between">
        <NuxtLink to="/" class="flex items-center gap-2.5 font-bold text-gray-900 dark:text-white">
          <img src="/icon.svg" alt="" class="w-8 h-8 rounded-lg" />
          SmartFinance
        </NuxtLink>
        <NuxtLink :to="isAuthenticated ? '/settings' : '/login'" class="text-sm font-semibold text-emerald-600 dark:text-emerald-400 hover:underline">
          {{ isAuthenticated ? 'Ayarlara dön' : 'Girişe dön' }}
        </NuxtLink>
      </div>
    </header>

    <main class="max-w-3xl mx-auto px-4 py-8 sm:py-12 policy">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-gray-900 dark:text-white">Gizlilik Politikası</h1>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Son güncelleme: {{ updatedAt }}</p>

      <p class="lead">
        SmartFinance, gelir ve giderlerini takip etmen için bir uygulamadır. Bu sayfa hangi verilerini işlediğimizi,
        neden işlediğimizi, kimlerle paylaştığımızı ve haklarını açıkça anlatır.
      </p>

      <h2>1. Veri sorumlusu</h2>
      <p>
        Verilerini {{ operatorName }} işler (6698 sayılı Kişisel Verilerin Korunması Kanunu kapsamında veri sorumlusu).
        <template v-if="contactEmail">
          Soruların için: <a :href="`mailto:${contactEmail}`">{{ contactEmail }}</a>
        </template>
      </p>

      <h2>2. Hangi verileri işliyoruz?</h2>
      <ul>
        <li><b>Hesap bilgilerin:</b> kullanıcı adı, e-posta, ad ve soyad, şifren (yalnızca geri döndürülemez şekilde şifrelenmiş olarak).</li>
        <li><b>Finansal kayıtların:</b> girdiğin gelir ve giderler, kategoriler, açıklamalar, bütçe limitleri, birikim hedefleri ve tekrarlayan ödemeler (maaş, kira, fatura, abonelik, taksit).</li>
        <li><b>Fiş fotoğrafları:</b> yalnızca "Fiş Tara" özelliğini kullandığında; fotoğraf okunduktan sonra saklanmaz.</li>
        <li><b>Tercihlerin:</b> para birimi ve tema seçimin cihazında saklanır.</li>
      </ul>
      <p>Banka hesaplarına, kartlarına veya şifrelerine erişmeyiz; reklam ve izleme (analitik) araçları kullanmayız.</p>

      <h2>3. Neden ve hangi dayanakla işliyoruz?</h2>
      <p>
        Verilerini yalnızca uygulamayı sana sunmak için işleriz: kayıtlarını göstermek, ay sonu tahminini hesaplamak,
        tekrarlayan ödemeleri otomatik eklemek ve istediğinde yapay zekâ asistanından cevap almak.
        Hukuki dayanak, hesabını oluştururken kurduğun hizmet sözleşmesinin ifasıdır (KVKK m.5/2-c).
      </p>

      <h2>4. Verilerini kimlerle paylaşıyoruz?</h2>
      <p>Hizmeti sunabilmek için şu sağlayıcılar verilerini bizim adımıza işler:</p>
      <ul>
        <li><b>Render</b> (uygulama sunucusu) ve <b>Neon</b> (veritabanı): kayıtların burada saklanır.</li>
        <li><b>Vercel</b>: uygulamanın arayüzünü sunar.</li>
        <li>
          <b>Google (Gemini API):</b> yapay zekâ asistanına soru sorduğunda sorunla birlikte ilgili finansal özetin
          (işlemlerin, bütçelerin, tekrarlayan ödemelerin), "Fiş Tara" kullandığında ise fiş fotoğrafın Google'a gönderilir.
          Google bu verileri kendi koşullarına göre işler. Bu özellikleri kullanmak zorunda değilsin; kullanmazsan hiçbir veri Google'a gitmez.
        </li>
        <li>
          <b>ExchangeRate-API:</b> döviz kurlarını almak için kullanılır; bu servise kişisel verin gönderilmez.
        </li>
      </ul>
      <p>
        Bu sağlayıcıların bir kısmı yurt dışında bulunur; dolayısıyla verilerin yurt dışına aktarılabilir. Verilerini reklam amacıyla
        kimseye satmaz veya kiralamayız.
      </p>

      <h2>5. Ne kadar saklıyoruz?</h2>
      <p>
        Verilerini hesabın açık olduğu sürece saklarız. Hesabını sildiğinde tüm kayıtların da kalıcı olarak silinir.
        Telefonundaki çevrimdışı kopya, çıkış yaptığında silinir.
      </p>

      <h2>6. Haklarını nasıl kullanırsın?</h2>
      <p>KVKK m.11 uyarınca verilerine erişebilir, düzeltilmesini veya silinmesini isteyebilir, işlemeye itiraz edebilirsin. Çoğunu uygulamadan kendin yapabilirsin:</p>
      <ul>
        <li><b>Görüntüle ve düzelt:</b> Profilim ve işlemler sayfaları.</li>
        <li><b>İndir:</b> Ayarlar → Veri ve Gizlilik → "İşlemleri CSV Olarak İndir".</li>
        <li><b>Sil:</b> Ayarlar → Veri ve Gizlilik → "Hesabımı Sil". Silme anında ve geri alınamaz.</li>
      </ul>
      <p v-if="contactEmail">Diğer talepler için <a :href="`mailto:${contactEmail}`">{{ contactEmail }}</a> adresine yazabilirsin.</p>

      <h2>7. Çerezler ve cihazda saklanan veriler</h2>
      <p>
        Yalnızca uygulamanın çalışması için gerekli olanları kullanırız: oturum bilgin (giriş çerezleri), tema ve para birimi tercihin
        ve uygulamanın çevrimdışı açılabilmesi için cihazında tutulan önbellek. İzleme veya reklam çerezi yoktur.
      </p>

      <h2>8. Güvenlik</h2>
      <p>
        Bağlantılar şifrelidir (HTTPS), şifren geri döndürülemez biçimde saklanır, oturum anahtarların kısa ömürlüdür ve çıkış yaptığında geçersiz kılınır.
        Hiçbir sistem tamamen risksiz değildir; bir sorun fark edersen bize bildir.
      </p>

      <h2>9. Değişiklikler</h2>
      <p>Bu politikayı güncellersek bu sayfada yayınlar ve üstteki tarihi değiştiririz.</p>
    </main>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

useHead({ title: 'Gizlilik Politikası · SmartFinance' })

const { isAuthenticated } = useAuth()
const config = useRuntimeConfig()
const contactEmail = String(config.public.contactEmail || '')
const operatorName = String(config.public.operatorName || 'SmartFinance uygulamasının sahibi')
const updatedAt = '26 Ekim 2026'
</script>

<style scoped>
.policy h2 {
  margin-top: 2rem;
  margin-bottom: 0.5rem;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--p-text-color);
}
.policy p,
.policy li {
  line-height: 1.7;
}
.policy p {
  margin-top: 0.6rem;
}
.policy ul {
  margin-top: 0.6rem;
  padding-left: 1.25rem;
  list-style: disc;
}
.policy li {
  margin-top: 0.35rem;
}
.policy .lead {
  margin-top: 1.25rem;
  font-size: 1.05rem;
}
.policy a {
  color: #059669;
  font-weight: 600;
  text-decoration: underline;
}
</style>
