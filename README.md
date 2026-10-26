# SmartFinance

Gelir, gider, taksit ve faturalarını tek yerden takip eden, ay sonunu önceden gösteren kişisel finans uygulaması.
Türkçe arayüz, telefona kurulabilir (PWA), yapay zekâ asistanı ve fiş okuma içerir.

**Canlı:** https://smart-finance-app-kohl.vercel.app

## Özellikler

- **Ay sonu tahmini:** şimdiye kadarki gelir/gider + gelecek maaş, kira, fatura, taksit + günlük harcama hızı → ay sonu sonucu ve günlük güvenli harcama
- **Tekrarlayan gelir/gider:** maaş, kira, fatura, abonelik ve taksitler her ay işlemlere otomatik eklenir (taksitte son taksit küsuratı kapatır)
- **Yapay zekâ asistanı:** kendi verilerine bakarak soruları cevaplar (Google Gemini)
- **Fiş tarama:** fişin fotoğrafından tutar, tarih, kategori ve para birimi okunur
- **Çoklu para birimi:** TL, USD, EUR, GBP, PLN; kurlar canlı alınır
- **Bütçe limitleri, birikim hedefleri, CSV dışa aktarma, hesabı silme**
- **PWA:** ana ekrana eklenir, çevrimdışı açılır (son kaydedilen verilerle)

## Teknoloji

| Katman | Teknoloji |
|---|---|
| Ön yüz | Nuxt 3 (tarayıcıda çalışan uygulama), Vue 3, Tailwind CSS, PrimeVue, Chart.js, `@vite-pwa/nuxt` |
| Arka yüz | Django, Django REST Framework, Djoser, SimpleJWT, WhiteNoise, Gunicorn |
| Veritabanı | PostgreSQL (üretim, Neon) / SQLite (yerel) |
| Yapay zekâ | Google Gemini (`google-genai`) |

## Yerelde çalıştırma

Gerekenler: Python 3.12, Node 22.

```bash
# 1) Arka yüz
cd backend
cp .env.example .env          # GEMINI_API_KEY değerini yaz (yapay zekâ için); gerisi yerel için hazır
python -m venv venv && venv\Scripts\activate    # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver     # http://localhost:8000

# 2) Ön yüz (başka bir terminalde)
cd frontend
npm install
npm run dev                    # http://localhost:3000
```

Docker ile: `backend/.env` dosyasını hazırla, sonra `docker-compose up --build`.

Testler: `cd backend && DJANGO_DEBUG=True python manage.py test finance`

## Ortam değişkenleri

Hepsi `backend/.env.example` dosyasında açıklanmıştır. Üretimde **şunlar zorunludur**:

| Değişken | Açıklama |
|---|---|
| `DJANGO_SECRET_KEY` | Uzun, rastgele. Yoksa sunucu başlamaz. |
| `DATABASE_URL` | PostgreSQL adresi. Yoksa SQLite kullanılır ve **her yeniden başlatmada veriler silinir**. |
| `GEMINI_API_KEY` | Yapay zekâ ve fiş tarama için. |

Ön yüz: `NUXT_PUBLIC_API_BASE` (arka yüz adresi, `/api` olmadan), isteğe bağlı `NUXT_PUBLIC_CONTACT_EMAIL` ve
`NUXT_PUBLIC_OPERATOR_NAME` (Gizlilik Politikası sayfasında gösterilir).

## Canlıya alma kontrol listesi

**Render (arka yüz)**
- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command: `gunicorn config.wsgi:application --workers 1 --threads 2 --timeout 120`
- Environment: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `GEMINI_API_KEY`
- İlk istek, ücretsiz planda sunucu uyuduysa 30–60 sn sürebilir.

**Vercel (ön yüz)**
- Root Directory: `frontend`; ek ayar gerekmez (adres koddan gelir).

**Yayından önce**
- Gizlilik Politikası'ndaki bilgileri kendine göre tamamla (`NUXT_PUBLIC_OPERATOR_NAME`, `NUXT_PUBLIC_CONTACT_EMAIL`).
- Gemini ücretsiz kullanımında Google, gönderilen içeriği ürünlerini geliştirmek için kullanabilir. Finansal veri gönderdiğin için
  gerçek kullanıcılar gelmeden **ücretli (faturalandırmalı) Gemini planına** geçmeyi veya politikadaki ifadeyi buna göre güncellemeyi düşün.
- `npm audit` hâlâ 7 uyarı gösterir; hepsi Nuxt 4'e geçişle kapanır (geliştirme araçlarındadır, canlı uygulamayı etkilemez).

## Güvenlik özeti

- Kısa ömürlü (30 dk) erişim anahtarı + dönen yenileme anahtarı; çıkışta sunucuda geçersiz kılınır
- Girişte kullanıcı adı başına deneme sınırı; yapay zekâ uç noktalarında kullanıcı başına ve günlük toplam sınır
- Her kullanıcı yalnızca kendi verisine erişir; hesap silme tüm verileri siler
- HTTPS zorunlu (HSTS), CORS yalnızca kendi ön yüz adresine açık
- Ön yüzde güvenlik başlıkları (CSP, X-Frame-Options, nosniff, Permissions-Policy)
- Gizli anahtarlar yalnızca ortam değişkenlerinde; `.env` dosyaları git'e girmez
