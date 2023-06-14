# OCR Tabel dari Foto Dokumen menggunakan YOLOv8
Selamat datang di proyek "OCR Tabel dari Foto Dokumen menggunakan YOLOv8"! Proyek ini dibuat sebagai bagian dari tugas take home untuk melamar posisi Machine Vision Engineer di eFishery.

## Deskripsi Proyek
Proyek ini bertujuan untuk mengembangkan sebuah sistem yang dapat melakukan Optical Character Recognition (OCR) pada tabel yang terdapat dalam foto dokumen. Dalam proyek ini, kami akan menggunakan model YOLOv8 untuk mendeteksi tabel dalam gambar dan kemudian menerapkan teknik OCR untuk mengekstraksi teks dari tabel tersebut. Tujuan utama proyek ini adalah memberikan alat yang dapat membantu dalam memperoleh data dari tabel secara otomatis dan efisien.

## Instalasi dan Penggunaan
Berikut adalah langkah-langkah untuk menginstal dan menjalankan proyek ini di local environtment, sangat disarankan untuk menggunakan virtual environment atau sudah terpasang docker:
### Python Lokal
1. Kloning repositori ini: Gunakan perintah git clone untuk mengkloning repositori ini ke direktori lokal.
```
git clone https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery.git
```
2. Pengaturan lingkungan virtual (opsional): Disarankan untuk membuat dan mengaktifkan lingkungan virtual Python sebelum melanjutkan instalasi dependensi. Anda dapat menggunakan venv atau alat serupa.
3. Instalasi dependensi: Masuk ke direktori proyek dan jalankan perintah berikut untuk menginstal dependensi yang diperlukan.
```
pip install -r requirements.txt
```
4. Untuk mengeksekusi aplikasi dan sehingga muncul interface aplikasinya, jalankan perintah eksekusi di dalam direktori
```
streamlit run app.py
```
5. Buka browser internet dan masuk ke localhost:8501, aplikasi terbuka selamat mencoba.

### docker-compose
1. Kloning repositori ini: Gunakan perintah git clone untuk mengkloning repositori ini ke direktori lokal.
```
git clone https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery.git
```
2. Jalankan perintah `docker-compose` ini untuk mulai build dan menjalankan langsung aplikasi
```
docker-compose up
```
3. Buka browser internet dan masuk ke localhost:8501, aplikasi terbuka selamat mencoba.

## Interface antar muka
### Input gambar
![image](https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery/assets/16248869/17e652aa-0310-45ea-b2fe-2a383882d397)

### Upload Gambar
![image](https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery/assets/16248869/c4cb990a-cb47-4e40-858d-48494d37e7ef)

### Hasil deteksi dan OCR dari Tabel
![image](https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery/assets/16248869/50446e57-c1fd-4ba3-8fd2-dad60971d1b8)
![image](https://github.com/fulankun1412/OCR-YoloV8-Lanang-efishery/assets/16248869/2bab2489-291e-4e11-955e-845e12e8f62a)

## Referensi 
Dokumentasi YOLOv8: [Ultralytics YOLOv8](https://docs.ultralytics.com/modes/)
