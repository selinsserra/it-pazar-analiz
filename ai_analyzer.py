"""
AI Analyzer - Hafta 4
JSON ozeti Claude'a gonderip pazar yorumu uretir.

Calistir: python3 ai_analyzer.py
Cikti:    data/ai_yorum_YYYY-MM-DD.json
"""

import os
import json
import glob
from datetime import date
from dotenv import load_dotenv
from anthropic import Anthropic

# =============== AYARLAR ===============

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

MODEL = "claude-sonnet-4-5"
MAX_TOKENS = 2000


# =============== YARDIMCI FONKSIYONLAR ===============

def en_son_json_dosyasini_bul() -> str:
    """data/ klasorundeki en yeni analiz JSON dosyasini bulur."""
    dosyalar = glob.glob("data/analiz_*.json")
    if not dosyalar:
        raise FileNotFoundError("data/ klasorunde analiz JSON bulunamadi! Once analyzer.py calistir.")
    return max(dosyalar)


def ozeti_yukle(dosya_yolu: str) -> dict:
    """JSON ozet dosyasini Python sozlugune yukler."""
    with open(dosya_yolu, "r", encoding="utf-8") as f:
        return json.load(f)


# =============== PROMPT OLUSTURMA ===============

SISTEM_MESAJI = """Sen 15 yillik deneyime sahip bir IT pazar analistisin.
Gorevin: Haftalik IT is ilani verisini analiz edip somut, eyleme gecirilebilir icgoruler uretmek.

Veri kapsami (her zaman dogru ifade et):
- 5 ulke: ABD (USD), Birlesik Krallik (GBP), Almanya (EUR), Polonya (PLN), Hindistan (INR)
- Maas analizi 4 ulkeyi kapsar (UK, ABD, Almanya, Polonya). Hindistan maas analizinden haric tutulmustur cunku INR olcegi diger ulkelerden cok farkli.
- 7 meslek grubu: Makine Ogrenmesi Muhendisi, Veri Muhendisi, Bulut Muhendisi, Siber Guvenlik, DevOps Muhendisi, Veri/Is Analisti, Yazilim Muhendisi

Kritik kurallar:
- Maas karsilastirmasi yaparken para birimini her zaman belirt (Almanya EUR, Polonya PLN, UK GBP, ABD USD). Farkli para birimlerini dogrudan kiyaslama, sadece kendi ulkesi icindeki goreceli buyuklugu tartis.
- "USA ve UK'nin verileri kullanildi" gibi eksik kapsam ifadeleri kullanma. Maas analizi 4 ulkeyi kapsar.
- Sadece veride GERCEKTEN gorunen seyleri yorumla. Uydurma yapma.
- Sayilara dayan, abartili dil kullanma ("inanilmaz", "muhtesem" yok).
- Cevabin SADECE gecerli JSON olsun. Markdown, ek aciklama, "iste cevabim" gibi giris yok.
- Turkce yaz.
"""

KULLANICI_PROMPTU_SABLON = """Asagida bu haftanin global IT pazar verisi var.
Lutfen analiz et ve TAM olarak su JSON formatinda cevap ver:

{{
  "haftanin_ozeti": "2-3 cumlelik genel durum ozeti",
  "yukselen_skiller": [
    {{"skill": "...", "yorum": "Tek cumle aciklama"}},
    {{"skill": "...", "yorum": "..."}},
    {{"skill": "...", "yorum": "..."}}
  ],
  "maas_icgorüleri": [
    "Maas verisinde dikkat ceken bir bulgu - kullandigin her sayinin yaninda para birimini yaz (USD, GBP, EUR, PLN)",
    "Ulkeler arasi bir karsilastirma - her ulkenin maasini KENDI para biriminde belirt, dogrudan rakam karsilastirmasi yapma",
    "Skill bazli bir gozlem - hangi ulkenin verisi oldugunu ve para birimini belirt"
  ],
  "stratejik_icgoru": "Bu haftanin tek en degerli bulgusu. Sektoru izleyen biri icin neden onemli oldugunu acikla. 2-3 cumle.",
  "veri_kalitesi_notu": "Veride dikkat edilmesi gereken bir konu (ornegin maas bilgisi orani, skill bulunma orani gibi)"
}}

VERI:
{veri_json}
"""


def prompt_olustur(ozet: dict) -> str:
    """JSON ozeti kullanici promptuna gomuyoruz."""
    veri_str = json.dumps(ozet, ensure_ascii=False, indent=2)
    return KULLANICI_PROMPTU_SABLON.format(veri_json=veri_str)


