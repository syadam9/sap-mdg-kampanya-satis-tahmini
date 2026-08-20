# Sipariş Yönetiminde Yapay Zeka Destekli Kampanya Önerisi ve Satış Tahmini

SAP MDG (Master Data Governance) tabanlı bir sipariş yönetimi senaryosuna yönelik, müşteri segmentasyonu, kampanya önerisi ve satış tahmini yapan uçtan uca bir analitik proje.

## Kapsam ve Senaryo Notu

Bu çalışma, gerçek bir e-ticaret veri seti (Online Retail II) kullanılarak, müşteri segmentasyonu, kampanya önerisi ve satış tahmini yöntemlerinin SAP MDG tabanlı bir sipariş/müşteri yönetimi senaryosunda nasıl uygulanabileceğini göstermeyi amaçlamaktadır. Çalışma doğrudan bir SAP MDG sistem entegrasyonu içermemektedir; veri şeması, SAP MDG'nin Customer Master, Material Master ve Sales Order kavramlarına benzetilerek yapılandırılmıştır.

## Veri Seti

- **Kaynak:** [Online Retail II (Kaggle/UCI)](https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci)
- **İçerik:** İngiltere merkezli bir hediyelik eşya şirketinin 2009-2011 yılları arasındaki gerçek sipariş kayıtları (~1 milyon satır)
- **Alanlar:** Fatura no, ürün kodu/açıklaması, miktar, fiyat, tarih, müşteri ID, ülke

## Metodoloji

### 1. Veri Temizliği
İptal edilen siparişler, negatif/sıfır miktar-fiyat kayıtları, eksik ürün açıklamaları, tekrarlanan satırlar ve kargo/muhasebe kalemleri (POST, BANK CHARGES vb.) veri setinden çıkarılmıştır.

### 2. Keşifsel Veri Analizi
Aylık satış trendi, haftanın günlerine göre satış dağılımı, en çok satan ürünler ve ülke bazlı satış payı incelenmiştir.

### 3. Kampanya Önerisi Modülü
- RFM (Recency, Frequency, Monetary) analizi ile müşteriler 5 segmente ayrılmıştır.
- Her segmente kural tabanlı bir kampanya türü eşleştirilmiştir.
- Random Forest sınıflandırıcı, RFM değerlerine ek olarak ülke, ortalama sepet büyüklüğü ve ortalama ürün fiyatı özellikleriyle eğitilmiştir.

### 4. Satış Tahmini Modülü
- XGBoost regresyon modeli, lag ve hareketli ortalama özellikleriyle günlük satışı tahmin etmektedir.
- Model performansı, naive bir referans modelle (baseline) karşılaştırılarak doğrulanmıştır.
- Veri setinin son gününden itibaren 30 günlük gerçek gelecek tahmini (recursive forecasting) üretilmiştir.

## Sonuçlar

| Modül | Metrik | Değer |
|---|---|---|
| Kampanya Sınıflandırma | Doğruluk (Accuracy) | %93.42 |
| Satış Tahmini | MAE | £10,656 |
| Satış Tahmini | Baseline'a göre iyileşme | %26.1 |

**Not:** Kampanya sınıflandırma modelinin yüksek doğruluğu, hedef etiketlerin RFM değerlerinden kural tabanlı türetilmiş olmasından kaynaklanmaktadır. Model, gerçek kampanya geri dönüş verisini değil, oluşturulan segmentasyon kurallarını öğrenmektedir. Detaylı tartışma notebook içinde yer almaktadır.

## Dosya Yapısı
sap-mdg-kampanya-satis-tahmini.ipynb Analiz ve model gelistirme notebooku
app.py Streamlit dashboard
rfm_kampanya_sonuclari.csv Musteri segment ve kampanya sonuclari
satis_tahmini_sonuclari.csv Test donemi satis tahminleri
segment_ozeti.csv Segment bazli ozet istatistikler
gelecek_tahmin.csv 30 gunluk gelecek satis tahmini
README.md

## Kurulum ve Çalıştırma

### Notebook
Notebook, Google Colab üzerinde çalıştırılacak şekilde hazırlanmıştır. `online_retail_II.csv` dosyasının Colab ortamına yüklenmesi gerekmektedir.

### Dashboard
```bash
pip install streamlit pandas matplotlib plotly
streamlit run app.py
```

## Kullanılan Teknolojiler

- **Veri işleme:** pandas, numpy
- **Makine öğrenmesi:** scikit-learn (Random Forest), XGBoost
- **Görselleştirme:** matplotlib, Plotly
- **Dashboard:** Streamlit

## Sınırlamalar

- Kampanya sınıflandırma modeli, kural tabanlı etiketlerle eğitilmiştir; gerçek kampanya geri dönüş verisi kullanılmamıştır.
- Satış tahmini, recursive (özyinelemeli) bir yöntem kullanmaktadır; bu yöntemde tahmin hatalarının zaman içinde birikme riski bulunmaktadır.
- SAP MDG entegrasyonu bir senaryo olarak ele alınmıştır, gerçek bir sistem bağlantısı içermemektedir.