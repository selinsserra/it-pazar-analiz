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

# v2.0 - Genisletilmis ulke listesi
# Maas analizi: US, UK, DE, PL (IN hariç - INR olcegi farkli)
ULKELER = {
    "us": "ABD",
    "gb": "UK",
    "de": "Almanya",
    "in": "Hindistan",
    "pl": "Polonya"
}

# v2.0.1 - Sorgu esitleme: her grup tek sorgu, adil karsilastirma icin
ARAMALAR = [
    ("machine learning engineer", "Makine Ogrenmesi Muhendisi"),
    ("data engineer",              "Veri Muhendisi"),
    ("cloud engineer",             "Bulut Muhendisi"),
    ("security engineer",          "Siber Guvenlik"),
    ("devops engineer",            "DevOps Muhendisi"),
    ("data analyst",               "Veri/Is Analisti"),
    ("software engineer",          "Yazilim Muhendisi")
]

# Sayfa basina kac sonuc?
SAYFA_SAYISI = 2
SAYFA_BASINA_ILAN = 50

# Rate limit icin bekleme (5 ulke x 11 arama = 110 istek, dakikada 25 limit)
BEKLEME_SN = 2.5


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
        "max_days_old": 180,   # son 6 ay (180 gun)
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


def ilani_sadelestir(ham_ilan: dict, ulke_adi: str, arama_sorgu: str, ana_grup: str) -> dict:
    """
    Adzuna'dan gelen ham ilani ihtiyacimiz olan alanlara indirger.
    """
    return {
        "cekim_tarihi":    str(date.today()),
        "ulke":            ulke_adi,
        "arama_sorgusu":   arama_sorgu,
        "ana_grup":        ana_grup,
        "ilan_basligi":    ham_ilan.get("title", ""),
        "sirket":          ham_ilan.get("company", {}).get("display_name", ""),
        "konum":           ham_ilan.get("location", {}).get("display_name", ""),
        "maas_min":        ham_ilan.get("salary_min"),
        "maas_max":        ham_ilan.get("salary_max"),
        "para_birimi":     ham_ilan.get("salary_currency"),
        "sozlesme_tipi":   ham_ilan.get("contract_time", ""),
        "calisma_sekli":   ham_ilan.get("contract_type", ""),
        "kategori":        ham_ilan.get("category", {}).get("label", ""),
        "aciklama":        (ham_ilan.get("description", "") or "")[:5000],
        "ilan_tarihi":     (ham_ilan.get("created", "") or "")[:10],
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
    print(f"Ana gruplar:  {len(set(a[1] for a in ARAMALAR))} grup")
    print(f"Adzuna sorgusu: {len(ARAMALAR)} arama")
    print(f"Toplam istek: {len(ULKELER) * len(ARAMALAR) * SAYFA_SAYISI}")
    print("=" * 70)
    
    tum_ilanlar = []
    
    # Her ulke icin
    for ulke_kodu, ulke_adi in ULKELER.items():
        print(f"\n>>> {ulke_adi} ({ulke_kodu.upper()}) <<<")
        
        # Her arama icin (tuple: sorgu + ana grup)
        for arama_sorgu, ana_grup in ARAMALAR:
            print(f"  [{ana_grup}] Arama: '{arama_sorgu}'")
            
            for sayfa in range(1, SAYFA_SAYISI + 1):
                ham_ilanlar = tek_sayfa_cek(ulke_kodu, arama_sorgu, sayfa)
                
                for ham in ham_ilanlar:
                    tum_ilanlar.append(ilani_sadelestir(ham, ulke_adi, arama_sorgu, ana_grup))
                
                print(f"    Sayfa {sayfa}: {len(ham_ilanlar)} ilan")
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
    print(f"\nAna grup dagilimi:\n{df['ana_grup'].value_counts().to_string()}")
    print(f"\nAdzuna sorgu dagilimi:\n{df['arama_sorgusu'].value_counts().to_string()}")
    
    # data/ klasorunu olustur (yoksa)
    os.makedirs("data", exist_ok=True)


    # CSV'ye kaydet (tarih damgaliyla)
    dosya_adi = f"data/ilanlar_{date.today()}.csv"
    df.to_csv(dosya_adi, index=False, encoding="utf-8-sig")
    
    print(f"\n✓ Veri kaydedildi: {dosya_adi}")
    print(f"✓ Dosya boyutu: {os.path.getsize(dosya_adi):,} bytes")


if __name__ == "__main__":
    main()