import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Kampanya ve Satış Analitik Platformu", layout="wide")

rfm = pd.read_csv("rfm_kampanya_sonuclari.csv")
satis = pd.read_csv("satis_tahmini_sonuclari.csv", parse_dates=["Tarih"])
segment_ozeti = pd.read_csv("segment_ozeti.csv")
gelecek = pd.read_csv("gelecek_tahmin.csv", parse_dates=["Tarih"])

segment_renkleri = {
    "Sadık Müşteri": "#2e7d32",
    "Kaybedilme Riski (Değerli)": "#c62828",
    "Pasif/Kaybedilmiş": "#616161",
    "Yeni / Potansiyel Müşteri": "#1565c0",
    "Orta Segment": "#f9a825"
}

PLOTLY_TEMPLATE = "plotly_dark"

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Analitik Platform")
    st.caption("SAP MDG Sipariş Yönetimi Senaryosu")
    st.divider()
    sayfa = st.radio("Bölüm Seç", ["Genel Bakış", "Kampanya Önerisi", "Satış Tahmini"])
    st.divider()
    st.caption("Veri kaynağı: Online Retail II")
    st.caption("Modeller: Random Forest (kampanya), XGBoost (satış tahmini)")

# --- Üst başlık ---
st.title("Sipariş Yönetiminde Kampanya Önerisi ve Satış Tahmini")
st.caption("SAP MDG tabanlı bir sipariş/müşteri yönetimi senaryosuna yönelik analitik uygulama")
st.divider()

