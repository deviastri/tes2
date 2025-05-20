
import streamlit as st
import pandas as pd

st.set_page_config(page_title="📈 Rekap Penambahan & Pengurangan", layout="wide")
st.title("📆 Laporan Penambahan & Pengurangan Tarif Berdasarkan Lokasi")

uploaded_file = st.file_uploader("📄 Upload Data Excel Boarding", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.lower().str.strip()

    df['cetak boarding pass'] = pd.to_datetime(df['cetak boarding pass']).dt.date
    df['jam'] = pd.to_numeric(df['jam'], errors='coerce')
    df['tarif'] = pd.to_numeric(df['tarif'], errors='coerce')
    df['keberangkatan'] = df['keberangkatan'].str.upper().str.strip()

    lokasi_lengkap = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']
    selected_date = st.date_input("Pilih Tanggal", value=df['cetak boarding pass'].min())

    filtered_df = df[
        (df['cetak boarding pass'] == selected_date) &
        (df['jam'] >= 0) & (df['jam'] <= 8)
    ]

    penambahan = filtered_df.groupby('keberangkatan')['tarif'].sum().reindex(lokasi_lengkap, fill_value=0).reset_index()
    penambahan.columns = ['Lokasi', 'Penambahan']
    penambahan['Pengurangan'] = 0  # Placeholder kolom

    penambahan['Penambahan'] = penambahan['Penambahan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    penambahan['Pengurangan'] = penambahan['Pengurangan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    st.subheader(f"Hasil Rekap: {selected_date.strftime('%d %B %Y')}")
    st.dataframe(penambahan, use_container_width=True)
else:
    st.info("Silakan unggah file Excel untuk mulai.")
