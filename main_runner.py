"""
Hafta 6 - Otomasyon
Tum pipeline'i tek seferde calistirir.

Sira: scraper -> analyzer -> ai_analyzer -> chart_generator -> report_builder -> email_sender

Calistir: python3 main_runner.py
"""

import subprocess
import sys
from datetime import datetime


# Calistirilacak betikler (sira onemli!)
ADIMLAR = [
    ("Veri toplama",      "main_scraper.py"),
    ("Veri analizi",      "analyzer.py"),
    ("AI yorumu",         "ai_analyzer.py"),
    ("Grafik uretimi",    "chart_generator.py"),
    ("HTML rapor",        "report_builder.py"),
    ("E-posta gonderim",  "email_sender.py"),
]


def adim_calistir(ad: str, betik: str) -> bool:
    """Tek bir betigi calistirir. Basarili olursa True, hata olursa False doner."""
    print()
    print("=" * 70)
    print(f">>> {ad.upper()}  ({betik})")
    print("=" * 70)
    
    sonuc = subprocess.run(
        [sys.executable, betik],
        capture_output=False,   # Cikti dogrudan terminale aksin
        text=True
    )
    
    if sonuc.returncode == 0:
        print(f"\n✓ {ad} tamamlandi")
        return True
    else:
        print(f"\n✗ {ad} BASARISIZ! Cikis kodu: {sonuc.returncode}")
        return False


def main():
    baslangic = datetime.now()
    
    print("#" * 70)
    print(f"# IT PAZAR ANALIZ PIPELINE - {baslangic.strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 70)
    
    for ad, betik in ADIMLAR:
        basarili = adim_calistir(ad, betik)
        if not basarili:
            print()
            print("#" * 70)
            print(f"# PIPELINE DURDU: '{ad}' adiminda hata olustu")
            print("#" * 70)
            sys.exit(1)  # GitHub Actions'a "basarisiz" sinyali ver
    
    bitis = datetime.now()
    sure = (bitis - baslangic).total_seconds()
    
    print()
    print("#" * 70)
    print(f"# PIPELINE BASARIYLA TAMAMLANDI")
    print(f"# Sure: {sure:.0f} saniye")
    print(f"# Bitis: {bitis.strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 70)


if __name__ == "__main__":
    main()
    