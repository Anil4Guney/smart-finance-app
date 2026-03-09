import os

# KENDİ GERÇEK ŞİFRENİ BURAYA YAZ (Tırnakları silme)
api_key = "AIzaSyAF9Xm4_eBi55KlehzaUeACkvnn7wE6gBU" 

# Python'a dosyayı en saf ve hatasız formatta (UTF-8) yaratmasını emrediyoruz
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f"GEMINI_API_KEY={api_key}\n")

print("✅ KUSURSUZ .env DOSYASI BAŞARIYLA YARATILDI!")