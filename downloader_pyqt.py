import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from zipfile import ZipFile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QFileDialog,
    QVBoxLayout, QHBoxLayout, QProgressBar, QMessageBox, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

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
        self.setGeometry(100, 100, 500, 400)
        self.setWindowIcon(QIcon.fromTheme("document-save"))
        self.init_ui()
        self.setStyleSheet(self.get_stylesheet())

    def get_stylesheet(self):
        return """
        QWidget {
            background-color: #23272e;
            color: #f8f8f2;
            font-family: 'Segoe UI', 'Arial', sans-serif;
            font-size: 15px;
        }
        QLineEdit, QProgressBar {
            background: #2d323b;
            border: 1.5px solid #44475a;
            border-radius: 6px;
            padding: 6px;
            color: #f8f8f2;
        }
        QLabel {
            color: #8be9fd;
            font-weight: bold;
        }
        QPushButton {
            background-color: #50fa7b;
            color: #23272e;
            border-radius: 8px;
            padding: 8px 18px;
            font-weight: bold;
            font-size: 15px;
        }
        QPushButton:hover {
            background-color: #3be8b0;
        }
        QProgressBar {
            border: 1.5px solid #44475a;
            border-radius: 6px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #ffb86c;
            border-radius: 6px;
        }
        QFrame {
            background: #282a36;
            border-radius: 10px;
            border: 1.5px solid #44475a;
        }
        """

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(18)

        # Başlık
        title = QLabel("Moodle PDF Downloader")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        # Ana kutu
        frame = QFrame()
        frame_layout = QVBoxLayout()
        frame_layout.setSpacing(12)
        frame.setLayout(frame_layout)

        # URL
        url_label = QLabel("Ders URL'si:")
        self.url_input = QLineEdit()
        frame_layout.addWidget(url_label)
        frame_layout.addWidget(self.url_input)

        # Klasör seçici
        folder_label = QLabel("İndirme Klasörü:")
        hbox = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_btn = QPushButton("Klasör Seç")
        self.folder_btn.clicked.connect(self.select_folder)
        hbox.addWidget(self.folder_input)
        hbox.addWidget(self.folder_btn)
        # Klasörü Aç butonu
        self.open_folder_btn = QPushButton("Klasörü Aç")
        self.open_folder_btn.clicked.connect(self.open_folder)
        hbox.addWidget(self.open_folder_btn)
        frame_layout.addWidget(folder_label)
        frame_layout.addLayout(hbox)

        # ZIP dosya ismi
        zip_label = QLabel("ZIP Dosya İsmi:")
        self.zip_input = QLineEdit("all_docs.zip")
        frame_layout.addWidget(zip_label)
        frame_layout.addWidget(self.zip_input)

        # MoodleSession
        session_label = QLabel("MoodleSession (Oturum Token):")
        self.session_input = QLineEdit()
        self.session_input.setEchoMode(QLineEdit.Password)
        frame_layout.addWidget(session_label)
        frame_layout.addWidget(self.session_input)

        # İndir butonu
        self.download_btn = QPushButton("İndir ve ZIP'le")
        self.download_btn.clicked.connect(self.start_download)
        frame_layout.addWidget(self.download_btn)

        # İlerleme çubuğu
        self.progress = QProgressBar()
        self.progress.setValue(0)
        frame_layout.addWidget(self.progress)

        main_layout.addWidget(frame)
        self.setLayout(main_layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if folder:
            self.folder_input.setText(folder)

    def open_folder(self):
        folder = self.folder_input.text().strip()
        if folder and os.path.isdir(folder):
            if sys.platform.startswith('win'):
                os.startfile(folder)
            elif sys.platform.startswith('darwin'):
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')

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