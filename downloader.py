import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile
import tkinter as tk
from tkinter import filedialog, messagebox
import json

# === AYARLAR ===
SETTINGS_FILE = "settings.json"

# Varsayılan ayarlar
DEFAULT_SETTINGS = {
    "last_url": "",
    "download_folders": [],
    "last_zip_name": "all_docs.zip"
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)

def download_and_zip(base_url, download_folder, zip_filename, cookies):
    os.makedirs(download_folder, exist_ok=True)
    session = requests.Session()
    res = session.get(base_url, cookies=cookies)
    if res.status_code != 200:
        raise Exception(f"Sayfa alınamadı! Status code: {res.status_code}")
    soup = BeautifulSoup(res.text, "html.parser")
    resource_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/mod/resource/view.php?id=" in href:
            full_url = urljoin(base_url, href)
            resource_links.append(full_url)
    resource_links = list(set(resource_links))
    downloaded_files = []
    for i, view_url in enumerate(resource_links, start=1):
        r = session.get(view_url, cookies=cookies, allow_redirects=True, stream=True)
        final_url = r.url
        filename = final_url.split("/")[-1].split("?")[0]
        filepath = os.path.join(download_folder, filename)
        content_type = r.headers.get("Content-Type", "")
        if not any(ct in content_type for ct in [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument"
        ]):
            continue
        with open(filepath, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        downloaded_files.append(filepath)
    if not downloaded_files:
        raise Exception("Hiçbir dosya indirilemedi!")
    with ZipFile(zip_filename, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, arcname=os.path.basename(file))
    return len(downloaded_files)

def main_gui():
    settings = load_settings()
    root = tk.Tk()
    root.title("Moodle PDF Downloader")
    root.geometry("450x320")

    def select_folder():
        folder = filedialog.askdirectory()
        if folder:
            folder_var.set(folder)
            if folder not in settings["download_folders"]:
                settings["download_folders"].append(folder)
                save_settings(settings)
                update_folder_menu()

    def update_folder_menu():
        menu = folder_menu["menu"]
        menu.delete(0, "end")
        for f in settings["download_folders"]:
            menu.add_command(label=f, command=lambda v=f: folder_var.set(v))

    def start_download():
        url = url_var.get().strip()
        folder = folder_var.get().strip()
        zipname = zip_var.get().strip()
        session_token = session_var.get().strip()
        if not url or not folder or not zipname or not session_token:
            messagebox.showerror("Eksik Bilgi", "Lütfen tüm alanları doldurun!")
            return
        cookies = {"MoodleSession": session_token}
        try:
            root.config(cursor="wait")
            root.update()
            count = download_and_zip(url, folder, zipname, cookies)
            messagebox.showinfo("Başarılı", f"{count} dosya indirildi ve ZIP'e eklendi!\nZIP: {zipname}")
            # Ayarları güncelle
            settings["last_url"] = url
            settings["last_zip_name"] = zipname
            if folder not in settings["download_folders"]:
                settings["download_folders"].append(folder)
            save_settings(settings)
            update_folder_menu()
        except Exception as e:
            messagebox.showerror("Hata", str(e))
        finally:
            root.config(cursor="")

    # --- Arayüz Elemanları ---
    tk.Label(root, text="Ders URL'si:").pack(anchor="w", padx=10, pady=(10,0))
    url_var = tk.StringVar(value=settings.get("last_url", ""))
    tk.Entry(root, textvariable=url_var, width=60).pack(padx=10)

    tk.Label(root, text="İndirme Klasörü:").pack(anchor="w", padx=10, pady=(10,0))
    folder_frame = tk.Frame(root)
    folder_frame.pack(padx=10, fill="x")
    folder_var = tk.StringVar(value=settings["download_folders"][0] if settings["download_folders"] else "downloads")
    folder_menu = tk.OptionMenu(folder_frame, folder_var, *(settings["download_folders"] or ["downloads"]))
    folder_menu.pack(side="left")
    tk.Button(folder_frame, text="Klasör Seç", command=select_folder).pack(side="left", padx=5)

    tk.Label(root, text="ZIP Dosya İsmi:").pack(anchor="w", padx=10, pady=(10,0))
    zip_var = tk.StringVar(value=settings.get("last_zip_name", "all_docs.zip"))
    tk.Entry(root, textvariable=zip_var, width=40).pack(padx=10)

    tk.Label(root, text="MoodleSession (Oturum Token):").pack(anchor="w", padx=10, pady=(10,0))
    session_var = tk.StringVar(value="")
    tk.Entry(root, textvariable=session_var, width=40, show="*").pack(padx=10)

    tk.Button(root, text="İndir ve ZIP'le", command=start_download, bg="#4CAF50", fg="white").pack(pady=20)

    update_folder_menu()
    root.mainloop()

if __name__ == "__main__":
    main_gui()
