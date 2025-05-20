import streamlit as st
import pandas as pd

st.set_page_config(page_title="📈 Rekap Penambahan & Pengurangan", layout="wide")
st.title("📆 Laporan Penambahan & Pengurangan Tarif Berdasarkan Lokasi")

# 🔍 Deteksi otomatis nama kolom
def find_column(df, keywords):
    for col in df.columns:
        col_clean = col.lower().strip()
        for key in keywords:
            if key in col_clean:
                return col
    return None

uploaded_file = st.file_uploader("📄 Upload Data Excel Boarding", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # 🔍 Temukan nama kolom
    col_tanggal = find_column(df, ["cetak boarding", "tanggal"])
    col_jam = find_column(df, ["jam"])
    col_tarif = find_column(df, ["tarif"])
    col_lokasi = find_column(df, ["keberangkatan", "lokasi"])

    if None in [col_tanggal, col_jam, col_tarif, col_lokasi]:
        st.error("❌ Tidak dapat menemukan semua kolom yang dibutuhkan. Harus ada kolom: jam, tarif, keberangkatan, dan cetak boarding pass.")
        st.write("📌 Kolom ditemukan:", df.columns.tolist())
        st.stop()

    # 🔄 Parsing dan normalisasi
    df[col_tanggal] = pd.to_datetime(df[col_tanggal], errors='coerce').dt.date
    df = df.dropna(subset=[col_tanggal])

    df[col_jam] = pd.to_numeric(df[col_jam], errors='coerce')
    df[col_tarif] = pd.to_numeric(df[col_tarif], errors='coerce')
    df[col_lokasi] = df[col_lokasi].astype(str).str.upper().str.strip()

    lokasi_lengkap = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']
    selected_date = st.date_input("📅 Pilih Tanggal", value=df[col_tanggal].min())

    # Filter jam 0-8 pada tanggal terpilih
    filtered_df = df[
        (df[col_tanggal] == selected_date) &
        (df[col_jam] >= 0) & (df[col_jam] <= 8)
    ]

    penambahan = (
        filtered_df.groupby(col_lokasi)[col_tarif]
        .sum().reindex(lokasi_lengkap, fill_value=0)
        .reset_index()
    )
    penambahan.columns = ['Lokasi', 'Penambahan']
    penambahan['Pengurangan'] = 0  # Kolom placeholder

    # Format Rupiah
    penambahan['Penambahan'] = penambahan['Penambahan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    penambahan['Pengurangan'] = penambahan['Pengurangan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    st.subheader(f"Hasil Rekap: {selected_date.strftime('%d %B %Y')}")
    st.dataframe(penambahan, use_container_width=True)

else:
    st.info("Silakan unggah file Excel untuk mulai.")
