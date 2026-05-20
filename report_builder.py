"""
Hafta 5 - Parca 5B
JSON ozeti + AI yorumu + grafikler -> Tek HTML rapor.

Calistir: python3 report_builder.py
Cikti:    data/rapor_YYYY-MM-DD.html
"""

import json
import glob
import base64
import os
from datetime import date


# =============== RENK PALETI ===============

RENK_ANA = "#1F4E79"
RENK_VURGU = "#2E75B6"
RENK_ACIK = "#D5E8F0"
RENK_METIN = "#333333"
RENK_ARKAPLAN = "#F5F5F5"


# =============== YARDIMCI ===============

def en_son_dosya(pattern: str) -> str:
    """Verilen pattern icin en yeni dosyayi bulur."""
    dosyalar = glob.glob(pattern)
    if not dosyalar:
        raise FileNotFoundError(f"Pattern eslestirmedi: {pattern}")
    return max(dosyalar)


def goruntu_base64(dosya_yolu: str) -> str:
    """PNG dosyasini base64 string'e cevirir (HTML icine gomulebilir)."""
    with open(dosya_yolu, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# =============== HTML PARCALARI ===============

def html_baslik(ai: dict, analiz: dict) -> str:
    """Ust baslik bolumu."""
    return f"""
    <div style="background-color: {RENK_ANA}; color: white; padding: 30px 40px; border-radius: 8px 8px 0 0;">
        <h1 style="margin: 0 0 8px 0; font-size: 26px; font-weight: 700;">
            Haftalik IT Pazar Raporu
        </h1>
        <p style="margin: 0; font-size: 14px; opacity: 0.9;">
            Tarih: {ai.get('tarih', '?')} &nbsp;|&nbsp;
            Toplam ilan: {analiz.get('toplam_ilan', '?')} &nbsp;|&nbsp;
            Ulkeler: UK, Almanya, ABD
        </p>
    </div>
    """


def html_yonetici_ozet(yorum: dict) -> str:
    """AI'nin haftalik ozet cümlesi."""
    return f"""
    <div style="background-color: {RENK_ACIK}; padding: 20px 30px; border-left: 4px solid {RENK_ANA};">
        <h2 style="margin: 0 0 10px 0; color: {RENK_ANA}; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
            Haftanin Ozeti
        </h2>
        <p style="margin: 0; color: {RENK_METIN}; font-size: 16px; line-height: 1.6;">
            {yorum.get('haftanin_ozeti', '')}
        </p>
    </div>
    """


def html_yukselen_skiller(yorum: dict) -> str:
    """Yukselen 3 skill'i kartlar halinde goster."""
    skiller = yorum.get("yukselen_skiller", [])
    
    kartlar = ""
    for s in skiller:
        kartlar += f"""
        <div style="background: white; border: 1px solid #E0E0E0; border-radius: 6px; padding: 18px; margin-bottom: 10px;">
            <h3 style="margin: 0 0 6px 0; color: {RENK_ANA}; font-size: 17px;">
                {s.get('skill', '')}
            </h3>
            <p style="margin: 0; color: {RENK_METIN}; font-size: 14px; line-height: 1.5;">
                {s.get('yorum', '')}
            </p>
        </div>
        """
    
    return f"""
    <div style="padding: 30px 40px; background: white;">
        <h2 style="margin: 0 0 18px 0; color: {RENK_ANA}; font-size: 18px;">
            Yukselen Skill'ler
        </h2>
        {kartlar}
    </div>
    """


def html_grafik(baslik: str, b64_veri: str, alt_metin: str = "") -> str:
    """Bir grafigi HTML'e gomülmus base64 olarak ekle."""
    return f"""
    <div style="padding: 20px 40px; background: white; text-align: center;">
        <h2 style="margin: 0 0 15px 0; color: {RENK_ANA}; font-size: 18px; text-align: left;">
            {baslik}
        </h2>
        <img src="data:image/png;base64,{b64_veri}" alt="{alt_metin}"
             style="max-width: 100%; height: auto; border-radius: 4px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
    </div>
    """


def html_maas_icgorüleri(yorum: dict) -> str:
    """Maas icgorulerini madde madde goster."""
    icgoruler = yorum.get("maas_icgorüleri", [])
    
    maddeler = ""
    for ic in icgoruler:
        maddeler += f"""
        <li style="margin-bottom: 12px; line-height: 1.6;">
            {ic}
        </li>
        """
    
    return f"""
    <div style="padding: 20px 40px; background: white;">
        <h2 style="margin: 0 0 15px 0; color: {RENK_ANA}; font-size: 18px;">
            Maas Icgorüleri
        </h2>
        <ul style="margin: 0; padding-left: 20px; color: {RENK_METIN}; font-size: 14px;">
            {maddeler}
        </ul>
    </div>
    """


def html_stratejik_icgoru(yorum: dict) -> str:
    """Vurgulu stratejik icgoru kutusu."""
    return f"""
    <div style="padding: 25px 40px; background: {RENK_ANA}; color: white; margin-top: 10px;">
        <h2 style="margin: 0 0 10px 0; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0.85;">
            Bu Haftanin Stratejik Icgorüsü
        </h2>
        <p style="margin: 0; font-size: 16px; line-height: 1.6; font-weight: 500;">
            {yorum.get('stratejik_icgoru', '')}
        </p>
    </div>
    """


def html_dipnot(yorum: dict, ai: dict) -> str:
    """Veri kalitesi notu + sistem bilgisi."""
    return f"""
    <div style="padding: 20px 40px; background: #FAFAFA; border-top: 1px solid #E0E0E0; font-size: 12px; color: #777;">
        <p style="margin: 0 0 8px 0;">
            <strong>Veri Kalitesi Notu:</strong> {yorum.get('veri_kalitesi_notu', '')}
        </p>
        <p style="margin: 0; opacity: 0.7;">
            Otomatik uretilmistir &nbsp;|&nbsp; Model: {ai.get('model', '?')} &nbsp;|&nbsp;
            Token: giris {ai.get('kullanim', {}).get('giris_token', '?')}, cikis {ai.get('kullanim', {}).get('cikis_token', '?')}
        </p>
    </div>
    """


# =============== ANA HTML KOMPOZISYON ===============

def html_olustur(ai: dict, analiz: dict, grafik1_b64: str, grafik2_b64: str) -> str:
    """Tum parcalari birlestirip son HTML'i uret."""
    yorum = ai.get("yorum", {})
    
    icerik = (
        html_baslik(ai, analiz) +
        html_yonetici_ozet(yorum) +
        html_yukselen_skiller(yorum) +
        html_grafik("En Cok Aranan 10 Skill", grafik1_b64, "Top skiller bar chart") +
        html_maas_icgorüleri(yorum) +
        html_grafik("Rol Bazinda Maas Karsilastirma", grafik2_b64, "Maas karsilastirma chart") +
        html_stratejik_icgoru(yorum) +
        html_dipnot(yorum, ai)
    )
    
    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Haftalik IT Pazar Raporu</title>
</head>
<body style="margin: 0; padding: 20px; background: {RENK_ARKAPLAN}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;">
    <div style="max-width: 720px; margin: 0 auto; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.06);">
        {icerik}
    </div>
</body>
</html>
"""


# =============== ANA AKIS ===============

def main():
    print("=" * 60)
    print("HTML RAPOR URETIMI")
    print("=" * 60)
    
    # 1. AI yorumunu yukle
    ai_dosyasi = en_son_dosya("data/ai_yorum_*.json")
    print(f"AI yorumu: {ai_dosyasi}")
    with open(ai_dosyasi, "r", encoding="utf-8") as f:
        ai = json.load(f)
    
    # 2. Analiz dosyasini yukle
    analiz_dosyasi = en_son_dosya("data/analiz_*.json")
    print(f"Analiz:    {analiz_dosyasi}")
    with open(analiz_dosyasi, "r", encoding="utf-8") as f:
        analiz = json.load(f)
    
    # 3. Grafikleri yukle (base64'e cevir)
    g1_dosyasi = en_son_dosya("data/chart_skiller_*.png")
    g2_dosyasi = en_son_dosya("data/chart_maaslar_*.png")
    print(f"Grafik 1:  {g1_dosyasi}")
    print(f"Grafik 2:  {g2_dosyasi}")
    
    g1_b64 = goruntu_base64(g1_dosyasi)
    g2_b64 = goruntu_base64(g2_dosyasi)
    
    # 4. HTML olustur
    html = html_olustur(ai, analiz, g1_b64, g2_b64)
    
    # 5. Dosyaya kaydet
    cikti_yolu = f"data/rapor_{date.today()}.html"
    with open(cikti_yolu, "w", encoding="utf-8") as f:
        f.write(html)
    
    boyut_kb = os.path.getsize(cikti_yolu) / 1024
    print()
    print("=" * 60)
    print(f"✓ HTML rapor olusturuldu: {cikti_yolu}")
    print(f"✓ Dosya boyutu: {boyut_kb:,.1f} KB")
    print("=" * 60)
    print()
    print("Onizleme icin: VS Code'da dosyaya sag tikla -> 'Open Preview'")
    print("veya tarayicida ac: open data/rapor_*.html")


if __name__ == "__main__":
    main()