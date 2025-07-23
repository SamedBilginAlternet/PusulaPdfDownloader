import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# --- İNDİRME FONKSİYONU ---
def download_and_zip(base_url, download_folder, zip_filename, cookies, progress_callback=None):
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
    total = len(resource_links)
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
        if progress_callback:
            progress_callback(int(i / total * 100))
    if not downloaded_files:
        raise Exception("Hiçbir dosya indirilemedi!")
    with ZipFile(zip_filename, "w") as zipf:
        for file in downloaded_files:
            zipf.write(file, arcname=os.path.basename(file))
    return len(downloaded_files)

# --- İNDİRME THREAD'I ---
class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url, folder, zipname, session_token):
        super().__init__()
        self.url = url
        self.folder = folder
        self.zipname = zipname
        self.session_token = session_token

    def run(self):
        try:
            count = download_and_zip(
                self.url, self.folder, self.zipname,
                {"MoodleSession": self.session_token},
                progress_callback=self.progress.emit
            )
            self.finished.emit(count)
        except Exception as e:
            self.error.emit(str(e))

# --- ANA ARAYÜZ ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moodle PDF Downloader (PyQt5)")
        self.setGeometry(100, 100, 500, 350)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # URL
        layout.addWidget(QLabel("Ders URL'si:"))
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        # Klasör seçici
        layout.addWidget(QLabel("İndirme Klasörü:"))
        hbox = QHBoxLayout()
        self.folder_input = QLineEdit()
        hbox.addWidget(self.folder_input)
        self.folder_btn = QPushButton("Klasör Seç")
        self.folder_btn.clicked.connect(self.select_folder)
        hbox.addWidget(self.folder_btn)
        layout.addLayout(hbox)

        # ZIP dosya ismi
        layout.addWidget(QLabel("ZIP Dosya İsmi:"))
        self.zip_input = QLineEdit("all_docs.zip")
        layout.addWidget(self.zip_input)

        # MoodleSession
        layout.addWidget(QLabel("MoodleSession (Oturum Token):"))
        self.session_input = QLineEdit()
        self.session_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.session_input)

        # İndir butonu
        self.download_btn = QPushButton("İndir ve ZIP'le")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # İlerleme çubuğu
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            self.folder_input.setText(folder)

    def start_download(self):
        url = self.url_input.text().strip()
        folder = self.folder_input.text().strip()
        zipname = self.zip_input.text().strip()
        session_token = self.session_input.text().strip()
        if not url or not folder or not zipname or not session_token:
            QMessageBox.warning(self, "Eksik Bilgi", "Lütfen tüm alanları doldurun!")
            return
        self.download_btn.setEnabled(False)
        self.progress.setValue(0)
        self.thread = DownloadThread(url, folder, zipname, session_token)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, count):
        self.download_btn.setEnabled(True)
        self.progress.setValue(100)
        QMessageBox.information(self, "Başarılı", f"{count} dosya indirildi ve ZIP'e eklendi!")

    def on_error(self, msg):
        self.download_btn.setEnabled(True)
        QMessageBox.critical(self, "Hata", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 