# =============== CLAUDE'A GONDER ===============

def claude_ile_analiz_et(prompt: str) -> tuple[str, dict]:
    """
    Claude'a istek atar, cevabi ve token kullanim bilgisini doner.
    """
    client = Anthropic(api_key=API_KEY)
    
    print(f"Claude'a istek gonderiliyor (model: {MODEL})...")
    mesaj = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SISTEM_MESAJI,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    cevap = mesaj.content[0].text
    kullanim = {
        "giris_token": mesaj.usage.input_tokens,
        "cikis_token": mesaj.usage.output_tokens,
        "tahmini_maliyet_usd": round(
            mesaj.usage.input_tokens * 0.000003 + mesaj.usage.output_tokens * 0.000015, 6
        )
    }
    
    return cevap, kullanim


def cevabi_parse_et(cevap: str) -> dict:
    """
    Claude'un JSON cevabini Python sozlugune cevirir.
    Bazen Claude ` ```json ... ``` ` ile sarar, onu temizleriz.
    """
    cevap = cevap.strip()
    # Markdown code block temizle
    if cevap.startswith("```"):
        cevap = cevap.split("```")[1]
        if cevap.startswith("json"):
            cevap = cevap[4:]
        cevap = cevap.strip()
    if cevap.endswith("```"):
        cevap = cevap[:-3].strip()
    
    return json.loads(cevap)


# =============== CIKTI GOSTER ===============

def yorumu_yazdir(yorum: dict) -> None:
    """AI yorumunu insan okunabilir formatta terminale yazdir."""
    print("\n" + "=" * 70)
    print("AI PAZAR YORUMU")
    print("=" * 70)
    
    print(f"\n[HAFTANIN OZETI]")
    print(yorum.get("haftanin_ozeti", ""))
    
    print(f"\n[YUKSELEN SKILLER]")
    for s in yorum.get("yukselen_skiller", []):
        print(f"  • {s['skill']}: {s['yorum']}")
    
    print(f"\n[MAAS ICGORULERI]")
    for ic in yorum.get("maas_icgorüleri", []):
        print(f"  • {ic}")
    
    print(f"\n[STRATEJIK ICGORU]")
    print(yorum.get("stratejik_icgoru", ""))
    
    print(f"\n[VERI KALITESI NOTU]")
    print(yorum.get("veri_kalitesi_notu", ""))
    print()


# =============== ANA AKIS ===============

def main():
    if not API_KEY:
        print("HATA: ANTHROPIC_API_KEY .env dosyasinda bulunamadi!")
        return
    
    # 1. En son analiz JSON'ini bul
    json_yolu = en_son_json_dosyasini_bul()
    print(f"Analiz dosyasi: {json_yolu}")
    
    # 2. Ozeti yukle
    ozet = ozeti_yukle(json_yolu)
    print(f"Toplam ilan: {ozet.get('toplam_ilan')}")
    print(f"Skill bulunma orani: %{ozet.get('skill_bulunma_orani_yuzde')}")
    print()
    
    # 3. Prompt olustur
    prompt = prompt_olustur(ozet)
    print(f"Prompt uzunlugu: {len(prompt)} karakter")
    print()
    
    # 4. Claude'a gonder
    cevap, kullanim = claude_ile_analiz_et(prompt)
    print(f"Token kullanim: giris={kullanim['giris_token']}, cikis={kullanim['cikis_token']}")
    print(f"Tahmini maliyet: ${kullanim['tahmini_maliyet_usd']}")
    
    # 5. Cevabi parse et
    try:
        yorum = cevabi_parse_et(cevap)
    except json.JSONDecodeError as e:
        print(f"\nHATA: Claude'un cevabi gecerli JSON degil!")
        print(f"Ham cevap:\n{cevap}")
        return
    
    # 6. Terminale yazdir
    yorumu_yazdir(yorum)
    
    # 7. Dosyaya kaydet
    cikti = {
        "tarih": str(date.today()),
        "kaynak_analiz": json_yolu,
        "model": MODEL,
        "kullanim": kullanim,
        "yorum": yorum
    }
    
    dosya = f"data/ai_yorum_{date.today()}.json"
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(cikti, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✓ AI yorumu kaydedildi: {dosya}")
    print(f"✓ Dosya boyutu: {os.path.getsize(dosya):,} bayt")
    print("=" * 70)


if __name__ == "__main__":
    main()
    