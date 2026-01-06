import streamlit as st
import pandas as pd
import ollama
import json
import os
import time

# --- 1. KONFIGURASI SISTEM ---
if 'SSL_CERT_FILE' in os.environ:
    del os.environ['SSL_CERT_FILE']

MODEL_AI = "llama3.2" 
FILE_DATABASE = "data_akademik.csv"

# Pengaturan Halaman (Page Config)
st.set_page_config(
    page_title="Sistem Manajemen Data Akademik",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LOGIKA BACKEND (AI & DATABASE) ---

def extract_with_ai(teks_mentah):
    """
    Fungsi Ekstraksi Entitas Menggunakan LLM Lokal (Versi Robust).
    """
    # System Prompt: Menggunakan Data Dummy untuk mencegah halusinasi
    system_instruction = """
    PERAN: Anda adalah DATA PARSER ENGINE.
    TUGAS: Analisis teks input dan konversi menjadi struktur JSON.
    
    ATURAN VALIDASI:
    1. Identifikasi entitas: Nama, NIM, Nilai, dan Keterangan.
    2. Gabungkan entitas dalam satu konteks kalimat menjadi satu objek.
    3. NIM harus berupa STRING angka murni.
    4. JANGAN menyalin teks instruksi (misal: 'String Nomor'). Gunakan data riil.
    5. JANGAN buat data fiktif. Hanya ekstrak dari teks yang diberikan.
    6. JANGAN BERIKAN DATA DARI CONTOH JIKA KAMU TIDAK BISA JAWAB CUKUP BERIKAN JSON KOSONG.
    
    CONTOH OUTPUT JSON (Ikuti pola struktur ini):
    {
        "data": [
            {
                "nama": "Budi Santoso", 
                "nim": "101234", 
                "nilai": 85, 
                "keterangan": "Tugas Tambahan"
            }
        ]
    }
    """
    
    try:
        response = ollama.chat(
            model=MODEL_AI, 
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': teks_mentah}
            ],
            format='json' # Fitur Native JSON Ollama
        )
        
        raw_output = response['message']['content']
        parsed_json = json.loads(raw_output)
        
        # Normalisasi Struktur Data
        data_list = []
        if isinstance(parsed_json, dict):
            if "data" in parsed_json:
                data_list = parsed_json["data"]
            else:
                data_list = [parsed_json]
        elif isinstance(parsed_json, list):
            data_list = parsed_json
            
        # Sanitasi Data (Pembersihan Key & Anti-Halusinasi)
        final_data = []
        for item in data_list:
            nama = item.get("nama") or item.get("name")
            nim_raw = str(item.get("nim") or item.get("id") or "")
            nilai = item.get("nilai") or item.get("score")
            ket = item.get("keterangan") or item.get("note") or ""
            
            # Filter Python: Hapus jika NIM berisi teks aneh (akibat halusinasi AI)
            if "string" in nim_raw.lower() or "nomor" in nim_raw.lower():
                nim_raw = ""

            # Validasi: Hanya simpan jika minimal ada NIM (dan NIM bukan kosong)
            if nim_raw and nim_raw != "None" and nim_raw != "":
                final_data.append({
                    "nama": nama,
                    "nim": nim_raw,
                    "nilai": nilai,
                    "keterangan": ket
                })
                
        return final_data
            
    except Exception as e:
        return None

def update_database(data_baru):
    """
    Mekanisme Penyimpanan Data (Upsert Operation).
    """
    try:
        if isinstance(data_baru, dict):
            data_baru = [data_baru]
            
        new_df = pd.DataFrame(data_baru)
        
        if 'nim' not in new_df.columns or new_df.empty:
            return 0, 0
            
        new_df['nim'] = new_df['nim'].astype(str)
        rows_added = 0
        rows_updated = 0

        if os.path.exists(FILE_DATABASE):
            existing_df = pd.read_csv(FILE_DATABASE)
            existing_df['nim'] = existing_df['nim'].astype(str)

            existing_nims = existing_df['nim'].tolist()
            new_nims = new_df['nim'].tolist()
            
            # Hitung statistik
            rows_updated = len(set(new_nims).intersection(existing_nims))
            rows_added = len(set(new_nims) - set(existing_nims))

            existing_df.set_index('nim', inplace=True)
            new_df.set_index('nim', inplace=True)

            # Update data lama
            existing_df.update(new_df)
            
            # Tambah data baru
            baris_baru = new_df[~new_df.index.isin(existing_df.index)]
            combined_df = pd.concat([existing_df, baris_baru])
            
            combined_df.reset_index(inplace=True)
            combined_df.to_csv(FILE_DATABASE, index=False)
        else:
            new_df.to_csv(FILE_DATABASE, index=False)
            rows_added = len(new_df)
            
        return rows_added, rows_updated
            
    except Exception as e:
        st.error(f"Kesalahan Sistem Database: {e}")
        return 0, 0

