"""
Adzuna API ilk test istegi.
Amac: API anahtarlarimizin calistigini dogrulamak + gelen veriyi incelemek.
"""

import os
import requests
from dotenv import load_dotenv

# .env dosyasini oku ve icindeki degiskenleri sisteme yukle
load_dotenv()

# .env'den anahtarlari al
APP_ID = os.getenv("ADZUNA_APP_ID")
API_KEY = os.getenv("ADZUNA_API_KEY")

# Anahtarlarin yuklendigini dogrula (guvenlik icin sadece ilk 4 karakteri goster)
print(f"APP_ID yuklendi mi? {'EVET' if APP_ID else 'HAYIR'} (ilk 4 karakter: {APP_ID[:4] if APP_ID else 'YOK'})")
print(f"API_KEY yuklendi mi? {'EVET' if API_KEY else 'HAYIR'} (ilk 4 karakter: {API_KEY[:4] if API_KEY else 'YOK'})")
print()

# Eger anahtarlar yuklenmediyse dur
if not APP_ID or not API_KEY:
    print("HATA: .env dosyasi okunamadi veya anahtarlar eksik!")
    exit()

# Adzuna API endpoint (gb = Great Britain / Ingiltere)
# Sayfa numarasi URL'nin sonundaki /1
url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

# Istek parametreleri
params = {
    "app_id": APP_ID,
    "app_key": API_KEY,
    "results_per_page": 10,          # Sayfa basina 10 sonuc
    "what": "python developer",      # Aranan iş
    "content-type": "application/json"
}

print("Adzuna API'ye istek atiliyor...")
print(f"Ulke: UK (gb)")
print(f"Arama: python developer")
print()

response = requests.get(url, params=params, timeout=15)

print(f"Durum kodu: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    
    # Toplam kac ilan var?
    print(f"Toplam ilan sayisi (UK'de python developer): {data.get('count', 0):,}")
    print(f"Bu sayfadaki ilan sayisi: {len(data.get('results', []))}")
    print()
    
    # Ilk 3 ilani detayli goster
    print("=" * 70)
    print("ILK 3 ILAN:")
    print("=" * 70)
    for i, ilan in enumerate(data.get('results', [])[:3], start=1):
        print(f"\n[{i}] {ilan.get('title', 'Baslik yok')}")
        
        sirket = ilan.get('company', {}).get('display_name', 'Sirket yok')
        print(f"    Sirket: {sirket}")
        
        konum = ilan.get('location', {}).get('display_name', 'Konum yok')
        print(f"    Konum: {konum}")
        
        maas_min = ilan.get('salary_min')
        maas_max = ilan.get('salary_max')
        if maas_min and maas_max:
            print(f"    Maas: £{maas_min:,.0f} - £{maas_max:,.0f}")
        else:
            print(f"    Maas: Belirtilmemis")
        
        tarih = ilan.get('created', '')[:10]  # YYYY-MM-DD kismini al
        print(f"    Yayin tarihi: {tarih}")
else:
    print("HATA: API istegi basarisiz oldu.")
    print(f"Yanit: {response.text[:500]}")