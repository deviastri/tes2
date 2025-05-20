import streamlit as st
import pandas as pd

st.set_page_config(page_title="📈 Rekap Penambahan & Pengurangan", layout="wide")
st.title("📆 Laporan Penambahan & Pengurangan Tarif Berdasarkan Lokasi")

uploaded_file = st.file_uploader("📄 Upload Data Excel Boarding", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    # Parsing kolom
    df['CETAK BOARDING PASS'] = pd.to_datetime(df['CETAK BOARDING PASS'], errors='coerce').dt.date
    df = df.dropna(subset=['CETAK BOARDING PASS'])

    df['JAM'] = pd.to_numeric(df['JAM'], errors='coerce')
    df['TARIF'] = pd.to_numeric(df['TARIF'], errors='coerce')
    df['ASAL'] = df['ASAL'].astype(str).str.upper().str.strip()

    lokasi_lengkap = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']
    selected_date = st.date_input("📅 Pilih Tanggal", value=df['CETAK BOARDING PASS'].min())

    # Filter berdasarkan tanggal & jam 0–8
    filtered_df = df[
        (df['CETAK BOARDING PASS'] == selected_date) &
        (df['JAM'] >= 0) & (df['JAM'] <= 8)
    ]

    penambahan = (
        filtered_df.groupby('ASAL')['TARIF']
        .sum().reindex(lokasi_lengkap, fill_value=0)
        .reset_index()
    )
    penambahan.columns = ['Lokasi', 'Penambahan']
    penambahan['Pengurangan'] = 0  # placeholder kolom

    # Format nominal
    penambahan['Penambahan'] = penambahan['Penambahan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    penambahan['Pengurangan'] = penambahan['Pengurangan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    st.subheader(f"Hasil Rekap: {selected_date.strftime('%d %B %Y')}")
    st.dataframe(penambahan, use_container_width=True)

else:
    st.info("Silakan unggah file Excel untuk mulai.")
