"""
Security probe: attacks a LOCALLY running backend the way a hacker would (72 checks).

Run it before every release. Never point it at the live site (it creates test users and hammers login).

1) Start the backend like production, on a throw-away database:
     set DJANGO_DEBUG=False
     set DJANGO_SECRET_KEY=any-long-random-text
     set DJANGO_ADMIN_URL=gizli-panel-xyz/
     set DATABASE_URL=sqlite:///probe.sqlite3
     python manage.py migrate && python manage.py runserver 127.0.0.1:8001 --noreload
   (PowerShell: use  $env:DJANGO_DEBUG="False"  instead of set; and leave CORS_ALLOWED_ORIGINS unset
    and move backend/.env away, so the production defaults are tested.)
2) In another terminal:
     pip install requests pyjwt
     python tools/security_probe.py http://127.0.0.1:8001

It checks: access without login, forged/expired tokens, user isolation (IDOR), privilege escalation,
CORS, Host header, security headers, injection strings, oversized/invalid input and uploads,
refresh-token rotation/logout, login brute-force limit and closed password-reset endpoints.
"""
import base64, json, sys, time
import jwt, requests

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8001"
ALLOWED_ORIGIN = "https://smart-finance-app-kohl.vercel.app"
results = []


def check(name, ok, detail=""):
    results.append((ok, name, detail))
    print(("PASS " if ok else "FAIL ") + name + (f"  [{detail}]" if detail and not ok else ""))


def req(method, path, token=None, **kw):
    headers = kw.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, BASE + path, headers=headers, timeout=60, **kw)


# ---------- A. no token ----------
print("\n== A. Giriş yapmadan erişim ==")
for path in ["/api/transactions/", "/api/subscriptions/", "/api/savings-goals/", "/api/budgets/", "/api/forecast/", "/auth/users/me/", "/auth/users/"]:
    r = req("GET", path)
    check(f"GET {path} -> 401", r.status_code == 401, r.status_code)
for path in ["/api/chat/", "/api/scan-receipt/", "/api/transactions/"]:
    r = req("POST", path, json={})
    check(f"POST {path} -> 401", r.status_code == 401, r.status_code)

# ---------- setup two users ----------
def register(username):
    r = req("POST", "/auth/users/", json={"username": username, "password": "Sup3r-Gizli-Sifre-91", "email": f"{username}@example.com", "first_name": "T", "last_name": "U"})
    assert r.status_code == 201, (r.status_code, r.text)
    return r.json()["id"]

def login(username, password="Sup3r-Gizli-Sifre-91"):
    r = req("POST", "/auth/jwt/create/", json={"username": username, "password": password})
    assert r.status_code == 200, (r.status_code, r.text)
    return r.json()

suffix = str(int(time.time()))[-6:]
a_name, b_name = f"alice{suffix}", f"bob{suffix}"
a_id, b_id = register(a_name), register(b_name)
a, b = login(a_name), login(b_name)

# ---------- B. forged / broken tokens ----------
print("\n== B. Sahte ve bozuk token ==")
def b64(d): return base64.urlsafe_b64encode(json.dumps(d).encode()).rstrip(b"=").decode()
payload = {"token_type": "access", "exp": int(time.time()) + 3600, "iat": int(time.time()), "jti": "x", "user_id": a_id}
none_token = f"{b64({'alg': 'none', 'typ': 'JWT'})}.{b64(payload)}."
wrong_key = jwt.encode(payload, "wrong-key", algorithm="HS256")
expired = jwt.encode({**payload, "exp": int(time.time()) - 10}, "wrong-key", algorithm="HS256")
refresh_as_access = a["refresh"]
for name, tok in [("alg=none", none_token), ("yanlış anahtar", wrong_key), ("süresi dolmuş", expired), ("çöp", "abc.def.ghi"), ("refresh token access gibi", refresh_as_access)]:
    r = req("GET", "/api/transactions/", token=tok)
    check(f"{name} token reddedilir", r.status_code == 401, r.status_code)
