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

# Pengaturan Halaman (Page Config) - Formal
st.set_page_config(
    page_title="Sistem Informasi Akademik - Input Cerdas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. LOGIKA BACKEND (AI & DATABASE) ---

def extract_with_ai(teks_mentah):
    """
    Fungsi Ekstraksi Entitas Menggunakan LLM Lokal.
    """
    # System Prompt dibuat sangat instruktif dan kaku untuk akurasi
    system_instruction = """
    PERAN: Anda adalah ENGINES PARSER DATA AKADEMIK.
    
    TUGAS: 
    Analisis teks input dan konversi menjadi format JSON standar.
    
    ATURAN VALIDASI:
    1. Identifikasi entitas: Nama, NIM, Nilai, dan Keterangan.
    2. Gabungkan entitas yang tersebar dalam satu konteks kalimat menjadi satu objek.
    3. NIM wajib dikonversi menjadi format String.
    4. Jika angka nilai tergabung dengan teks (contoh: 'nilai80'), pisahkan menjadi integer.
    5. Jangan membuat data fiktif. Jika informasi tidak ada, isi dengan null atau string kosong.

    FORMAT OUTPUT JSON:
    {
        "data": [
            {
                "nama": "String Nama Lengkap", 
                "nim": "String Nomor Induk", 
                "nilai": Integer, 
                "keterangan": "String Catatan"
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
            format='json' 
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
            
        # Sanitasi Data (Pembersihan Key)
        final_data = []
        for item in data_list:
            nama = item.get("nama") or item.get("name")
            nim = str(item.get("nim") or item.get("id") or "")
            nilai = item.get("nilai") or item.get("score")
            ket = item.get("keterangan") or item.get("note") or ""
            
            # Validasi Kelayakan Data (Minimal ada NIM atau Nama)
            if (nama or (nim and nim != "None" and nim != "")):
                final_data.append({
                    "nama": nama,
                    "nim": nim,
                    "nilai": nilai,
                    "keterangan": ket
                })
                
        return final_data
            
    except Exception as e:
        return None

def update_database(data_baru):
    """
    Mekanisme Penyimpanan Data (Upsert Operation).
    Mengembalikan jumlah baris baru dan baris yang diperbarui.
    """
    try:
        if isinstance(data_baru, dict):
            data_baru = [data_baru]
            
        new_df = pd.DataFrame(data_baru)
        
        if 'nim' not in new_df.columns:
            return 0, 0
            
        new_df['nim'] = new_df['nim'].astype(str)

        rows_added = 0
        rows_updated = 0

        if os.path.exists(FILE_DATABASE):
            existing_df = pd.read_csv(FILE_DATABASE)
            existing_df['nim'] = existing_df['nim'].astype(str)

            # Identifikasi data baru vs update
            existing_nims = existing_df['nim'].tolist()
            new_nims = new_df['nim'].tolist()
            
            rows_updated = len(set(new_nims).intersection(existing_nims))
            rows_added = len(set(new_nims) - set(existing_nims))

            existing_df.set_index('nim', inplace=True)
            new_df.set_index('nim', inplace=True)

            existing_df.update(new_df)
            
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

# Sidebar: Panduan & Informasi
with st.sidebar:
    st.header("Panduan Pengguna")
    st.markdown("""
    **Format Penulisan Input:**
    Sistem menggunakan *Natural Language Processing*. Pastikan input Anda mengandung informasi kunci:
    1. **Nama Mahasiswa**
    2. **NIM** (Nomor Induk Mahasiswa)
    3. **Nilai** (Angka)
    
    **Contoh Input Valid:**
    > *"Update nilai tugas akhir mahasiswa Budi (NIM 101) menjadi 85."*
    
    > *"Input data baru: Siti Aminah, NIM 102, Nilai 90. Tambahkan keterangan 'Lulus dengan Pujian'."*
    """)
    st.divider()
    st.caption(f"Engine: {MODEL_AI} (Local Inference)")
    st.caption("Status Sistem: Aktif")

# Main Content
st.title("Sistem Digitalisasi Data Akademik")
st.markdown("Modul Konversi Data Tidak Terstruktur ke Database Terelasi")
st.divider()

col_input, col_table = st.columns([1, 1.5], gap="large")

with col_input:
    st.subheader("Panel Input Data")
    
    with st.form("form_input_data", clear_on_submit=True):
        teks_input = st.text_area(
            "Masukkan instruksi atau data teks:",
            height=200,
            placeholder="Ketik data di sini. Contoh: Masukkan nilai 80 untuk mahasiswa Andi dengan NIM 12345...",
            help="Area ini menerima input teks bebas (paragraf, list, atau chat)."
        )
        
        # Tombol submit yang bersih
        btn_submit = st.form_submit_button("Proses & Simpan Data", type="primary")

    if btn_submit and teks_input:
        with st.status("Sedang memproses data...", expanded=True) as status:
            st.write("Menganalisis struktur teks...")
            hasil_ekstraksi = extract_with_ai(teks_input)
            
            if hasil_ekstraksi:
                st.write("Melakukan validasi entitas...")
                added, updated = update_database(hasil_ekstraksi)
                status.update(label="Proses Selesai", state="complete", expanded=False)
                
                # Feedback yang profesional
                if added > 0 or updated > 0:
                    st.success(f"Laporan Transaksi: {added} data baru ditambahkan, {updated} data diperbarui.")
                    time.sleep(1) # Jeda sedikit agar user membaca
                    st.rerun()
                else:
                    st.warning("Data terbaca namun tidak ada perubahan pada database (Duplikasi identik).")
            else:
                status.update(label="Gagal Memproses", state="error")
                st.error("Sistem tidak dapat mengidentifikasi entitas data. Mohon periksa format input Anda.")

with col_table:
    st.subheader("Tabel Data Mahasiswa")
    
    if os.path.exists(FILE_DATABASE):
        df = pd.read_csv(FILE_DATABASE)
        
        # Menampilkan total data
        st.markdown(f"*Total Data Tersimpan: {len(df)} Mahasiswa*")
        
        # Tabel yang rapi
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "nim": st.column_config.TextColumn("NIM", width="medium"),
                "nama": st.column_config.TextColumn("Nama Lengkap", width="large"),
                "nilai": st.column_config.NumberColumn("Nilai Akhir", format="%d"),
                "keterangan": st.column_config.TextColumn("Keterangan Tambahan")
            }
        )
        
        # Tombol Unduh
        with open(FILE_DATABASE, "rb") as f:
            st.download_button(
                label="Unduh Laporan (.csv)",
                data=f,
                file_name="rekap_nilai_mahasiswa.csv",
                mime="text/csv"
            )
    else:
        st.info("Database kosong. Silakan lakukan input data melalui panel di sebelah kiri.")