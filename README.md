---

# 🤖 Intelligent Unstructured Data Parser (Local LLM)

Aplikasi cerdas untuk mengonversi **teks tidak terstruktur** (seperti chat, notulen rapat, atau laporan manual) menjadi **data database terstruktur (CSV)** secara otomatis.

Proyek ini dirancang untuk berjalan **100% Offline** (Local Inference) menggunakan teknologi **Small Language Model (SLM) Llama 3.2** melalui framework **Ollama**, menjamin privasi data akademik tanpa dikirim ke cloud server pihak ketiga.

---

## ✨ Fitur Unggulan

* **🛡️ Privacy First:** Data diproses di perangkat lokal (Localhost), aman untuk data sensitif.
* **🧠 AI-Powered Parsing:** Mengubah instruksi bahasa alami (Natural Language) menjadi format JSON standar.
* **🔄 Smart Upsert Logic:** Algoritma cerdas yang mendeteksi duplikasi data berdasarkan NIM (Nomor Induk Mahasiswa). Jika data sudah ada, sistem akan melakukan *Update*; jika belum, akan melakukan *Insert*.
* **🚫 Anti-Hallucination:** Dilengkapi filter validasi Python untuk mencegah AI menghasilkan data sampah/halusinasi.
* **📊 Interactive Dashboard:** Antarmuka web modern berbasis **Streamlit** dengan fitur feedback real-time dan export data.

---

## 🛠️ Teknologi yang Digunakan

* **Bahasa Pemrograman:** Python 3.x
* **Interface:** Streamlit
* **AI Engine:** Ollama (Llama 3.2 - 3B Parameters)
* **Data Processing:** Pandas
* **Format Pertukaran Data:** JSON & CSV

---

## ⚙️ Prasyarat (Wajib Dibaca)

Sebelum menjalankan kode Python, Anda **WAJIB** menyiapkan *Environment AI* terlebih dahulu:

1. **Instal Aplikasi Ollama**
* Unduh dan instal aplikasi desktop Ollama dari [ollama.com](https://ollama.com).
* Pastikan aplikasi berjalan di background (ikon Ollama muncul di taskbar).


2. **Download Model Llama 3.2**
Buka terminal/CMD, lalu jalankan perintah berikut untuk mengunduh model otak AI-nya:
```bash
ollama pull llama3.2

```



---

## 🚀 Panduan Instalasi

1. **Clone Repository**
```bash
git clone https://github.com/username-anda/nama-repo-anda.git
cd nama-repo-anda

```


2. **Buat Virtual Environment (Disarankan)**
Supaya library tidak tercampur dengan sistem utama laptop.
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate

```


3. **Install Library Python**
```bash
pip install streamlit pandas ollama

```



---

## 🖥️ Cara Menjalankan Aplikasi

Aplikasi ini memiliki antarmuka berbasis Web (Streamlit).

1. Pastikan aplikasi **Ollama** sudah berjalan.
2. Buka terminal di dalam folder proyek, lalu ketik:
```bash
streamlit run dashboard.py

```


3. Browser akan otomatis terbuka di alamat `http://localhost:8501`.

---

## 📖 Cara Penggunaan

### 1. Panel Input (Kiri)

Masukkan instruksi atau laporan teks pada kolom yang tersedia.

**Contoh Input Valid:**

> *"Tolong catat mahasiswa baru atas nama Siti Aminah, NIM 10245, dengan Nilai Akhir 90. Tambahkan keterangan 'Lulus Cumlaude'."*

**Contoh Update Data:**

> *"Revisi nilai untuk NIM 10245 menjadi 95 karena ada penambahan tugas."*

### 2. Panel Output (Kanan)

* Tabel akan menampilkan data secara *real-time*.
* Data disimpan otomatis ke file `data_akademik.csv`.
* Anda bisa mengunduh file CSV melalui tombol **"Unduh Laporan"**.

---

## 📂 Struktur Folder

```
├── dashboard.py         # Kode Utama (Frontend & Backend Logic)
├── data_akademik.csv    # Database File (Terbuat Otomatis)
├── README.md            # Dokumentasi Proyek
└── requirements.txt     # Daftar Library (Opsional)

```

---

## 🐛 Troubleshooting

* **Error: `ollama.ConnectionError**`
* *Solusi:* Aplikasi Ollama Desktop belum berjalan. Buka aplikasinya terlebih dahulu.


* **Error: `Model not found**`
* *Solusi:* Anda belum menarik modelnya. Jalankan `ollama pull llama3.2` di terminal.


* **Data tidak masuk ke tabel?**
* *Solusi:* Cek format input Anda. Pastikan mengandung minimal **Nama** dan **NIM**.



---