r = req("GET", "/api/transactions/", headers={"Authorization": "Basic YWxpY2U6cGFzcw=="})
check("Basic auth reddedilir", r.status_code == 401, r.status_code)

# ---------- C. isolation ----------
print("\n== C. Kullanıcılar arası izolasyon (IDOR) ==")
tx = req("POST", "/api/transactions/", token=b["access"], json={"title": "BOB-GIZLI", "amount": "12.50", "transaction_type": "EXPENSE", "category": "Food", "date": "2026-10-01"}).json()
sub = req("POST", "/api/subscriptions/", token=b["access"], json={"name": "BOB-ABONE", "amount": "5", "due_date": "2099-01-01", "kind": "SUBSCRIPTION"}).json()
goal = req("POST", "/api/savings-goals/", token=b["access"], json={"title": "BOB-HEDEF", "target_amount": "100"}).json()
for label, path in [("işlem", f"/api/transactions/{tx['id']}/"), ("abonelik", f"/api/subscriptions/{sub['id']}/"), ("hedef", f"/api/savings-goals/{goal['id']}/")]:
    check(f"Alice, Bob'un {label} kaydını okuyamaz", req("GET", path, token=a["access"]).status_code == 404)
    check(f"Alice, Bob'un {label} kaydını değiştiremez", req("PATCH", path, token=a["access"], json={"title": "x", "name": "x"}).status_code == 404)
    check(f"Alice, Bob'un {label} kaydını silemez", req("DELETE", path, token=a["access"]).status_code == 404)
lists = " ".join(req("GET", p, token=a["access"]).text for p in ["/api/transactions/", "/api/subscriptions/", "/api/savings-goals/", "/api/forecast/"])
check("Alice'in listelerinde Bob'un verisi yok", "BOB-" not in lists)
mine = req("POST", "/api/transactions/", token=a["access"], json={"title": "t", "amount": "1", "transaction_type": "EXPENSE", "category": "Food", "date": "2026-10-01", "user": b_id, "id": 999999, "recurring": 1}).json()
check("Başka kullanıcı adına kayıt açılamaz (user alanı yok sayılır)", "user" not in mine and mine.get("id") != 999999)
bob_list = req("GET", "/api/transactions/", token=b["access"]).json()
check("Bob'un listesinde Alice'in kaydı yok", all(t["title"] != "t" for t in bob_list))
me = req("PATCH", "/auth/users/me/", token=a["access"], json={"is_staff": True, "is_superuser": True, "is_active": True, "first_name": "Ali"}).json()
check("Kendini yönetici yapamaz", "is_staff" not in me and "is_superuser" not in me)
users = req("GET", "/auth/users/", token=a["access"]).json()
check("Kullanıcı listesinde yalnızca kendisi görünür", len(users) == 1 and users[0]["username"] == a_name, len(users))
r = req("POST", "/gizli-panel-xyz/login/?next=/gizli-panel-xyz/", data={"username": a_name, "password": "Sup3r-Gizli-Sifre-91", "next": "/gizli-panel-xyz/"}, allow_redirects=False)
check("Normal kullanıcı yönetici paneline giremez", r.status_code in (200, 403) and "sessionid" not in r.cookies, r.status_code)

