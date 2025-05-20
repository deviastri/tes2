import streamlit as st
import pandas as pd

st.set_page_config(page_title="📊 Rekap Tarif ASDP", layout="wide")

st.markdown(
    "<h2 style='text-align: center; color: #2c3e50;'>📆 Laporan Penambahan & Pengurangan Tarif (Jam 0–7)</h2><hr>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("📁 Upload Data Excel Boarding Pass", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()

    df['CETAK BOARDING PASS'] = pd.to_datetime(df['CETAK BOARDING PASS'], errors='coerce').dt.date
    df = df.dropna(subset=['CETAK BOARDING PASS'])

    df['JAM'] = pd.to_numeric(df['JAM'], errors='coerce')
    df['TARIF'] = pd.to_numeric(df['TARIF'], errors='coerce')
    df['ASAL'] = df['ASAL'].astype(str).str.upper().str.strip()

    lokasi_lengkap = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']

    col1, col2 = st.columns(2)
    with col1:
        date_penambahan = st.date_input("📅 Tanggal Penambahan", value=df['CETAK BOARDING PASS'].min())
    with col2:
        date_pengurangan = st.date_input("📅 Tanggal Pengurangan", value=df['CETAK BOARDING PASS'].max())

    # Filter jam 0-7
    df_penambahan = df[
        (df['CETAK BOARDING PASS'] == date_penambahan) &
        (df['JAM'] >= 0) & (df['JAM'] <= 7)
    ]
    df_pengurangan = df[
        (df['CETAK BOARDING PASS'] == date_pengurangan) &
        (df['JAM'] >= 0) & (df['JAM'] <= 7)
    ]

    penambahan = df_penambahan.groupby('ASAL')['TARIF'].sum().reindex(lokasi_lengkap, fill_value=0)
    pengurangan = df_pengurangan.groupby('ASAL')['TARIF'].sum().reindex(lokasi_lengkap, fill_value=0)

    result = pd.DataFrame({
        'No': range(1, len(lokasi_lengkap)+1),
        'Lokasi': lokasi_lengkap,
        'Penambahan': penambahan.values,
        'Pengurangan': pengurangan.values
    })

    total_penambahan = result['Penambahan'].sum()
    total_pengurangan = result['Pengurangan'].sum()

    # Format nominal
    result['Penambahan'] = result['Penambahan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    result['Pengurangan'] = result['Pengurangan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    total_row = pd.DataFrame([{
        'No': '',
        'Lokasi': 'TOTAL',
        'Penambahan': f"Rp {total_penambahan:,.0f}".replace(",", "."),
        'Pengurangan': f"Rp {total_pengurangan:,.0f}".replace(",", ".")
    }])

    final_df = pd.concat([result, total_row], ignore_index=True)

    st.subheader("📊 Tabel Rekapitulasi")
    st.write(f"📅 Penambahan: {date_penambahan.strftime('%d %B %Y')} | Pengurangan: {date_pengurangan.strftime('%d %B %Y')}")
    st.dataframe(final_df, use_container_width=True)

    st.success("✅ Data berhasil direkap.")
else:
    st.info("Silakan unggah file Excel untuk memulai.")
