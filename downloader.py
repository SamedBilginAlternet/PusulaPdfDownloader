import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile

# === AYARLAR ===
BASE_URL = "http://eds.pau.edu.tr/2/course/view.php?id=225477"
DOWNLOAD_FOLDER = "downloads"
ZIP_FILENAME = "all_docs.zip"

cookies = {
    
    "MoodleSession": "your session token",  # Güncel MoodleSession
}

# === Hazırlık ===
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
session = requests.Session()

print("🌐 Sayfa yükleniyor...")
res = session.get(BASE_URL, cookies=cookies)
if res.status_code != 200:
    print(f"❌ Sayfa alınamadı! Status code: {res.status_code}")
    exit()

print("✅ Sayfa başarıyla alındı.\n")

soup = BeautifulSoup(res.text, "html.parser")
resource_links = []

# 🎯 view.php ile başlayan Moodle kaynak linklerini bul
for a in soup.find_all("a", href=True):
    href = a["href"]
    if "/mod/resource/view.php?id=" in href:
        full_url = urljoin(BASE_URL, href)
        resource_links.append(full_url)

resource_links = list(set(resource_links))  # tekrarları kaldır
print(f"🔗 {len(resource_links)} adet 'view.php?id=' linki bulundu.\n")

downloaded_files = []

# 🔁 Her view.php linkine git, yönlendirilen gerçek dosyayı indir
for i, view_url in enumerate(resource_links, start=1):
    print(f"➡️  [{i}/{len(resource_links)}] {view_url}")
    try:
        # Yönlendirmeyi takip et → gerçek dosya linkine ulaş
        r = session.get(view_url, cookies=cookies, allow_redirects=True, stream=True)
        final_url = r.url  # yönlendirilmiş gerçek dosya (pluginfile.php)

        filename = final_url.split("/")[-1].split("?")[0]
        filepath = os.path.join(DOWNLOAD_FOLDER, filename)

        content_type = r.headers.get("Content-Type", "")
        if not any(ct in content_type for ct in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument"
        ]):
            print(f"⚠️ Geçersiz içerik türü: {content_type}")
            continue

        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        downloaded_files.append(filepath)
        print(f"✅ İndirildi: {filename}\n")

    except Exception as e:
        print(f"❌ Hata: {e}\n")

# 🗜 ZIP işlemi
print(f"🗜 ZIP'e {len(downloaded_files)} dosya ekleniyor...")
with ZipFile(ZIP_FILENAME, "w") as zipf:
    for file in downloaded_files:
        zipf.write(file, arcname=os.path.basename(file))

print("✅ Tüm işlem tamamlandı. ZIP dosyası: all_docs.zip")