# --- 3. ANTARMUKA PENGGUNA (UI PROFESSIONAL) ---

# Sidebar: Panduan & Informasi Lengkap
with st.sidebar:
    st.header("📘 Panduan Sistem")
    
    st.markdown("### 1. Standar Input")
    st.info("""
    Sistem memproses instruksi bahasa alami (*Natural Language*). 
    Pastikan input mengandung 3 elemen kunci:
    - **Nama Lengkap**
    - **NIM** (Identifikasi Unik)
    - **Nilai** (Numerik)
    """)
    
    st.markdown("### 2. Contoh Perintah Valid")
    with st.expander("Lihat Contoh Format"):
        st.markdown("**Input Data Baru:**")
        st.code("Input nilai mahasiswa baru: Putri (NIM 105), Nilai Akhir 88.", language="text")
        
        st.markdown("**Update Data Lama:**")
        st.code("Revisi nilai untuk NIM 105 menjadi 95 karena ada tugas tambahan.", language="text")
        
        st.markdown("**Input Kolektif (Bulk):**")
        st.code("""
        Daftar Nilai:
        1. Andi (101) - 80
        2. Budi (102) - 90
        """, language="text")

    st.markdown("### 3. Catatan Teknis")
    st.warning("""
    - **NIM Unik:** Data dengan NIM sama akan menimpa data lama (Update).
    - **Format Angka:** Gunakan angka biasa (80), bukan teks (delapan puluh).
    """)
    
    st.divider()
    st.caption(f"Backend Engine: **{MODEL_AI}**")
    st.caption("Environment: Local (Offline)")

# Main Content
st.title("Sistem Digitalisasi Data Akademik")
st.markdown("Dashboard Konversi Data Tidak Terstruktur ke Database Relasional")
st.divider()

col_input, col_table = st.columns([1, 1.5], gap="large")

with col_input:
    st.subheader("Panel Input Data")
    
    # clear_on_submit=False (Agar teks tidak hilang saat error/cek ulang)
    with st.form("form_input_data", clear_on_submit=False):
        teks_input = st.text_area(
            "Instruksi / Data Teks:",
            height=250,
            placeholder="Ketik data di sini...\nContoh: Masukkan nilai 80 untuk mahasiswa Andi dengan NIM 12345.",
            help="Masukkan teks laporan, chat, atau catatan notulensi di sini."
        )
        
        btn_submit = st.form_submit_button("Proses & Simpan", type="primary")

    if btn_submit and teks_input:
        # Menggunakan Status Container untuk tampilan loading yang rapi
        with st.status("Sedang memproses data...", expanded=True) as status:
            st.write("Menganalisis struktur teks...")
            hasil_ekstraksi = extract_with_ai(teks_input)
            
            if hasil_ekstraksi:
                st.write(f"Validasi: Ditemukan {len(hasil_ekstraksi)} entitas data.")
                added, updated = update_database(hasil_ekstraksi)
                status.update(label="Proses Selesai", state="complete", expanded=False)
                
                # Feedback Hasil
                if added > 0 or updated > 0:
                    st.success(f"Laporan Transaksi: {added} Data Baru, {updated} Data Diperbarui.")
                    time.sleep(1.5) 
                    st.rerun() 
                else:
                    st.warning("Data valid terbaca, namun tidak ada perubahan pada database (Data Identik).")
            else:
                status.update(label="Gagal Memproses", state="error")
                st.error("Gagal mengekstrak data. Pastikan format input mengandung NIM dan Nama yang jelas.")

with col_table:
    st.subheader("Database Mahasiswa (Live)")
    
    if os.path.exists(FILE_DATABASE):
        df = pd.read_csv(FILE_DATABASE)
        
        # Tampilkan Total Data
        st.markdown(f"**Total Entitas:** `{len(df)}` Mahasiswa")
        
        # Tampilkan Tabel dengan Konfigurasi Kolom
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nim": st.column_config.TextColumn("NIM", width="medium"),
                "nama": st.column_config.TextColumn("Nama Lengkap", width="large"),
                "nilai": st.column_config.NumberColumn("Nilai", format="%d"),
                "keterangan": st.column_config.TextColumn("Keterangan")
            }
        )
        
        # Tombol Download
        with open(FILE_DATABASE, "rb") as f:
            st.download_button(
                label="Unduh Laporan (.csv)",
                data=f,
                file_name="rekap_data_akademik.csv",
                mime="text/csv"
            )
    else:
        st.info("Database belum tersedia. Silakan lakukan input data pertama.")