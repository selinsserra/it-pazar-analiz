"""
Hafta 5 - Parca 5C (v2.0)
HTML raporu Gmail SMTP ile e-posta olarak gonderir.
v2.0: Grafikleri CID attachment olarak gomer (Gmail/Outlook tarafindan daha guvenilir gosterilir).

Calistir: python3 email_sender.py
"""

import os
import re
import glob
import smtplib
import base64
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from dotenv import load_dotenv


# =============== AYARLAR ===============

load_dotenv()
GMAIL_ADRES = os.getenv("GMAIL_ADRES")
GMAIL_SIFRE = os.getenv("GMAIL_APP_SIFRE")
ALICI = os.getenv("ALICI_ADRES")

SMTP_SUNUCU = "smtp.gmail.com"
SMTP_PORT = 587


# =============== YARDIMCI ===============

def en_son_rapor_bul() -> str:
    """En yeni HTML rapor dosyasini bul."""
    dosyalar = glob.glob("data/rapor_*.html")
    if not dosyalar:
        raise FileNotFoundError("data/ klasorunde HTML rapor yok!")
    return max(dosyalar)


def base64_grafikleri_cid_ile_degistir(html: str) -> tuple[str, list]:
    """
    HTML icindeki base64 PNG'leri 'cid:grafik_X' referanslariyla degistirir.
    Eklentide gomulecek PNG'lerin (binary veri + cid) listesini doner.
    
    Donen: (degistirilmis_html, [(cid_1, png_bytes_1), (cid_2, png_bytes_2), ...])
    """
    # base64 PNG pattern'i: src="data:image/png;base64,XXXX..."
    pattern = r'src="data:image/png;base64,([^"]+)"'
    
    eklentiler = []
    
    def replacer(match):
        b64_veri = match.group(1)
        # PNG binary'sine cevir
        png_bytes = base64.b64decode(b64_veri)
        # Her grafige benzersiz bir CID ver
        cid = f"grafik_{len(eklentiler) + 1}"
        eklentiler.append((cid, png_bytes))
        # HTML'de src degistir
        return f'src="cid:{cid}"'
    
    yeni_html = re.sub(pattern, replacer, html)
    return yeni_html, eklentiler


# =============== E-POSTA GONDERME ===============

def eposta_gonder(html_icerik: str, konu: str, alici: str) -> None:
    """Gmail SMTP ile HTML e-posta + gomulu grafikler gonderir."""
    
    # base64 grafikleri CID ile degistir
    html_temiz, eklentiler = base64_grafikleri_cid_ile_degistir(html_icerik)
    print(f"  Tespit edilen gomulu grafik sayisi: {len(eklentiler)}")
    
    # MIME yapisi: "related" cunku HTML + ona ait gomulu resimler birlikte
    mesaj = MIMEMultipart("related")
    mesaj["Subject"] = konu
    mesaj["From"] = GMAIL_ADRES
    mesaj["To"] = alici
    
    # Ic kisim: alternative (plain + html)
    alt = MIMEMultipart("alternative")
    mesaj.attach(alt)
    
    duz_metin = "Bu e-posta HTML formatindadir. Lutfen HTML destekli bir istemcide goruntuleyin."
    alt.attach(MIMEText(duz_metin, "plain"))
    alt.attach(MIMEText(html_temiz, "html"))
    
    # Grafikleri CID ile ekle
    for cid, png_bytes in eklentiler:
        img = MIMEImage(png_bytes, "png")
        img.add_header("Content-ID", f"<{cid}>")
        img.add_header("Content-Disposition", "inline", filename=f"{cid}.png")
        mesaj.attach(img)
    
    # SMTP baglantisi
    print(f"  Gmail SMTP'ye baglaniliyor...")
    with smtplib.SMTP(SMTP_SUNUCU, SMTP_PORT) as server:
        server.starttls()
        server.login(GMAIL_ADRES, GMAIL_SIFRE)
        server.send_message(mesaj)
    
    print(f"  ✓ E-posta gonderildi: {alici}")


# =============== ANA AKIS ===============

def main():
    eksikler = []
    if not GMAIL_ADRES: eksikler.append("GMAIL_ADRES")
    if not GMAIL_SIFRE: eksikler.append("GMAIL_APP_SIFRE")
    if not ALICI: eksikler.append("ALICI_ADRES")
    if eksikler:
        print(f"HATA: .env dosyasinda eksik anahtarlar: {', '.join(eksikler)}")
        return
    
    print("=" * 60)
    print("E-POSTA GONDERIMI (CID destekli)")
    print("=" * 60)
    print(f"  Gonderen: {GMAIL_ADRES}")
    print(f"  Alici:    {ALICI}")
    
    rapor_dosyasi = en_son_rapor_bul()
    print(f"  Rapor:    {rapor_dosyasi}")
    
    with open(rapor_dosyasi, "r", encoding="utf-8") as f:
        html_icerik = f.read()
    
    konu = f"Haftalik IT Pazar Raporu - {date.today()}"
    
    try:
        eposta_gonder(html_icerik, konu, ALICI)
        print()
        print("=" * 60)
        print("✓ BASARILI - Gmail gelen kutunuzu kontrol edin")
        print("  Grafikler artik CID attachment olarak gomulu,")
        print("  manuel 'Display images' tiklamadan gorunmeli.")
        print("=" * 60)
    except smtplib.SMTPAuthenticationError:
        print("\nHATA: Gmail giris basarisiz! .env'i kontrol et.")
    except Exception as e:
        print(f"\nHATA: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()