import streamlit as st
import pandas as pd
from io import BytesIO

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

    pelabuhan_lengkap = ['MERAK', 'BAKAUHENI', 'KETAPANG', 'GILIMANUK']

    col1, col2 = st.columns(2)
    with col1:
        date_penambahan = st.date_input("📅 Tanggal Penambahan", value=df['CETAK BOARDING PASS'].min())
    with col2:
        date_pengurangan = st.date_input("📅 Tanggal Pengurangan", value=df['CETAK BOARDING PASS'].max())

    df_penambahan = df[
        (df['CETAK BOARDING PASS'] == date_penambahan) &
        (df['JAM'] >= 0) & (df['JAM'] <= 7)
    ]
    df_pengurangan = df[
        (df['CETAK BOARDING PASS'] == date_pengurangan) &
        (df['JAM'] >= 0) & (df['JAM'] <= 7)
    ]

    penambahan = df_penambahan.groupby('ASAL')['TARIF'].sum().reindex(pelabuhan_lengkap, fill_value=0)
    pengurangan = df_pengurangan.groupby('ASAL')['TARIF'].sum().reindex(pelabuhan_lengkap, fill_value=0)

    result = pd.DataFrame({
        'Pelabuhan Asal': pelabuhan_lengkap,
        'Penambahan': penambahan.values,
        'Pengurangan': pengurangan.values
    })

    total_penambahan = result['Penambahan'].sum()
    total_pengurangan = result['Pengurangan'].sum()

    result_display = result.copy()
    result_display['Penambahan'] = result_display['Penambahan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))
    result_display['Pengurangan'] = result_display['Pengurangan'].apply(lambda x: f"Rp {x:,.0f}".replace(",", "."))

    total_row = pd.DataFrame([{
        'Pelabuhan Asal': 'TOTAL',
        'Penambahan': f"Rp {total_penambahan:,.0f}".replace(",", "."),
        'Pengurangan': f"Rp {total_pengurangan:,.0f}".replace(",", ".")
    }])

    final_df_display = pd.concat([result_display, total_row], ignore_index=True)

    st.subheader("📊 Tabel Rekapitulasi")
    st.write(f"📅 Penambahan: {date_penambahan.strftime('%d %B %Y')} | Pengurangan: {date_pengurangan.strftime('%d %B %Y')}")
    st.dataframe(final_df_display, use_container_width=True)

    # Ekspor ke Excel
    def convert_df_to_excel(df_raw):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_raw.to_excel(writer, index=False, sheet_name='Rekap')
        output.seek(0)
        return output

    excel_bytes = convert_df_to_excel(result)
    st.download_button(
        label="⬇️ Unduh Excel Rekap",
        data=excel_bytes,
        file_name="rekap_penambahan_pengurangan.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success("✅ Data berhasil direkap & siap diunduh.")
else:
    st.info("Silakan unggah file Excel untuk memulai.")
