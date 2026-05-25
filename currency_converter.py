"""
Para Birimi Donusturucu (v2.0)
ExchangeRate-API'den guncel kurlari ceker, maas degerlerini USD'ye normalize eder.

Cache mekanizmasi: Her gun yeni kur ceker, gun icinde tekrar API'ye gitmez.
Boylece haftalik pipeline her calistirildiginda 1 API cagrisiyla yetinir.

Kullanim:
    from currency_converter import usd_cevir, kurlari_yukle
    
    kurlari_yukle()  # Bir kez cagirilir (pipeline basinda)
    maas_usd = usd_cevir(50000, "EUR")  # 50000 EUR -> USD
"""

import os
import json
import requests
from datetime import date

# =============== AYARLAR ===============

API_URL = "https://open.er-api.com/v6/latest/USD"
CACHE_DOSYA = "data/doviz_kurlari.json"

# Bizim 5 ulkemizin para birimleri
HEDEF_BIRIMLER = ["USD", "GBP", "EUR", "PLN", "INR"]


# =============== GLOBAL CACHE ===============

# Tum modul boyunca paylasilacak kur sozlugu
# Yapi: {"USD": 1.0, "GBP": 0.79, ...}
_KURLAR = {}
_KURLAR_TARIHI = None


# =============== FONKSIYONLAR ===============

def kurlari_indir() -> dict:
    """ExchangeRate-API'den taze kurlari ceker."""
    print(f"  Doviz kurlari indiriliyor: {API_URL}")
    yanit = requests.get(API_URL, timeout=15)
    
    if yanit.status_code != 200:
        raise Exception(f"API hatasi: durum {yanit.status_code}")
    
    data = yanit.json()
    if data.get("result") != "success":
        raise Exception(f"API basarisiz: {data.get('error-type', 'unknown')}")
    
    rates = data.get("rates", {})
    
    # Sadece bizim ihtiyacimiz olan birimleri al
    kurlar = {kod: rates.get(kod) for kod in HEDEF_BIRIMLER if kod in rates}
    
    print(f"  Indirilen kurlar: {len(kurlar)} para birimi")
    for kod, kur in kurlar.items():
        print(f"    1 USD = {kur:>10,.4f} {kod}")
    
    return kurlar


def kurlari_kaydet(kurlar: dict) -> None:
    """Kurlari cache dosyasina kaydeder (gun damgaliyla)."""
    os.makedirs("data", exist_ok=True)
    veri = {
        "tarih": str(date.today()),
        "kurlar": kurlar,
        "kaynak": API_URL
    }
    with open(CACHE_DOSYA, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=2)


def kurlari_oku_cache() -> dict | None:
    """Cache'den oku, eger bugune ait degilse None doner."""
    if not os.path.exists(CACHE_DOSYA):
        return None
    
    try:
        with open(CACHE_DOSYA, "r", encoding="utf-8") as f:
            veri = json.load(f)
        
        # Bugune ait mi kontrol et
        if veri.get("tarih") == str(date.today()):
            return veri.get("kurlar")
        else:
            return None
    except Exception:
        return None


def kurlari_yukle() -> dict:
    """
    Ana giris fonksiyonu.
    Once cache'i kontrol eder, yoksa API'den indirir.
    Donen sozluk hem return edilir hem de global _KURLAR'a yazilir.
    """
    global _KURLAR, _KURLAR_TARIHI
    
    # Cache kontrolu
    cached = kurlari_oku_cache()
    if cached:
        print(f"  Doviz kurlari cache'den okundu ({CACHE_DOSYA})")
        _KURLAR = cached
        _KURLAR_TARIHI = str(date.today())
        return cached
    
    # Cache yoksa veya eski, indir
    kurlar = kurlari_indir()
    kurlari_kaydet(kurlar)
    
    _KURLAR = kurlar
    _KURLAR_TARIHI = str(date.today())
    return kurlar


def usd_cevir(tutar: float, para_birimi: str) -> float | None:
    """
    Verilen tutari USD'ye cevirir.
    
    Args:
        tutar: Donusturulecek miktar (ornek: 50000)
        para_birimi: Kaynak birim kodu (ornek: "EUR", "GBP", "PLN")
    
    Returns:
        USD karsiligi (float) veya kur yoksa None
    
    Ornek:
        usd_cevir(50000, "EUR")  -> 58148.62 (yaklasik, kura gore)
    """
    if not _KURLAR:
        raise RuntimeError("Once kurlari_yukle() cagirilmali!")
    
    if tutar is None or para_birimi is None:
        return None
    
    # Para birimi koddan emin ol
    para_birimi = str(para_birimi).upper().strip()
    
    # USD ise donusum yok
    if para_birimi == "USD":
        return float(tutar)
    
    kur = _KURLAR.get(para_birimi)
    if not kur or kur <= 0:
        return None
    
    # Formul: 1 USD = X EUR, yani 1 EUR = 1/X USD
    return float(tutar) / kur


# =============== TEST (modul direkt calistirilirsa) ===============

if __name__ == "__main__":
    print("=" * 60)
    print("CURRENCY CONVERTER TEST")
    print("=" * 60)
    
    kurlari_yukle()
    
    print("\nTest donusumleri:")
    test_durumlar = [
        (1000, "USD"),
        (50000, "GBP"),
        (60000, "EUR"),
        (250000, "PLN"),
        (1500000, "INR"),
        (100, "XYZ"),   # gecersiz, None donmeli
    ]
    
    for tutar, birim in test_durumlar:
        usd = usd_cevir(tutar, birim)
        if usd is not None:
            print(f"  {tutar:>10,} {birim}  =  {usd:>10,.2f} USD")
        else:
            print(f"  {tutar:>10,} {birim}  =  CEVRILEMEZ ({birim} bilinmiyor)")
    
    print("\n" + "=" * 60)
    print("Test tamamlandi.")