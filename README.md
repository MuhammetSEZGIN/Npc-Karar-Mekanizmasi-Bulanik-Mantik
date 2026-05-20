# BIM434 - Bulanık Mantık Tabanlı NPC Karar Mekanizması

## Giriş Değişkenleri

1. NPC Canı
2. Oyuncuya Uzaklık
3. NPC Cephane / Enerji
4. Oyuncu Takım Desteği

Her giriş 0-100 aralığındadır.

## Çıkış

NPC Aksiyon Skoru: 0-100

Skor yorumlaması:

- 0-30: Kaç
- 30-55: Savun
- 55-75: Takip
- 75-100: Saldır

## Kurulum

```bash
pip install -r requirements.txt
```

## Çalıştırma

```bash
python main.py
```

## Web Arayüzü Stremlit

```bash
streamlit run app.py
```

Program önce test senaryolarını çalıştırır, ardından grafik dosyalarını `outputs` klasörüne kaydeder.

## Üretilen Grafikler

- Sistem mimarisi blok diyagramı
- Giriş üyelik fonksiyonları
- Çıkış üyelik fonksiyonu
- Kural ateşleme grafiği
- Durulaştırma grafiği
- Test senaryoları aksiyon skoru karşılaştırma grafiği
- Test senaryoları giriş-çıkış karşılaştırma grafiği
- Giriş-çıkış yüzey grafiği
- Giriş değeri hassasiyet grafiği
- Üyelik fonksiyonu parametre analizi grafiği
