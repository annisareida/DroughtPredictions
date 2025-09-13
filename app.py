import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# =================================================================================
# KONFIGURASI HALAMAN DAN DATA
# =================================================================================

# Konfigurasi dasar halaman Streamlit
st.set_page_config(
    page_title="Prediksi Kekeringan Ogan Ilir",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# [DIUBAH] Definisi 7 Kelas Kekeringan yang baru sesuai data Anda
# Kunci dictionary sekarang adalah string dari CSV, bukan angka
DROUGHT_CLASSES = {
    "Sangat Basah":      {"desc": "Kondisi tanah sangat jenuh air, potensi banjir atau genangan tinggi.", "color": "#154360"},
    "Basah Ekstrem":     {"desc": "Curah hujan sangat tinggi, melebihi kapasitas normal tanah.", "color": "#1A5276"},
    "Basah Sedang":      {"desc": "Kondisi lebih basah dari biasanya, pasokan air melimpah.", "color": "#4E80B4"},
    "Normal":            {"desc": "Kondisi hidrologi seimbang, ideal untuk pertanian dan ketersediaan air.", "color": "#2ECC71"},
    "Kering Sedang":     {"desc": "Kekeringan tingkat sedang, perlu kewaspadaan pada sektor pertanian.", "color": "#F39C12"},
    "Kering Parah":      {"desc": "Kekeringan parah, sumber air permukaan menurun drastis.", "color": "#E67E22"},
    "Kering Sangat Parah": {"desc": "Kondisi darurat kekeringan, krisis air meluas dan risiko kebakaran tinggi.", "color": "#C0392B"}
}

# [DIUBAH] Mapping kelas dari Teks ke Angka untuk kebutuhan plotting grafik
# Urutan angka menentukan posisi di sumbu Y grafik
CLASS_TO_NUMERIC = {
    "Sangat Basah": 1,
    "Basah Ekstrem": 2,
    "Basah Sedang": 3,
    "Normal": 4,
    "Kering Sedang": 5,
    "Kering Parah": 6,
    "Kering Sangat Parah": 7
}
# Kebalikannya, untuk memberi label pada sumbu Y grafik
NUMERIC_TO_CLASS_LABELS = list(CLASS_TO_NUMERIC.keys())


# [DIUBAH] Direktori data disesuaikan dengan path yang Anda berikan
# r"..." digunakan agar path Windows dapat dibaca dengan benar oleh Python
DATA_DIR = "dataset"

# [DIUBAH] Daftar 15 Kecamatan (pastikan nama file CSV sesuai)
# Contoh: "Indralaya" akan membaca file "indralaya.csv"
KECAMATAN_FILES = {
    "Indralaya": "indralaya.csv",
    "Indralaya Utara": "indralaya_utara.csv",
    "Indralaya Selatan": "indralaya_selatan.csv",
    "Tanjung Batu": "tanjung_batu.csv",
    "Tanjung Raja": "tanjung_raja.csv",
    "Rantau Alai": "rantau_alai.csv",
    "Rantau Panjang": "rantau_panjang.csv",
    "Sungai Pinang": "sungai_pinang.csv",
    "Pemulutan": "pemulutan.csv",
    "Pemulutan Barat": "pemulutan_barat.csv",
    "Pemulutan Selatan": "pemulutan_selatan.csv",
    "Kandis": "kandis.csv",
    "Payaraman": "payaraman.csv",
    "Muara Kuang": "Muara Kuang.csv",
    "Lubuk Keliat": "lubuk_keliat.csv"
}

# =================================================================================
# FUNGSI BANTUAN
# =================================================================================

# [DIUBAH TOTAL] Fungsi untuk memuat data disesuaikan dengan format CSV baru
@st.cache_data
def load_data(file_path):
    """
    Memuat data dari file CSV 1 kolom, tanpa header.
    Membuat kolom Tanggal secara otomatis.
    Memetakan kelas teks ke numerik untuk plotting.
    """
    try:
        # Baca CSV 1 kolom tanpa header, beri nama kolom 'Kelas_Kekeringan'
        df = pd.read_csv(file_path, header=None, names=['Kelas_Kekeringan'])
        
        # Buat kolom Tanggal. Asumsi data dimulai dari 1 Januari 2023
        # Sesuaikan start_date jika data Anda dimulai dari tanggal lain
        start_date = "2024-12-31"
        num_rows = len(df)
        df['Tanggal'] = pd.date_range(start=start_date, periods=num_rows, freq='D')

        # Buat kolom numerik untuk diplot di grafik
        df['Kelas_Numerik'] = df['Kelas_Kekeringan'].map(CLASS_TO_NUMERIC)
        
        return df
        
    except FileNotFoundError:
        st.error(f"File data tidak ditemukan di path: {file_path}. Pastikan nama file CSV sudah benar dan folder dataset ada.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
        return None

# =================================================================================
# TAMPILAN UTAMA APLIKASI
# =================================================================================

# --- HEADER ---
st.title("☀️ Dashboard Prediksi Kekeringan Ogan Ilir")
st.markdown("Analisis dan visualisasi data prediksi tingkat kekeringan per kecamatan di Kabupaten Ogan Ilir.")
st.markdown("---")

# --- SIDEBAR (PANEL KONTROL) ---
st.sidebar.header("⚙️ Panel Kontrol")
selected_kecamatan_name = st.sidebar.selectbox(
    "Pilih Kecamatan:",
    options=list(KECAMATAN_FILES.keys()),
    index=0
)

# Memuat data berdasarkan pilihan kecamatan
file_name = KECAMATAN_FILES[selected_kecamatan_name]
file_path = os.path.join(DATA_DIR, file_name)
df = load_data(file_path)

if df is not None:
    # Pilihan tanggal di sidebar
    selected_date = st.sidebar.date_input(
        "Pilih Tanggal Prediksi:",
        value=df['Tanggal'].max(), # Default ke tanggal terbaru
        min_value=df['Tanggal'].min(),
        max_value=df['Tanggal'].max()
    )
    selected_date = pd.to_datetime(selected_date).normalize() # normalize() untuk hapus info jam/menit

    # --- TAMPILAN UTAMA (MAIN AREA) ---
    st.header(f"📍 Status Prediksi di Kecamatan: **{selected_kecamatan_name}**")
    st.caption(f"Data untuk tanggal: **{selected_date.strftime('%d %B %Y')}**")

    # Ambil data untuk tanggal yang dipilih
    prediction_data = df[df['Tanggal'] == selected_date]

    if not prediction_data.empty:
        # Dapatkan kelas kekeringan (sekarang berupa string)
        current_class = prediction_data['Kelas_Kekeringan'].iloc[0]
        class_info = DROUGHT_CLASSES[current_class]

        # Tampilkan status dengan metrik dan warna
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric(
                label="Level Prediksi",
                value=current_class, # Langsung tampilkan nama kelasnya
            )
        with col2:
            st.markdown(
                f"""
                <div style="background-color: {class_info['color']}; padding: 20px; border-radius: 10px; text-align: center; height: 100%;">
                    <h3 style="color: white; margin: 0;">{current_class}</h3>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.info(f"**💡 Deskripsi:** {class_info['desc']}")

    else:
        st.warning("Tidak ada data prediksi untuk tanggal yang dipilih.")

    st.markdown("---")

    # --- GRAFIK INTERAKTIF ---
    st.header("📈 Grafik Historis Tingkat Kekeringan")
    st.markdown(f"Visualisasi tren prediksi kekeringan di **Kecamatan {selected_kecamatan_name}** dari waktu ke waktu.")

    fig = px.line(
        df,
        x='Tanggal',
        y='Kelas_Numerik', # [DIUBAH] Gunakan kolom numerik untuk sumbu Y
        markers=True,
        labels={"Tanggal": "Periode Waktu", "Kelas_Numerik": "Level Kekeringan"},
        custom_data=['Kelas_Kekeringan'], # Kirim nama kelas asli untuk ditampilkan di hover
        template="plotly_white"
    )

    # Kustomisasi tampilan grafik
    fig.update_traces(
        # [DIUBAH] Tampilkan nama kelas asli saat hover
        hovertemplate="<b>Tanggal:</b> %{x|%d %B %Y}<br><b>Level:</b> %{customdata[0]}<extra></extra>"
    )

    fig.update_layout(
        # [DIUBAH] Tampilkan label teks di sumbu Y, bukan angka
        yaxis=dict(
            tickmode='array',
            tickvals=list(CLASS_TO_NUMERIC.values()),
            ticktext=NUMERIC_TO_CLASS_LABELS
        ),
        title={'text': f"Tren Kekeringan di {selected_kecamatan_name}", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- PENJELASAN KELAS KEKERINGAN ---
    st.markdown("---")
    with st.expander("ℹ️ Klik di sini untuk melihat penjelasan setiap kelas kekeringan"):
        for class_name, info in DROUGHT_CLASSES.items():
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                    <div style="width: 20px; height: 20px; background-color: {info['color']}; border-radius: 5px; margin-right: 10px;"></div>
                    <div><b>{class_name}:</b> {info['desc']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

else:
    st.error("Gagal memuat data. Mohon periksa kembali path folder dan nama file CSV Anda.")
