# Node.js'in hafif bir sürümünü kullanıyoruz
FROM node:18-alpine

# Çalışma dizini
WORKDIR /app

# Paket dosyalarını kopyala ve kurulum yap
COPY package*.json ./
RUN npm install

# Tüm kodları kopyala
COPY . .

# Nuxt.js'in dışarıdan erişilebilir olması için Host ayarı
ENV HOST=0.0.0.0
ENV PORT=3000

# Portu aç
EXPOSE 3000

# Geliştirme sunucusunu başlat
CMD ["npm", "run", "dev"]