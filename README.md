# Panduan Eksperimen & Pengujian Sistem Client-Proxy-Server

[cite_start]Dokumen ini memuat panduan operasional teknis secara menyeluruh untuk mengeksekusi sistem Client-Proxy-Server berbasis *low-level socket programming* menggunakan Python 3 [cite: 61, 126-127]. [cite_start]Seluruh prosedur dikonfigurasikan secara spesifik menggunakan lingkungan editor **Visual Studio Code (VS Code)** dan divalidasi menggunakan **Wireshark Packet Analyzer** [cite: 134-135, 140-141].

---

## 1. Arsitektur Komponen Berkas Sistem
[cite_start]Sistem ini diimplementasikan menggunakan tepat tiga berkas Python utama ditambah satu berkas otomatisasi pengujian beban[cite: 47, 51, 254]:
* [cite_start]**`webserver.py`**: Beroperasi pada port 8000 (TCP untuk HTTP) dan port 9000 (UDP untuk Echo)[cite: 263, 273]. [cite_start]Berkas ini berfungsi melayani permintaan berkas HTML statis, menangani kode galat standar (404 Not Found dan 500 Internal Server Error), mencatat log aktivitas secara rinci, serta menerapkan model *multithreading* untuk menangani beberapa koneksi simultan [cite: 264, 270-271, 275].
* [cite_start]**`proxy.py`**: Beroperasi pada port 8080 (TCP) sebagai perantara tunggal (*gateway*) antara klien dan server [cite: 155, 277-278]. [cite_start]Berkas ini menjalankan mekanisme *caching* wajib untuk menyimpan respons HTTP secara lokal ke dalam direktori `cache/` berdasarkan jalur URL, mencatat log status Cache HIT atau MISS, serta menangani galat propagasi seperti 502 Bad Gateway dan 504 Gateway Timeout [cite: 279, 287-293].
* [cite_start]**`client.py`**: Berfungsi sebagai alat pengujian fungsionalitas ganda[cite: 48]. [cite_start]*Mode TCP* digunakan untuk mengirimkan permintaan HTTP GET ke Proxy Server lalu menampilkan teks HTML mentah pada terminal [cite: 309-311]. [cite_start]*Mode UDP* digunakan khusus untuk melakukan pengujian performa kualitas jaringan (QoS) dengan mengirimkan minimal 10 paket proaktif terstruktur langsung ke Web Server dengan batas waktu tunggu (*timeout*) maksimal 1 detik per paket [cite: 87, 312-314, 320, 414-415].
* [cite_start]**`multi_client.py`**: Skrip otomatisasi pengujian beban (*stress testing*) yang memanfaatkan modul `subprocess` untuk meluncurkan 5 *instance* klien secara simultan dalam hitungan milidetik guna memvalidasi keandalan model *thread-per-connection* pada server dan proxy [cite: 336-337, 401-404].

---

## 2. Panduan Menjalankan Sistem di VS Code

### Langkah 2.1: Menyiapkan Workspace Proyek
1. [cite_start]Buka aplikasi **VS Code** pada perangkat komputer Anda[cite: 135].
2. [cite_start]Pilih menu `File` > `Open Folder...`, lalu arahkan ke direktori proyek tempat empat berkas Python di atas dan aset berkas `index.html` diletakkan dalam satu folder root yang sama[cite: 259].
3. Buka terminal terintegrasi dengan menekan kombinasi tombol `Ctrl + \`` atau melalui menu `Terminal` > `New Terminal`.

### Langkah 2.2: Mengonfigurasi Pembagian Panel Terminal (Split Terminal)
Karena komponen server dan proxy berjalan secara persisten menggunakan kalang tak berujung (`while True`), terminal harus dibagi menjadi beberapa panel agar aktivitas log dapat dipantau berdampingan secara *real-time*:
1. Pada panel terminal terintegrasi VS Code yang sudah terbuka, perhatikan pojok kanan atas area terminal lalu klik ikon **Split Terminal** (ikon kotak terbagi dua) atau gunakan kombinasi tombol `Ctrl + Shift + 5`.
2. Lakukan klik sebanyak dua kali lagi hingga terminal terbagi menjadi minimal **3 panel berdampingan**.
3. Sesuaikan lebar masing-masing panel agar pembacaan teks baris log tidak terpotong.

### Langkah 2.3: Inisialisasi Berurutan Komponen Jaringan
[cite_start]Inisialisasi eksekusi program wajib mengikuti urutan hierarki topologi dari sisi belakang menuju sisi depan untuk mencegah kegagalan pengikatan koneksi (*Connection Refused*)[cite: 481]:

* **Terminal 1 (Panel Paling Kiri) - Menjalankan Web Server:**
    ```bash
    python webserver.py
    ```
    *Pastikan terminal ini tetap dibiarkan aktif. [cite_start]Server akan mencetak log startup dan pool thread siap melayani data masuk[cite: 380].*

* **Terminal 2 (Panel Tengah) - Menjalankan Proxy Server:**
    ```bash
    python proxy.py
    ```
    [cite_start]*Proxy akan mulai mendengarkan koneksi pada port 8080 dan secara otomatis mendeteksi atau membuat folder direktori lokal bernama `cache/`[cite: 277, 388].*

* **Terminal 3 (Panel Paling Kanan) - Menjalankan Klien Tester:**
    *Gunakan panel terminal ke-3 ini untuk mengeksekusi seluruh skenario pengujian fungsional di bawah.*

---

## 3. Skenario Pengujian & Pengumpulan Data Metrik

### Skenario A: Verifikasi Mekanisme TCP Caching (HIT vs MISS)
1. [cite_start]Pada Terminal 3, jalankan pengujian TCP klien untuk pertama kalinya:
   ```bash
   python client.py -mode tcp