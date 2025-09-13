import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, date

# = an================================================================================
# KONFIGURASI HALAMAN DAN DATA
# =================================================================================

st.set_page_config(
    page_title="Prediksi Kekeringan Ogan Ilir",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deskripsi dan saran disesuaikan untuk pertanian & musim tanam
DROUGHT_CLASSES = {
    "Sangat Basah": {
        "desc": "Kondisi tanah sangat jenuh air. Risiko tinggi busuk akar dan serangan jamur. Lahan sawah tergenang.",
        "saran": "Tunda penanaman. Perbaiki drainase lahan. Waspada serangan hama seperti keong mas.",
        "color": "#154360"
    },
    "Basah Ekstrem": {
        "desc": "Curah hujan sangat tinggi. Pertumbuhan tanaman palawija terhambat. Penyerbukan bunga dapat terganggu.",
        "saran": "Pastikan drainase optimal. Tunda pemupukan untuk menghindari pencucian hara. Pantau kelembaban.",
        "color": "#1A5276"
    },
    "Basah Sedang": {
        "desc": "Kondisi sangat baik untuk memulai musim tanam padi sawah. Ketersediaan air melimpah.",
        "saran": "Waktu ideal untuk pengolahan lahan basah dan tanam padi. Hemat air untuk persiapan masa depan.",
        "color": "#4E80B4"
    },
    "Normal": {
        "desc": "Kondisi hidrologi seimbang. Ideal untuk pertumbuhan vegetatif tanaman padi dan palawija.",
        "saran": "Lakukan pemupukan dan penyiangan sesuai jadwal. Pertahankan jadwal irigasi normal.",
        "color": "#2ECC71"
    },
    "Kering Sedang": {
        "desc": "Kandungan air tanah mulai menurun. Tanaman mulai menunjukkan gejala stres ringan (daun sedikit layu di siang hari).",
        "saran": "Mulai terapkan irigasi hemat air (misal: irigasi selang-seling). Pertimbangkan tanam palawija hemat air.",
        "color": "#F39C12"
    },
    "Kering Parah": {
        "desc": "Kekeringan mulai merusak tanaman. Pertumbuhan terhambat, potensi gagal panen meningkat.",
        "saran": "Prioritaskan air untuk fase kritis tanaman (pembungaan/pengisian biji). Lakukan penyiraman di pagi/sore hari.",
        "color": "#E67E22"
    },
    "Kering Sangat Parah": {
        "desc": "Krisis air, potensi gagal panen total (puso). Tanah retak dan sangat keras.",
        "saran": "Fokus penyelamatan tanaman yang masih bisa produktif. Siapkan lahan untuk musim tanam berikutnya (menunggu hujan).",
        "color": "#C0392B"
    }
}


CLASS_TO_NUMERIC = { "Sangat Basah": 1, "Basah Ekstrem": 2, "Basah Sedang": 3, "Normal": 4, "Kering Sedang": 5, "Kering Parah": 6, "Kering Sangat Parah": 7 }
NUMERIC_TO_CLASS_LABELS = list(CLASS_TO_NUMERIC.keys())
DATA_DIR = "dataset"

# Pastikan nama file "Muara Kuang.csv" sudah benar, termasuk spasinya
KECAMATAN_FILES = {
    "Indralaya": "indralaya.csv", "Indralaya Utara": "indralaya_utara.csv", "Indralaya Selatan": "indralaya_selatan.csv",
    "Tanjung Batu": "tanjung_batu.csv", "Tanjung Raja": "tanjung_raja.csv", "Rantau Alai": "rantau_alai.csv",
    "Rantau Panjang": "rantau_panjang.csv", "Sungai Pinang": "sungai_pinang.csv", "Pemulutan": "pemulutan.csv",
    "Pemulutan Barat": "pemulutan_barat.csv", "Pemulutan Selatan": "pemulutan_selatan.csv", "Kandis": "kandis.csv",
    "Payaraman": "payaraman.csv", "Muara Kuang": "Muara Kuang.csv", "Lubuk Keliat": "lubuk_keliat.csv"
}

# =================================================================================
# FUNGSI BANTUAN
# =================================================================================

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, header=None, names=['Kelas_Kekeringan'])
        
        # [DIUBAH] Logika dikembalikan agar data masa depan (prediksi) bisa ditampilkan
        # Tanggal akan dibuat untuk seluruh baris data tanpa dipotong oleh tanggal hari ini.
        start_date = "2024-31-12"
        num_rows = len(df)
        df['Tanggal'] = pd.date_range(start=start_date, periods=num_rows, freq='D')

        df['Kelas_Numerik'] = df['Kelas_Kekeringan'].map(CLASS_TO_NUMERIC)
        
        return df
        
    except FileNotFoundError:
        st.error(f"File data tidak ditemukan: {file_path}. Pastikan nama file benar dan folder '{DATA_DIR}' ada.")
        return None
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memuat data: {e}")
        return None

# =================================================================================
# TAMPILAN UTAMA APLIKASI
# =================================================================================

# --- HEADER ---
st.title("☀️ Dashboard Prediksi Kekeringan Pertanian Ogan Ilir")
st.markdown("Analisis dan visualisasi data prediksi tingkat kekeringan untuk mendukung keputusan pertanian di Kabupaten Ogan Ilir.")
st.markdown("---")

