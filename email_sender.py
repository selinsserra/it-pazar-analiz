"""
Hafta 5 - Parca 5C
HTML raporu Gmail SMTP ile e-posta olarak gonderir.

Calistir: python3 email_sender.py
"""

import os
import glob
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


# =============== AYARLAR ===============

load_dotenv()
GMAIL_ADRES = os.getenv("GMAIL_ADRES")
GMAIL_SIFRE = os.getenv("GMAIL_APP_SIFRE")
ALICI = os.getenv("ALICI_ADRES")

SMTP_SUNUCU = "smtp.gmail.com"
SMTP_PORT = 587   # TLS portu


# =============== YARDIMCI ===============

def en_son_rapor_bul() -> str:
    """En yeni HTML rapor dosyasini bul."""
    dosyalar = glob.glob("data/rapor_*.html")
    if not dosyalar:
        raise FileNotFoundError("data/ klasorunde HTML rapor yok! Once report_builder.py calistir.")
    return max(dosyalar)


# =============== E-POSTA GONDERME ===============

def eposta_gonder(html_icerik: str, konu: str, alici: str) -> None:
    """Gmail SMTP ile HTML e-posta gonderir."""
    
    # Multipart mesaj: hem duz metin hem HTML versiyon
    mesaj = MIMEMultipart("alternative")
    mesaj["Subject"] = konu
    mesaj["From"] = GMAIL_ADRES
    mesaj["To"] = alici
    
    # Plain text yedek (HTML acilmayan istemciler icin)
    duz_metin = "Bu e-posta HTML formatindadir. Lutfen HTML destekli bir istemcide goruntuleyin."
    mesaj.attach(MIMEText(duz_metin, "plain"))
    mesaj.attach(MIMEText(html_icerik, "html"))
    
    # SMTP baglantisi
    print(f"Gmail SMTP'ye baglaniliyor ({SMTP_SUNUCU}:{SMTP_PORT})...")
    with smtplib.SMTP(SMTP_SUNUCU, SMTP_PORT) as server:
        server.starttls()   # TLS sifreleme baslat
        print("TLS aktiflesti, giris yapiliyor...")
        server.login(GMAIL_ADRES, GMAIL_SIFRE)
        print("Giris basarili, mesaj gonderiliyor...")
        server.send_message(mesaj)
    
    print(f"✓ E-posta gonderildi: {alici}")


# =============== ANA AKIS ===============

def main():
    # Anahtarlari kontrol et
    eksikler = []
    if not GMAIL_ADRES: eksikler.append("GMAIL_ADRES")
    if not GMAIL_SIFRE: eksikler.append("GMAIL_APP_SIFRE")
    if not ALICI: eksikler.append("ALICI_ADRES")
    
    if eksikler:
        print(f"HATA: .env dosyasinda eksik anahtarlar: {', '.join(eksikler)}")
        return
    
    print("=" * 60)
    print("E-POSTA GONDERIMI")
    print("=" * 60)
    print(f"Gonderen: {GMAIL_ADRES}")
    print(f"Alici:    {ALICI}")
    print()
    
    # En son raporu yukle
    rapor_dosyasi = en_son_rapor_bul()
    print(f"Rapor:    {rapor_dosyasi}")
    
    with open(rapor_dosyasi, "r", encoding="utf-8") as f:
        html_icerik = f.read()
    
    boyut_kb = len(html_icerik) / 1024
    print(f"Boyut:    {boyut_kb:.1f} KB")
    print()
    
    # E-postayi gonder
    konu = f"Haftalik IT Pazar Raporu - {date.today()}"
    
    try:
        eposta_gonder(html_icerik, konu, ALICI)
        print()
        print("=" * 60)
        print("✓ BASARILI - Gmail gelen kutunuzu kontrol edin")
        print("=" * 60)
    except smtplib.SMTPAuthenticationError:
        print("\nHATA: Gmail giris basarisiz!")
        print("Kontrol et:")
        print("  1. GMAIL_APP_SIFRE 16 haneli App Password mi? (normal Gmail sifresi DEGIL)")
        print("  2. 2-Step Verification acik mi?")
        print("  3. App password'u dogru kopyaladin mi?")
    except Exception as e:
        print(f"\nHATA: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()