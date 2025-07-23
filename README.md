# Moodle PDF Downloader (PyQt5)

Moodle ders sayfalarındaki PDF ve dokümanları kolayca indirip ZIP dosyası olarak kaydetmenizi sağlayan modern bir Python uygulamasıdır. PyQt5 tabanlı arayüzü ile ders URL’sini, indirme klasörünü ve ZIP dosya ismini kolayca seçebilirsiniz.

## Özellikler
- **Modern Arayüz:** PyQt5 ile şık ve kullanıcı dostu.
- **Ders URL’si Girişi:** Herhangi bir Moodle dersinin bağlantısını girin.
- **Klasör Seçici:** İndirme klasörünü seçin.
- **ZIP Dosya İsmi:** ZIP dosyasının adını belirleyin.
- **Oturum (MoodleSession) Desteği:** Kendi oturum token’ınızı girerek erişim sağlayın.
- **İlerleme Çubuğu:** İndirme işlemi sırasında ilerlemeyi takip edin.

## Kurulum
1. Python 3 yüklü olmalı.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install PyQt5 requests beautifulsoup4
   ```

## Kullanım
1. `downloader_pyqt.py` dosyasını çalıştırın:
   ```bash
   python downloader_pyqt.py
   ```
2. Açılan arayüzde:
   - **Ders URL’si**: Moodle’daki dersin bağlantısını girin.
   - **İndirme Klasörü**: Klasör seçin.
   - **ZIP Dosya İsmi**: Oluşturulacak ZIP dosyasının adını girin.
   - **MoodleSession**: Tarayıcınızdan aldığınız güncel oturum token’ınızı girin.
   - **İndir ve ZIP’le** butonuna tıklayın.

## MoodleSession Nasıl Alınır?
1. Moodle’a giriş yapın.
2. Tarayıcıda geliştirici araçlarını açın (F12).
3. Bu repodaki `MoodleSessionScript.js` dosyasındaki scripti kullanarak veya manuel olarak “Application/Depolama > Cookies” bölümünden `MoodleSession` değerini kopyalayın.
4. Arayüze yapıştırın.

## Lisans
MIT 