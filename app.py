import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, date

# =================================================================================
# KONFIGURASI HALAMAN DAN DATA
# =================================================================================

st.set_page_config(
    page_title="Prediksi Kekeringan Ogan Ilir",
    page_icon="logos/logo7.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Kondisi Pertanian Padi dan Saran Berdasarkan Kelas SPI
DROUGHT_CLASSES = {
    "Sangat Basah": {
        "desc": "Sawah mengalami kelebihan air dan genangan yang dapat merusak akar, memperlambat pertumbuhan, serta meningkatkan risiko serangan penyakit akibat kelembaban tinggi.",
        "saran": "Perbaiki drainase, buat saluran pembuangan tambahan, dan lakukan pengendalian hama/penyakit secara intensif.",
        "color": "#154360"
    },
    "Basah Ekstrem": {
        "desc": "Ketersediaan air sangat tinggi, sawah rentan tergenang lama sehingga fase awal pertumbuhan padi terganggu.",
        "saran": "Pastikan irigasi berfungsi baik, lakukan pengeringan jika perlu, dan atur jadwal tanam agar tidak bertepatan dengan puncak hujan.",
        "color": "#1A5276"
    },
    "Basah Sedang": {
        "desc": "Kondisi air melimpah dan relatif stabil, cukup baik untuk pertumbuhan padi, namun genangan masih mungkin terjadi pada lahan dengan drainase buruk.",
        "saran": "Optimalkan pemanfaatan air, cegah genangan berlebih, dan gunakan varietas padi yang tahan genangan bila curah hujan tinggi.",
        "color": "#4E80B4"
    },
    "Normal": {
        "desc": "Curah hujan dan ketersediaan air dalam kondisi seimbang, sangat ideal untuk pertumbuhan padi dengan produktivitas maksimal.",
        "saran": "Pertahankan pola tanam yang ada, lakukan pemupukan sesuai anjuran, dan jaga sistem irigasi agar tetap stabil.",
        "color": "#2ECC71"
    },
    "Kering Sedang": {
        "desc": "Ketersediaan air mulai terbatas, sawah menunjukkan tanda retakan, dan padi berisiko mengalami stres kekurangan air.",
        "saran": "Terapkan irigasi berselang (alternate wetting and drying), kendalikan gulma agar tidak berebut air, dan fokuskan air pada fase kritis padi (anakan maksimum dan pembungaan).",
        "color": "#F39C12"
    },
    "Kering Parah": {
        "desc": "Kekeringan semakin nyata, suplai air irigasi tidak stabil, pertumbuhan padi melambat, dan hasil panen berpotensi turun signifikan.",
        "saran": "Gunakan varietas tahan kekeringan, lakukan pompanisasi dari sumber terdekat, dan sesuaikan waktu tanam dengan ketersediaan air.",
        "color": "#E67E22"
    },
    "Kering Sangat Parah": {
        "desc": "Kekeringan ekstrem, sawah sulit ditanami padi, risiko gagal panen sangat tinggi.",
        "saran": "Tunda penanaman padi hingga kondisi membaik, alihkan sementara ke tanaman lebih tahan kering, serta lakukan konservasi air seperti pembuatan embung atau penampungan air hujan.",
        "color": "#C0392B"
    }
}

CLASS_TO_NUMERIC = { 
    "Sangat Basah": 1, 
    "Basah Ekstrem": 2, 
    "Basah Sedang": 3, 
    "Normal": 4, 
    "Kering Sedang": 5, 
    "Kering Parah": 6, 
    "Kering Sangat Parah": 7 
}
NUMERIC_TO_CLASS_LABELS = list(CLASS_TO_NUMERIC.keys())
DATA_DIR = "dataset"

KECAMATAN_FILES = {
    "Indralaya": "indralaya.csv", "Indralaya Utara": "indralaya utara.csv", "Indralaya Selatan": "indralaya selatan.csv",
    "Tanjung Batu": "tanjung batu.csv", "Tanjung Raja": "tanjung raja.csv", "Rantau Alai": "rantau alai.csv",
    "Rantau Panjang": "rantau panjang.csv", "Sungai Pinang": "sungai pinang.csv", "Pemulutan": "pemulutan.csv",
    "Pemulutan Barat": "pemulutan barat.csv", "Pemulutan Selatan": "pemulutan selatan.csv", "Kandis": "kandis.csv",
    "Rambang Kuang": "rambang kuang.csv", "Muara Kuang": "muara kuang.csv", "Lubuk Keliat": "lubuk keliat.csv"
}

# =================================================================================
# FUNGSI BANTUAN
# =================================================================================
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, header=None, names=['Kelas_Kekeringan'])
        start_date = "2024-12-31"
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
# SIDEBAR NAVIGASI
# =================================================================================
st.sidebar.title("📌 Navigasi")
menu = st.sidebar.radio("Pilih Halaman:", ["Dashboard", "About"])

