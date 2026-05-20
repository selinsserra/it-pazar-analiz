"""
Adzuna API - Ana Scraper
Amac: UK, Almanya ve ABD icin IT is ilanlarini cekip CSV'ye kaydetmek.

Calistir: python3 main_scraper.py
Cikti:   data/ilanlar_YYYY-MM-DD.csv
"""

import os
import time
import requests
import pandas as pd
from datetime import date
from dotenv import load_dotenv

# =============== AYARLAR ===============

load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")

# Hangi ulkeleri tarayacagiz? (Adzuna kodlari)
ULKELER = {
    "gb": "UK",       # Great Britain
    "de": "Almanya",
    "us": "ABD"
}

# Hangi IT rolleri icin arama yapacagiz?
ARAMALAR = [
    "python developer",
    "data analyst",
    "data scientist"
]

# Her arama icin kac sayfa cekelim? (sayfa basina 50 ilan)
SAYFA_SAYISI = 2          # 2 sayfa = 100 ilan per arama per ulke
SAYFA_BASINA_ILAN = 50    # Adzuna max 50 verir

# Istekler arasinda bekleme (API'yi rahatsiz etmemek icin)
BEKLEME_SN = 1.5


# =============== FONKSIYONLAR ===============

def tek_sayfa_cek(ulke_kodu: str, arama: str, sayfa: int) -> list:
    """
    Belirli bir ulke + arama + sayfa icin Adzuna'dan ilanlari ceker.
    Basarisiz olursa bos liste doner.
    """
    url = f"https://api.adzuna.com/v1/api/jobs/{ulke_kodu}/search/{sayfa}"
    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "results_per_page": SAYFA_BASINA_ILAN,
        "what": arama,
        "content-type": "application/json"
    }
    
    try:
        yanit = requests.get(url, params=params, timeout=20)
        if yanit.status_code == 200:
            return yanit.json().get("results", [])
        else:
            print(f"  [!] Hata: durum {yanit.status_code}")
            return []
    except Exception as e:
        print(f"  [!] Istek hatasi: {e}")
        return []


def ilani_sadelestir(ham_ilan: dict, ulke_adi: str, arama_anahtari: str) -> dict:
    """
    Adzuna'dan gelen ham (cok detayli) ilani ihtiyacimiz olan alanlara indirger.
    Her ilan icin temiz bir sozluk dondurur.
    """
    return {
        "cekim_tarihi":    str(date.today()),
        "ulke":            ulke_adi,
        "arama_anahtari":  arama_anahtari,
        "ilan_basligi":    ham_ilan.get("title", ""),
        "sirket":          ham_ilan.get("company", {}).get("display_name", ""),
        "konum":           ham_ilan.get("location", {}).get("display_name", ""),
        "maas_min":        ham_ilan.get("salary_min"),
        "maas_max":        ham_ilan.get("salary_max"),
        "para_birimi":     ham_ilan.get("salary_currency"),
        "sozlesme_tipi":   ham_ilan.get("contract_time", ""),       # full_time / part_time
        "calisma_sekli":   ham_ilan.get("contract_type", ""),       # permanent / contract
        "kategori":        ham_ilan.get("category", {}).get("label", ""),
        "aciklama":        (ham_ilan.get("description", "") or "")[:5000],  # ilk 5000 karakter
        "ilan_tarihi":     (ham_ilan.get("created", "") or "")[:10],        # YYYY-MM-DD
        "ilan_url":        ham_ilan.get("redirect_url", "")
    }


# =============== ANA AKIS ===============

def main():
    # Anahtar kontrolu
    if not APP_ID or not API_KEY:
        print("HATA: .env dosyasi okunamadi veya anahtarlar eksik!")
        return
    
    print("=" * 70)
    print("ADZUNA IT IS ILANI TARAMASI BASLIYOR")
    print(f"Tarih:     {date.today()}")
    print(f"Ulkeler:   {', '.join(ULKELER.values())}")
    print(f"Aramalar:  {', '.join(ARAMALAR)}")
    print(f"Toplam istek: {len(ULKELER) * len(ARAMALAR) * SAYFA_SAYISI}")
    print("=" * 70)
    
    tum_ilanlar = []
    
    # Her ulke icin
    for ulke_kodu, ulke_adi in ULKELER.items():
        print(f"\n>>> {ulke_adi} ({ulke_kodu.upper()}) <<<")
        
        # Her arama icin
        for arama in ARAMALAR:
            print(f"  Arama: '{arama}'")
            
            # Her sayfa icin
            for sayfa in range(1, SAYFA_SAYISI + 1):
                ham_ilanlar = tek_sayfa_cek(ulke_kodu, arama, sayfa)
                
                # Sadelestirip listeye ekle
                for ham in ham_ilanlar:
                    tum_ilanlar.append(ilani_sadelestir(ham, ulke_adi, arama))
                
                print(f"    Sayfa {sayfa}: {len(ham_ilanlar)} ilan")
                
                # API'yi rahatsiz etmemek icin bekle
                time.sleep(BEKLEME_SN)
    
    # Tum veriyi DataFrame'e cevir
    if not tum_ilanlar:
        print("\nHIC ILAN CEKILEMEDI. Anahtarlari ve internet baglantisini kontrol et.")
        return
    
    df = pd.DataFrame(tum_ilanlar)
    
    # Ozet istatistikler
    print("\n" + "=" * 70)
    print("OZET")
    print("=" * 70)
    print(f"Toplam ilan: {len(df)}")
    print(f"Ulke dagilimi:\n{df['ulke'].value_counts().to_string()}")
    print(f"\nArama dagilimi:\n{df['arama_anahtari'].value_counts().to_string()}")
    
    # data/ klasorunu olustur (yoksa)
    os.makedirs("data", exist_ok=True)
    
    # CSV'ye kaydet (tarih damgaliyla)
    dosya_adi = f"data/ilanlar_{date.today()}.csv"
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    
    print(f"\n✓ Veri kaydedildi: {dosya_adi}")
    print(f"✓ Dosya boyutu: {os.path.getsize(dosya_adi):,} bytes")


if __name__ == "__main__":
    main()