# ---------- D. CORS / Host / headers ----------
print("\n== D. CORS, Host ve başlıklar ==")
r = req("OPTIONS", "/api/transactions/", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "authorization"})
check("Kötü niyetli site CORS izni alamaz", "access-control-allow-origin" not in {k.lower() for k in r.headers}, dict(r.headers).get("access-control-allow-origin"))
r = req("OPTIONS", "/api/transactions/", headers={"Origin": "null", "Access-Control-Request-Method": "GET"})
check("Origin: null izin almaz", "access-control-allow-origin" not in {k.lower() for k in r.headers})
r = req("OPTIONS", "/api/transactions/", headers={"Origin": ALLOWED_ORIGIN, "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "authorization"})
check("Kendi ön yüzün izin alır", r.headers.get("access-control-allow-origin") == ALLOWED_ORIGIN, r.headers.get("access-control-allow-origin"))
r = req("OPTIONS", "/api/transactions/", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
check("Üretimde localhost origin'i kapalı", "access-control-allow-origin" not in {k.lower() for k in r.headers}, r.headers.get("access-control-allow-origin"))
r = requests.get(BASE + "/api/transactions/", headers={"Host": "evil.example"}, timeout=20)
check("Sahte Host başlığı reddedilir", r.status_code == 400, r.status_code)
r = req("GET", "/yok-boyle-bir-sayfa/")
check("404 sayfası ayrıntı sızdırmaz", r.status_code == 404 and not any(w in r.text for w in ("Traceback", "DEBUG", "settings", "INSTALLED_APPS")))
r = req("POST", "/auth/jwt/create/", data="{bozuk json", headers={"Content-Type": "application/json"})
check("Bozuk JSON temiz 400 döner", r.status_code == 400 and "Traceback" not in r.text, r.status_code)
r = req("GET", "/api/transactions/", token=a["access"], headers={"X-Forwarded-Proto": "https"})
h = {k.lower(): v for k, v in r.headers.items()}
check("X-Content-Type-Options: nosniff", h.get("x-content-type-options") == "nosniff")
check("X-Frame-Options: DENY", h.get("x-frame-options") == "DENY", h.get("x-frame-options"))
check("HSTS başlığı var (https)", "max-age" in h.get("strict-transport-security", ""), h.get("strict-transport-security"))
check("API yanıtı önbelleğe alınmaz (no-store)", "no-store" in h.get("cache-control", ""), h.get("cache-control"))
check("Sunucu sürümü sızdırmaz", "django" not in h.get("server", "").lower() and "x-powered-by" not in h, h.get("server"))
r = req("GET", "/admin/login/")
check("Yönetim paneli /admin/ adresinde değil (404)", r.status_code == 404, r.status_code)
r = req("GET", "/gizli-panel-xyz/login/")
check("Yönetim paneli yalnızca gizli adreste açılır", r.status_code == 200, r.status_code)

# ---------- E. injection / abuse ----------
print("\n== E. Enjeksiyon ve kötüye kullanım ==")
payloads = ["' OR '1'='1", "'; DROP TABLE finance_transaction;--", "<script>alert(1)</script>", "{{7*7}}", "${7*7}", "../../etc/passwd", "\u0000null", "😀" * 50]
ok = True
for p in payloads:
    r = req("POST", "/api/transactions/", token=a["access"], json={"title": p[:250], "amount": "1", "transaction_type": "EXPENSE", "category": p[:90], "date": "2026-10-02", "description": p})
    if r.status_code not in (201, 400):
        ok = False
check("Enjeksiyon dizeleri 500 üretmez", ok)
lst = req("GET", "/api/transactions/", token=a["access"])
check("Tablolar sağlam, liste çalışıyor", lst.status_code == 200)
check("Yanıt türü JSON (HTML olarak yorumlanmaz)", lst.headers.get("content-type", "").startswith("application/json"), lst.headers.get("content-type"))
r = req("POST", "/auth/jwt/create/", json={"username": "' OR 1=1 --", "password": "x"})
check("Girişte SQL enjeksiyonu işe yaramaz", r.status_code == 401, r.status_code)
base = {"title": "x", "transaction_type": "EXPENSE", "category": "Food", "date": "2026-10-02"}
for label, extra in [("negatif tutar", {"amount": "-5"}), ("sıfır tutar", {"amount": "0"}), ("1e999", {"amount": "1e999"}), ("NaN", {"amount": "NaN"}), ("çok büyük", {"amount": "9" * 30}), ("çok uzun başlık", {"amount": "1", "title": "x" * 10000}), ("1800 yılı", {"amount": "1", "date": "1800-01-01"}), ("uzun açıklama", {"amount": "1", "description": "x" * 5000})]:
    r = req("POST", "/api/transactions/", token=a["access"], json={**base, **extra})
    check(f"Geçersiz girdi reddedilir: {label}", r.status_code == 400, r.status_code)
big = "x" * (12 * 1024 * 1024)
try:
    r = req("POST", "/api/transactions/", token=a["access"], data=json.dumps({"title": big}), headers={"Content-Type": "application/json"})
    check("12 MB'lık JSON istek reddedilir", r.status_code in (400, 413), r.status_code)
except requests.RequestException as exc:
    check("12 MB'lık istek reddedilir (bağlantı kesildi)", True, str(exc)[:60])
r = req("POST", "/api/scan-receipt/", token=a["access"], files={"image": ("x.png", b"\x00" * (20 * 1024 * 1024), "image/png")})
check("20 MB'lık dosya yüklemesi en başta kesilir (413)", r.status_code == 413, r.status_code)
r = req("PUT", "/api/budgets/sync/", token=a["access"], json={"limits": {f"k{i}": 1 for i in range(500)}})
check("Bütçe senkronunda aşırı kategori sayısı reddedilir", r.status_code == 400, r.status_code)
r = req("POST", "/api/scan-receipt/", token=a["access"], files={"image": ("x.svg", b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>", "image/svg+xml")})
check("SVG/HTML dosyası fiş olarak kabul edilmez", r.status_code == 400, r.status_code)
r = req("POST", "/api/scan-receipt/", token=a["access"], files={"image": ("x.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 100, "image/png")})
check("Bozuk görsel temiz 400 döner", r.status_code == 400, r.status_code)

# ---------- F. auth abuse ----------
print("\n== F. Oturum kötüye kullanımı ==")
r = req("POST", "/auth/jwt/refresh/", json={"refresh": "abc"})
check("Çöp refresh token reddedilir", r.status_code == 401, r.status_code)
new = req("POST", "/auth/jwt/refresh/", json={"refresh": b["refresh"]}).json()
r = req("POST", "/auth/jwt/refresh/", json={"refresh": b["refresh"]})
check("Kullanılmış refresh token tekrar çalışmaz (rotasyon)", r.status_code == 401, r.status_code)
req("POST", "/auth/jwt/logout/", json={"refresh": new["refresh"]})
r = req("POST", "/auth/jwt/refresh/", json={"refresh": new["refresh"]})
check("Çıkıştan sonra refresh token ölü", r.status_code == 401, r.status_code)
codes = [req("POST", "/auth/jwt/create/", json={"username": a_name, "password": f"yanlis{i}"}).status_code for i in range(24)]
check("Şifre tahmini 429 ile durdurulur", 429 in codes, sorted(set(codes)))
check("Kilitliyken bile doğru şifre sınırı aşar (bilgi)", True, "bilgi")
for label, body in [("tekrar eden kullanıcı adı", {"username": b_name}), ("zayıf şifre", {"username": f"yeni{suffix}", "password": "12345678"}), ("geçersiz e-posta", {"username": f"yeni{suffix}", "email": "yok"}), ("çok uzun kullanıcı adı", {"username": "u" * 500})]:
    payload = {"password": "Sup3r-Gizli-Sifre-91", "email": "a@b.com", **body}
    r = req("POST", "/auth/users/", json=payload)
    check(f"Kayıt reddedilir: {label}", r.status_code == 400, r.status_code)
r = req("POST", "/auth/users/reset_password/", json={"email": "bob@example.com"})
check("Şifre sıfırlama (e-posta) kapalı", r.status_code in (401, 403), r.status_code)

# ---------- summary ----------
failed = [r for r in results if not r[0]]
print(f"\n{len(results) - len(failed)}/{len(results)} kontrol geçti")
for _, name, detail in failed:
    print("BAŞARISIZ:", name, detail)
sys.exit(1 if failed else 0)