# =================================================================================
# HALAMAN DASHBOARD
# =================================================================================
if menu == "Dashboard":
    # Header dengan logo7
    col_header1, col_header2 = st.columns([0.1, 0.9])
    with col_header1:
        st.image("logos/logo7.png", width=60)   # logo di header
    with col_header2:
        st.title("☀️ Dashboard Prediksi Kekeringan Pertanian Ogan Ilir")

    st.markdown("Analisis dan visualisasi data prediksi tingkat kekeringan untuk mendukung keputusan pertanian di Kabupaten Ogan Ilir.")
    st.markdown("---")

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
            value=df['Tanggal'].max(),
            min_value=df['Tanggal'].min(),
            max_value=df['Tanggal'].max()
        )
        selected_date = pd.to_datetime(selected_date).normalize()

        st.header(f"📍 Status Prediksi di Kecamatan: **{selected_kecamatan_name}**")
        st.caption(f"Data untuk tanggal: **{selected_date.strftime('%d %B %Y')}**")

        prediction_data = df[df['Tanggal'] == selected_date]

        if not prediction_data.empty:
            current_class = prediction_data['Kelas_Kekeringan'].iloc[0]
            class_info = DROUGHT_CLASSES.get(current_class, {"desc": "Kelas tidak dikenal.", "saran": "Periksa kembali data.", "color": "#808080"})

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

# =================================================================================
# HALAMAN ABOUT
# =================================================================================
elif menu == "About":
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Website ini dibuat untuk menampilkan hasil riset tim **PKM RE Universitas Sriwijaya 2025** dengan judul:  
    **“Penerapan Long Short-Term Memory dalam Memprediksi Curah Hujan untuk Klasifikasi Kekeringan berdasarkan Standardized Precipitation Index di Kabupaten Ogan Ilir.”**

    👩‍💻 **Tim Peneliti**  
    - Ketua: Annisa Reida Raheima (Teknik Informatika)  
    - Anggota: Evan Febrian (Teknik Informatika), Nabila Kurnia Aprianti (Teknik Informatika), Dio Subayu Jonathan (Ilmu Tanah)  
    - Dosen Pembimbing: Ibu Alvi Syahrini Utami, S.Si., M.Kom.  

    📢 Penelitian ini mendapat dukungan pendanaan **PKM-RE 2025** dari **Kementerian Pendidikan, Kebudayaan, Riset, dan Teknologi Republik Indonesia (Kemendikbudristek RI).**
    """)

    st.subheader("Didukung Oleh:")
    logo_files = [
        "logos/logo1.png", "logos/logo2.png", "logos/logo3.png", "logos/logo4.png",
        "logos/logo5.png", "logos/logo6.jpg", "logos/logo7.png"
    ]

    row1_cols = st.columns(4)
    row2_cols = st.columns(4)

    for i, col in enumerate(row1_cols):
        if i < len(logo_files):
            try:
                col.image(logo_files[i], width=120)  # kecilkan ukuran logo
            except:
                col.warning(f"Logo {i+1} gagal dimuat.")

    for i, col in enumerate(row2_cols):
        if (i+4) < len(logo_files):
            try:
                col.image(logo_files[i+4], width=120)  # kecilkan ukuran logo
            except:
                col.warning(f"Logo {i+5} gagal dimuat.")