# --- Yardımcı fonksiyon: metrik kartı ---
def metrik_karti(baslik, deger):
    st.markdown(
        f"""
        <div style="background-color:#1a1d23; border:1px solid #2d3748; border-radius:8px; padding:16px 20px;">
        <div style="color:#9aa4b2; font-size:13px;">{baslik}</div>
        <div style="font-size:26px; font-weight:600; margin-top:6px;">{deger}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Genel Bakış ---
if sayfa == "Genel Bakış":
    col1, col2, col3 = st.columns(3)
    with col1:
        metrik_karti("Toplam Müşteri", f"{rfm['Customer ID'].nunique():,}")
    with col2:
        metrik_karti("Toplam Satış (Test Dönemi)", f"£{satis['Satis'].sum():,.2f}")
    with col3:
        mae_deger = (satis['Satis'] - satis['Tahmin']).abs().mean()
        metrik_karti("Ortalama Tahmin Hatası (MAE)", f"£{mae_deger:,.2f}")

    st.write("")
    st.subheader("Müşteri Segment Dağılımı")
    segment_sayilari = rfm["Segment"].value_counts().reset_index()
    segment_sayilari.columns = ["Segment", "Müşteri Sayısı"]
    segment_sayilari = segment_sayilari.sort_values("Müşteri Sayısı")

    fig = go.Figure()
    for _, row in segment_sayilari.iterrows():
        fig.add_trace(go.Bar(
            x=[row["Müşteri Sayısı"]],
            y=[row["Segment"]],
            orientation="h",
            marker_color=segment_renkleri.get(row["Segment"], "#999999"),
            text=[row["Müşteri Sayısı"]],
            showlegend=False
        ))
    fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="", xaxis_title="Müşteri Sayısı")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Segment Özet Tablosu")
    segment_ozeti_goster = segment_ozeti.rename(columns={
        "Musteri_Sayisi": "Müşteri Sayısı",
        "Ortalama_Recency": "Ort. Recency",
        "Ortalama_Frequency": "Ort. Frequency",
        "Ortalama_Monetary": "Ort. Monetary (£)"
    })
    segment_ozeti_goster["Ort. Monetary (£)"] = segment_ozeti_goster["Ort. Monetary (£)"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(segment_ozeti_goster, use_container_width=True, hide_index=True)

# --- Kampanya Önerisi ---
elif sayfa == "Kampanya Önerisi":
    st.subheader("Müşteri Sorgula")
    st.caption("Listeden bir müşteri seçin.")

    musteri_listesi = rfm[["Customer ID", "Segment"]].sort_values("Customer ID")
    musteri_secenekleri = [
        f"{row['Customer ID']} — {row['Segment']}" for _, row in musteri_listesi.iterrows()
    ]

    secilen = st.selectbox("Müşteri Seç:", musteri_secenekleri)
    musteri_id = int(secilen.split(" — ")[0])

    sonuc = rfm[rfm["Customer ID"] == musteri_id]
    segment_adi = sonuc.iloc[0]["Segment"]
    renk = segment_renkleri.get(segment_adi, "#999999")


    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style="background-color:#1a1d23; border:1px solid #2d3748; border-radius:8px; padding:18px; height:220px;">
            <div style="color:#9aa4b2; font-size:13px; letter-spacing:0.5px;">MÜŞTERİ BİLGİSİ</div>
            <div style="margin-top:14px; font-size:14px; line-height:2;">
            Ülke: <b>{sonuc.iloc[0]['Ulke']}</b><br>
            Toplam Harcama: <b>£{sonuc.iloc[0]['Monetary']:,.2f}</b><br>
            Sipariş Sıklığı: <b>{sonuc.iloc[0]['Frequency']} sipariş</b><br>
            Son Alışveriş: <b>{sonuc.iloc[0]['Recency']} gün önce</b>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style="background-color:{renk}22; border-left:4px solid {renk}; border-radius:8px; padding:18px; height:220px;">
            <div style="color:#9aa4b2; font-size:13px; letter-spacing:0.5px;">SEGMENT</div>
            <div style="margin-top:14px; font-size:20px; font-weight:600;">{segment_adi}</div>
            <div style="margin-top:16px; font-size:14px; line-height:2; color:#c9ccd1;">
            Ort. Sepet Büyüklüğü: <b>{sonuc.iloc[0]['Ort_Sepet_Buyuklugu']:.1f}</b><br>
            Ort. Ürün Fiyatı: <b>£{sonuc.iloc[0]['Ort_Urun_Fiyati']:.2f}</b>
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style="background-color:#1565c022; border-left:4px solid #1565c0; border-radius:8px; padding:18px; height:220px;">
            <div style="color:#9aa4b2; font-size:13px; letter-spacing:0.5px;">ÖNERİLEN KAMPANYA</div>
            <div style="margin-top:14px; font-size:18px; font-weight:600;">{sonuc.iloc[0]['Onerilen_Kampanya']}</div>
            <div style="margin-top:16px; font-size:13px; color:#9aa4b2;">
            Kampanya, müşterinin RFM segmentine göre otomatik olarak eşleştirilmiştir.
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.write("")
    st.subheader("Ham Veri")
    detay = sonuc.rename(columns={
        "Onerilen_Kampanya": "Önerilen Kampanya",
        "Ulke": "Ülke",
        "Ort_Sepet_Buyuklugu": "Ort. Sepet Büyüklüğü",
        "Ort_Urun_Fiyati": "Ort. Ürün Fiyatı (£)"
    }).copy()
    detay["Monetary"] = detay["Monetary"].apply(lambda x: f"£{x:,.2f}")
    if "Ort. Ürün Fiyatı (£)" in detay.columns:
        detay["Ort. Ürün Fiyatı (£)"] = detay["Ort. Ürün Fiyatı (£)"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(detay, use_container_width=True, hide_index=True)


# --- Satış Tahmini ---
elif sayfa == "Satış Tahmini":
    st.subheader("Model Performansı: Gerçek vs Tahmin Edilen Satış (Test Dönemi)")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=satis["Tarih"], y=satis["Satis"], name="Gerçek Satış", line=dict(color="#1565c0")))
    fig2.add_trace(go.Scatter(x=satis["Tarih"], y=satis["Tahmin"], name="Tahmin Edilen Satış", line=dict(color="#f9a825")))
    fig2.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="Satış (£)", xaxis_title="Tarih")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    st.subheader("Gelecek 30 Günlük Satış Tahmini")
    st.caption("Veri setinin son gününden itibaren üretilen recursive tahmin.")

    gelecek_toplam = gelecek["Tahmin"].sum()
    metrik_karti("Gelecek 30 Gün Beklenen Ciro", f"£{gelecek_toplam:,.2f}")
    st.write("")

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=satis["Tarih"].tail(30), y=satis["Satis"].tail(30),
        name="Geçmiş Satış (Son 30 Gün)", line=dict(color="#1565c0")
    ))
    fig3.add_trace(go.Scatter(
        x=gelecek["Tarih"], y=gelecek["Tahmin"],
        name="Gelecek Tahmini (30 Gün)", line=dict(color="#f9a825", dash="dash")
    ))
    fig3.update_layout(template=PLOTLY_TEMPLATE, yaxis_title="Satış (£)", xaxis_title="Tarih")
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()
    st.subheader("Detaylı Veri")
    detay_satis = satis.rename(columns={"Satis": "Gerçek Satış (£)", "Tahmin": "Tahmin Edilen Satış (£)"}).copy()
    detay_satis["Tarih"] = detay_satis["Tarih"].dt.strftime("%d.%m.%Y")
    detay_satis["Gerçek Satış (£)"] = detay_satis["Gerçek Satış (£)"].apply(lambda x: f"£{x:,.2f}")
    detay_satis["Tahmin Edilen Satış (£)"] = detay_satis["Tahmin Edilen Satış (£)"].apply(lambda x: f"£{x:,.2f}")
    st.dataframe(detay_satis, use_container_width=True, hide_index=True, height=350)