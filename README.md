# Moodle PDF Downloader

Moodle ders sayfalarındaki PDF ve dokümanları kolayca indirip ZIP dosyası olarak kaydetmenizi sağlayan bir Python uygulamasıdır. Kullanıcı dostu arayüzü ile ders URL’sini, indirme klasörünü ve ZIP dosya ismini seçebilirsiniz.

## Özellikler
- **Kullanıcı Arayüzü (GUI):** Tkinter tabanlı kolay kullanım.
- **Ders URL’si Girişi:** Herhangi bir Moodle dersinin bağlantısını girin.
- **Klasör Seçici:** İndirme klasörünü seçin veya daha önce kullandıklarınızı açılır menüden seçin.
- **ZIP Dosya İsmi:** ZIP dosyasının adını belirleyin.
- **Oturum (MoodleSession) Desteği:** Kendi oturum token’ınızı girerek erişim sağlayın.
- **Ayarları Otomatik Kaydetme:** Son kullanılan URL, klasörler ve ZIP ismi kaydedilir.

## Kurulum
1. Python 3 yüklü olmalı.
2. Gerekli kütüphaneleri yükleyin:
   ```bash
   pip install requests beautifulsoup4
   ```

## Kullanım
1. `downloader.py` dosyasını çalıştırın:
   ```bash
   python downloader.py
   ```
2. Açılan arayüzde:
   - **Ders URL’si**: Moodle’daki dersin bağlantısını girin.
   - **İndirme Klasörü**: Klasör seçin veya açılır menüden daha önce kullandıklarınızı seçin.
   - **ZIP Dosya İsmi**: Oluşturulacak ZIP dosyasının adını girin.
   - **MoodleSession**: Tarayıcınızdan aldığınız güncel oturum token’ınızı girin.
   - **İndir ve ZIP’le** butonuna tıklayın.

## MoodleSession Nasıl Alınır?
1. Moodle’a giriş yapın.
2. Tarayıcıda geliştirici araçlarını açın (F12).
3.Bu dosyadaki MoodleSessionScripti kopyalayarak  MoodleSession değerine ulaşabilirsiniz.
4. “Application” veya “Depolama” sekmesinden “Cookies” bölümüne gelin.
5. `MoodleSession` değerini kopyalayın ve arayüze yapıştırın.






## Lisans
MIT 