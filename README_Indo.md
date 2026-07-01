# Slapx ⚡

Sebuah soundboard pendeteksi tamparan dan pukulan fisik laptop untuk Linux. Ketika Anda menampar atau memukul sasis laptop Anda, program ini akan memutar efek suara khusus acak (hingga 3 trek khusus) atau suara retro sintetis secara otomatis.

Slapx menghubungkan interaksi pengguna fisik dengan respons digital dengan mengubah sasis laptop Anda menjadi touchpad interaktif. Program ini dirancang agar sangat responsif, ringan, dan dapat disesuaikan.

---

## 📖 Daftar Isi
- [Fitur](#fitur)
- [Cara Kerja](#cara-kerja)
- [Arsitektur Proyek (Dimodularisasi)](#arsitektur-proyek-dimodularisasi)
- [Dependensi & Instalasi](#dependensi--instalasi)
- [Penggunaan](#penggunaan)
  - [Dashboard GUI (Default)](#dashboard-gui-default)
  - [Mode CLI Tanpa Kepala (Headless)](#mode-cli-tanpa-kepala-headless)
- [Konfigurasi (`config.json`)](#konfigurasi-configjson)
- [Pemecahan Masalah](#pemecahan-masalah)
- [Lisensi](#lisensi)

---

## ✨ Fitur

- 🎧 **Pendeteksi Pukulan Sasis**: Menggunakan `arecord` dari ALSA untuk menangkap sinyal audio mentah dari mikrofon bawaan Anda, mendeteksi transient amplitudo tinggi (lonjakan) yang disebabkan oleh tamparan/ketukan fisik laptop.
- 🎛️ **Grafik gelombang bergulir visual**: Dashboard Canvas Tkinter real-time yang menunjukkan puncak audio bergulir relatif terhadap garis ambang batas (threshold) Anda.
- 🎨 **Tema UI Futuristik**: Tema gelap penuh gaya yang terinspirasi oleh Catppuccin Mocha dengan warna status LED yang responsif.
- ⚡ **Pemicu tanpa latensi (zero-latency)**: Menggunakan proses pemutaran `mpv` non-blocking dengan beban overhead rendah untuk memastikan suara langsung terpicu seketika.
- 🎹 **Synthesizer Suara Bawaan**: Menghasilkan tiga efek suara retro secara otomatis (`default_ouch.wav`, `default_laser.wav`, dan `default_slap.wav`) saat booting pertama kali, memungkinkan Anda untuk langsung menguji aplikasi seketika.
- 🗃️ **Hingga 3 Slot Audio Kustom**: Tautkan trek audio kustom Anda sendiri (`.mp3`, `.wav`, `.ogg`, `.flac`, dll.) yang dipilih secara acak setelah pendeteksian.
- ⏱️ **Pelindung Jeda Waktu (Cooldown)**: Mencegah pemicuan ganda atau loop umpan balik audio dengan jeda cooldown yang dapat disesuaikan (mulai dari 0,1 detik hingga 5,0 detik).
- 🖥️ **Mode Headless Bebas X11**: Gunakan opsi `--headless` untuk menjalankan Slapx tanpa dependensi X11/Tkinter, membuatnya sangat cocok untuk server, eksekusi SSH jarak jauh, atau daemon terminal.
- ⚙️ **Konfigurasi Persisten**: Menyimpan pengaturan secara otomatis (sensitivitas, cooldown, slot audio, total tamparan) ke `config.json` dan memulihkannya kembali saat diluncurkan.

---

## 🛠️ Arsitektur Proyek (Dimodularisasi)

Codebase telah difaktorkan ulang ke dalam struktur modular yang rapi. Ini memisahkan peran, menghindari ketergantungan melingkar (circular dependencies), dan memungkinkan Tkinter dilewati sepenuhnya dalam mode headless.

```
Slapx/
├── slapx.py               # Titik masuk utama pembungkus CLI (mengeksekusi main.py)
├── config.json            # Penyimpanan konfigurasi yang dibuat otomatis
├── sounds/                # Direktori berisi klip suara default yang disintesis
│   ├── default_laser.wav
│   ├── default_ouch.wav
│   └── default_slap.wav
└── slapx/                 # Paket Python Modular
    ├── __init__.py        # File inisialisasi paket
    ├── constants.py       # Konstanta global (Sample rate, chunk sizes, slot maksimum)
    ├── config.py          # Kelas ConfigManager untuk persistensi status
    ├── synthesizer.py     # Algoritma sintesis gelombang untuk audio retro default
    ├── detector.py        # Pengelola subproses untuk perekaman ALSA dan pemutaran MPV
    ├── gui.py             # Dashboard visualizer Tkinter (dimuat secara malas/lazy-loaded pada mode GUI)
    └── main.py            # Orkestrator pusat dan parser argumen CLI
```

### Rincian Modul:
1. **[constants.py](file:///home/hangineering/slapx/slapx/constants.py)**: Memusatkan parameter seperti `SAMPLE_RATE` (16kHz), `CHUNK_SIZE` (512), dan `MAX_SLOTS` (3).
2. **[config.py](file:///home/hangineering/slapx/slapx/config.py)**: Mendefinisikan `ConfigManager` untuk memuat pengaturan, menginisialisasi nilai default, dan menulis modifikasi dengan aman.
3. **[synthesizer.py](file:///home/hangineering/slapx/slapx/synthesizer.py)**: Menyintesis bentuk gelombang yang dimodelkan secara matematis (sapuan frekuensi, peluruhan eksponensial, white noise) dan menyimpannya sebagai file `.wav`.
4. **[detector.py](file:///home/hangineering/slapx/slapx/detector.py)**: Mengalirkan byte stream mikrofon dari proses latar belakang `arecord`, menghitung puncak PCM, mendeteksi pemicu amplitudo, dan menjalankan pemutaran `mpv` secara non-blocking.
5. **[gui.py](file:///home/hangineering/slapx/slapx/gui.py)**: Antarmuka grafis utama yang dibangun dengan Tkinter. Memperbarui kanvas bentuk gelombang pada ~33 fps (setiap 30ms) menggunakan Queue yang thread-safe, berkedip merah saat tamparan terpicu, dan menyediakan slider bagi pengguna.
6. **[main.py](file:///home/hangineering/slapx/slapx/main.py)**: Menginstansiasi modul, bertindak sebagai koordinator, dan merutekan ke loop CLI/GUI tergantung pada opsi/flag CLI.

---

## 📥 Dependensi & Instalasi

Slapx berjalan di Linux. Sebelum meluncurkan, instal dependensi sistem menggunakan manajer paket Anda.

### Debian / Ubuntu
```bash
sudo apt update
sudo apt install alsa-utils mpv python3-tk
```

### Arch Linux
```bash
sudo pacman -S alsa-utils mpv tk
```

### Fedora
```bash
sudo dnf install alsa-utils mpv python3-tkinter
```

---

## 🚀 Penggunaan

Pertama, pastikan skrip titik masuk (entrypoint) dapat dieksekusi:
```bash
chmod +x slapx.py
```

### Dashboard GUI (Default)
Untuk meluncurkan panel kontrol visualizer grafis:
```bash
./slapx.py
```
- Klik **Start Listening** untuk mengaktifkan mikrofon.
- Sesuaikan **Sensitivity** (Sensitivitas) agar sesuai dengan lingkungan laptop Anda.
- Ketuk sasis laptop Anda di dekat keyboard atau trackpad untuk mengujinya!
- Klik **Ikon Folder (📂)** di slot mana saja untuk memilih file suara kustom.

### Mode CLI Tanpa Kepala (Headless)
Untuk menjalankan di dalam terminal atau sesi SSH tanpa menampilkan jendela UI:
```bash
./slapx.py --headless
```

Untuk menimpa pengaturan melalui CLI:
```bash
./slapx.py --headless --sensitivity 9000 --cooldown 2.0
```

---

## ⚙️ Konfigurasi (`config.json`)

File konfigurasi dibuat secara otomatis di direktori tempat perintah dijalankan. Berikut adalah strukturnya:

```json
{
    "sensitivity": 8000,
    "cooldown": 1.5,
    "sounds": [
        "/home/user/Projects/Slapx/sounds/default_ouch.wav",
        "/home/user/Projects/Slapx/sounds/default_laser.wav",
        "/home/user/Projects/Slapx/sounds/default_slap.wav"
    ],
    "total_slaps": 42
}
```

- **`sensitivity`** (Integer): Nilai ambang batas suara (kisaran: `500` - `30000`). Angka yang lebih rendah berarti lebih sensitif; angka yang lebih tinggi membutuhkan tamparan yang lebih keras.
- **`cooldown`** (Float): Durasi dalam hitungan detik (kisaran: `0.1` - `5.0`) di mana tamparan baru akan diabaikan untuk mencegah loop umpan balik.
- **`sounds`** (Array of strings): Jalur file absolut untuk masing-masing dari ketiga slot audio. Jika slot kosong, program akan menggunakan suara sintesis default sebagai cadangan.
- **`total_slaps`** (Integer): Jumlah kumulatif tamparan yang terdeteksi sepanjang masa.

---

## 🔍 Pemecahan Masalah

- **Mikrofon tidak menangkap suara**:
  Pastikan utilitas ALSA dapat melihat perangkat perekam Anda:
  ```bash
  arecord -l
  ```
  Pastikan mikrofon Anda tidak dibisukan (mute) dan gain input telah dinaikkan pada pengatur volume sistem Anda (misalnya, `pavucontrol` or `alsamixer`).
- **Penundaan suara atau latensi (lag)**:
  Pastikan `mpv` terinstal dan berjalan dengan benar dari terminal Anda. Jika Anda mengalami latensi, itu mungkin disebabkan oleh pengaturan buffer PulseAudio/Pipewire. Slapx meluncurkan `mpv` dengan argumen latensi rendah untuk menjaganya tetap secepat mungkin.
- **Kesalahan Tkinter tidak terinstal**:
  If you see `ModuleNotFoundError: No module named '_tkinter'`, instal `python3-tk` menggunakan manajer sistem Anda. Jika Anda tidak dapat menginstal komponen grafis, jalankan skrip dengan opsi `--headless`.

---

## 📄 Lisensi
Proyek ini bersifat open-source dan bebas untuk dimodifikasi atau didistribusikan. Selamat menampar!

---

## ☕ Support Me

If you find this project useful, consider supporting me:

[![Donate via Saweria](https://blue.kumparan.com/image/upload/fl_progressive,fl_lossy,c_fill,q_auto:best,w_640/v1634025439/01gvcf9vy7dhk2nkx30j2wr6n5.png)](https://saweria.co/raiinime)