# --- SIDEBAR (PANEL KONTROL) ---
st.sidebar.header("⚙️ Panel Kontrol")
selected_kecamatan_name = st.sidebar.selectbox(
    "Pilih Kecamatan:",
    options=list(KECAMATAN_FILES.keys()),
    index=0
)

file_name = KECAMATAN_FILES[selected_kecamatan_name]
file_path = os.path.join(DATA_DIR, file_name)
df = load_data(file_path)

if df is not None and not df.empty:
    selected_date = st.sidebar.date_input(
        "Pilih Tanggal Prediksi:",
        value=df['Tanggal'].max(), # Default ke tanggal terbaru dalam data
        min_value=df['Tanggal'].min(),
        max_value=df['Tanggal'].max()  # max_value sekarang adalah tanggal terakhir dari data prediksi
    )
    selected_date = pd.to_datetime(selected_date).normalize()

    # --- TAMPILAN UTAMA (MAIN AREA) ---
    st.header(f"📍 Status Prediksi di Kecamatan: **{selected_kecamatan_name}**")
    st.caption(f"Data untuk tanggal: **{selected_date.strftime('%d %B %Y')}**")

    prediction_data = df[df['Tanggal'] == selected_date]

    if not prediction_data.empty:
        current_class = prediction_data['Kelas_Kekeringan'].iloc[0]
        class_info = DROUGHT_CLASSES.get(current_class, {"desc": "Kelas tidak dikenal.", "saran": "Periksa kembali data.", "color": "#808080"})

        # Tampilkan status dengan metrik dan warna
        col1, col2 = st.columns([1, 2])
        with col1:
             st.markdown(f"##### Level Prediksi")
             st.markdown(
                f"""
                <div style="background-color: {class_info['color']}; padding: 25px; border-radius: 10px; text-align: center;">
                    <h2 style="color: white; margin: 0; font-weight: bold;">{current_class}</h2>
                </div>
                """, unsafe_allow_html=True
            )
        with col2:
            st.markdown("##### Deskripsi Kondisi Pertanian")
            st.info(f"**“** {class_info['desc']} **”**")
            st.markdown("##### Saran / Tindakan Pertanian")
            st.warning(f"**💡** {class_info['saran']}")

    else:
        st.warning("Tidak ada data prediksi untuk tanggal yang dipilih.")

    st.markdown("---")

    # --- GRAFIK INTERAKTIF ---
    st.header("📈 Grafik Historis dan Prediksi Tingkat Kekeringan")
    st.markdown(f"Visualisasi tren kekeringan di **Kecamatan {selected_kecamatan_name}**.")

    fig = px.line(
        df, x='Tanggal', y='Kelas_Numerik', markers=True,
        labels={"Tanggal": "Periode Waktu", "Kelas_Numerik": "Level Kekeringan"},
        custom_data=['Kelas_Kekeringan'], template="plotly_white"
    )
    fig.update_traces(hovertemplate="<b>Tanggal:</b> %{x|%d %B %Y}<br><b>Level:</b> %{customdata[0]}<extra></extra>")
    fig.update_layout(
        yaxis=dict(tickmode='array', tickvals=list(CLASS_TO_NUMERIC.values()), ticktext=NUMERIC_TO_CLASS_LABELS),
        title={'text': f"Tren Kekeringan di {selected_kecamatan_name}", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- PENJELASAN KELAS KEKERINGAN ---
    st.markdown("---")
    with st.expander("ℹ️ Klik di sini untuk melihat penjelasan detail setiap kelas kekeringan"):
        for class_name, info in DROUGHT_CLASSES.items():
            st.markdown(f"""
            <div style="display: flex; align-items: top; margin-bottom: 12px; border-left: 5px solid {info['color']}; padding-left: 10px;">
                <div>
                    <b style="font-size: 1.1em;">{class_name}</b><br>
                    <b>Deskripsi:</b> {info['desc']}<br>
                    <b>Saran:</b> {info['saran']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
    # --- BAGIAN LOGO ---
    st.markdown("---")
    st.subheader("Didukung Oleh:")

    # Ganti nama file 'logoX.png' dengan nama file logo Anda yang sebenarnya
    logo_files = [
        "logos/logo1.png", "logos/logo2.png", "logos/logo3.png", "logos/logo4.png",
        "logos/logo5.png", "logos/logo6.jpg", "logos/logo7.png"
    ]

    # Bagi menjadi dua baris, masing-masing 4 kolom
    row1_cols = st.columns(4)
    row2_cols = st.columns(4)

    for i, col in enumerate(row1_cols):
        if i < len(logo_files):
            try:
                col.image(logo_files[i], use_container_width='auto')
            except Exception as e:
                col.warning(f"Logo {i+1} gagal dimuat.")

    for i, col in enumerate(row2_cols):
        if (i+4) < len(logo_files):
            try:
                col.image(logo_files[i+4], use_container_width='auto')
            except Exception as e:
                col.warning(f"Logo {i+5} gagal dimuat.")


elif df is None:
    st.error("Gagal memuat data. Silakan periksa pesan error di atas.")
else:
    st.warning("Data untuk kecamatan ini kosong atau tidak valid.")
