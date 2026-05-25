"""
Hafta 5 - Parca 5A (v2.0)
Analiz JSON'undan grafikler uretir, PNG olarak kaydeder.

v2.0 yenilikleri:
- 7 ana grup destegi (eski 3 rol degil)
- 4 ulke maas analizi (UK, ABD, Almanya, Polonya - Hindistan harici)
- YENI: Ulke x Rol maas heatmap grafigi

Calistir: python3 chart_generator.py
Cikti:    data/chart_*.png (3 dosya)
"""

import json
import glob
import os
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


# =============== AYARLAR ===============

RENK_ANA = "#1F4E79"
RENK_VURGU = "#2E75B6"
RENK_ACIK = "#D5E8F0"
RENK_ARKAPLAN = "#F5F5F5"

# Heatmap icin renk haritasi (acik mavi -> koyu mavi)
HEATMAP_CMAP = "Blues"


# =============== YARDIMCI ===============

def en_son_analiz_yukle() -> dict:
    """En yeni analiz JSON'unu okur."""
    dosyalar = glob.glob("data/analiz_*.json")
    if not dosyalar:
        raise FileNotFoundError("data/ klasorunde analiz JSON yok!")
    with open(max(dosyalar), "r", encoding="utf-8") as f:
        return json.load(f)


# =============== GRAFIK 1: TOP SKILL ===============

def grafik_top_skiller(analiz: dict, dosya_yolu: str) -> None:
    """En cok aranan 10 skill'i yatay bar chart olarak ciz."""
    skiller = analiz.get("en_cok_aranan_skiller", {})
    
    sirali = sorted(skiller.items(), key=lambda x: x[1], reverse=True)[:10]
    isimler = [s[0] for s in sirali]
    sayilar = [s[1] for s in sirali]
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=RENK_ARKAPLAN)
    ax.set_facecolor(RENK_ARKAPLAN)
    
    isimler_ters = isimler[::-1]
    sayilar_ters = sayilar[::-1]
    
    bars = ax.barh(isimler_ters, sayilar_ters, color=RENK_ANA, edgecolor=RENK_VURGU)
    
    for bar, sayi in zip(bars, sayilar_ters):
        ax.text(bar.get_width() + max(sayilar) * 0.01, bar.get_y() + bar.get_height()/2,
                f"{sayi}", va="center", fontsize=10, color=RENK_ANA, fontweight="bold")
    
    ax.set_xlabel("Ilan Sayisi", fontsize=11, color="#333333")
    ax.set_title("En Cok Aranan 10 Skill (5 Ulke, 7 Meslek Grubu)",
                 fontsize=14, fontweight="bold", color=RENK_ANA, pad=15)
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(dosya_yolu, dpi=120, bbox_inches="tight", facecolor=RENK_ARKAPLAN)
    plt.close()
    print(f"  ✓ Grafik kaydedildi: {dosya_yolu}")


# =============== GRAFIK 2: ROL BAZINDA ILAN SAYISI ===============

def grafik_rol_dagilimi(analiz: dict, dosya_yolu: str) -> None:
    """7 ana grup icin ilan sayilarini gosterir."""
    rol_dagilimi = analiz.get("rol_dagilimi", {})
    
    if not rol_dagilimi:
        print("  ! rol_dagilimi yok, grafik atlandi")
        return
    
    sirali = sorted(rol_dagilimi.items(), key=lambda x: x[1], reverse=True)
    isimler = [s[0] for s in sirali]
    sayilar = [s[1] for s in sirali]
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=RENK_ARKAPLAN)
    ax.set_facecolor(RENK_ARKAPLAN)
    
    isimler_ters = isimler[::-1]
    sayilar_ters = sayilar[::-1]
    
    bars = ax.barh(isimler_ters, sayilar_ters, color=RENK_VURGU, edgecolor=RENK_ANA)
    
    for bar, sayi in zip(bars, sayilar_ters):
        ax.text(bar.get_width() + max(sayilar) * 0.01, bar.get_y() + bar.get_height()/2,
                f"{sayi}", va="center", fontsize=10, color=RENK_ANA, fontweight="bold")
    
    ax.set_xlabel("Ilan Sayisi", fontsize=11, color="#333333")
    ax.set_title("Meslek Grubu Bazinda Toplam Ilan Sayisi (5 Ulke Birlesik)",
                 fontsize=14, fontweight="bold", color=RENK_ANA, pad=15)
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(dosya_yolu, dpi=120, bbox_inches="tight", facecolor=RENK_ARKAPLAN)
    plt.close()
    print(f"  ✓ Grafik kaydedildi: {dosya_yolu}")


# =============== GRAFIK 3: ULKE x ROL MAAS HEATMAP ===============

def grafik_maas_heatmap(analiz: dict, dosya_yolu: str) -> None:
    """
    Ulke x Rol maas heatmap'i.
    Satirlar: 4 ulke (UK, ABD, Almanya, Polonya) - Hindistan harici
    Sutunlar: 7 ana grup
    Hucre: Ortalama maas (kendi para biriminde, normalize edilmedi - karsilastirma icin format string)
    """
    maas_stats = analiz.get("maas_istatistikleri", {})
    
    if not maas_stats:
        print("  ! Maas istatistigi yok, grafik atlandi")
        return
    
    ULKELER = ["UK", "ABD", "Almanya", "Polonya"]
    ROLLER = [
        "Makine Ogrenmesi Muhendisi",
        "Veri Muhendisi",
        "Bulut Muhendisi",
        "Siber Guvenlik",
        "DevOps Muhendisi",
        "Veri/Is Analisti",
        "Yazilim Muhendisi"
    ]
    
    # 2D matris olustur (satir = ulke, sutun = rol)
    matris = np.zeros((len(ULKELER), len(ROLLER)))
    
    for i, ulke in enumerate(ULKELER):
        for j, rol in enumerate(ROLLER):
            key = f"{ulke}_{rol}"
            ort_maas = maas_stats.get(key, {}).get("ort", 0)
            matris[i, j] = ort_maas
    
    # Grafigi olustur
    fig, ax = plt.subplots(figsize=(12, 5), facecolor=RENK_ARKAPLAN)
    
    im = ax.imshow(matris, cmap=HEATMAP_CMAP, aspect="auto")
    
    # Eksen etiketleri
    ax.set_xticks(np.arange(len(ROLLER)))
    ax.set_yticks(np.arange(len(ULKELER)))
    ax.set_xticklabels(ROLLER, rotation=30, ha="right", fontsize=10)
    ax.set_yticklabels(ULKELER, fontsize=11, fontweight="bold")
    
    # Her hucreye sayisal deger yaz
    max_deger = matris.max() if matris.max() > 0 else 1
    for i in range(len(ULKELER)):
        for j in range(len(ROLLER)):
            deger = matris[i, j]
            if deger > 0:
                # Hucre koyu ise beyaz yazi, acik ise koyu yazi
                metin_renk = "white" if deger > max_deger * 0.5 else RENK_ANA
                ax.text(j, i, f"{int(deger):,}", ha="center", va="center",
                        color=metin_renk, fontsize=9, fontweight="bold")
            else:
                ax.text(j, i, "-", ha="center", va="center", color="#999", fontsize=10)
    
    ax.set_title("Ulke x Meslek Grubu - Ortalama Maas Heatmap\n(Hindistan harici, her ulke kendi para biriminde)",
                 fontsize=13, fontweight="bold", color=RENK_ANA, pad=15)
    
    # Renk skalasi cubugu
    cbar = plt.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("Ortalama Maas", fontsize=10, color="#333333")
    
    plt.tight_layout()
    plt.savefig(dosya_yolu, dpi=120, bbox_inches="tight", facecolor=RENK_ARKAPLAN)
    plt.close()
    print(f"  ✓ Grafik kaydedildi: {dosya_yolu}")


# =============== ANA AKIS ===============

def main():
    print("=" * 60)
    print("GRAFIK URETIMI v2.0")
    print("=" * 60)
    
    analiz = en_son_analiz_yukle()
    print(f"Veri: {analiz.get('toplam_ilan')} ilan, {analiz.get('skill_bulunma_orani_yuzde')}% skill orani")
    print()
    
    os.makedirs("data", exist_ok=True)
    bugun = date.today()
    
    print("[1/3] Top Skill grafigi:")
    grafik_top_skiller(analiz, f"data/chart_skiller_{bugun}.png")
    
    print("\n[2/3] Rol Dagilimi grafigi:")
    grafik_rol_dagilimi(analiz, f"data/chart_roller_{bugun}.png")
    
    print("\n[3/3] Maas Heatmap grafigi:")
    grafik_maas_heatmap(analiz, f"data/chart_maaslar_{bugun}.png")
    
    print("\n" + "=" * 60)
    print("✓ TUM GRAFIKLER URETILDI (3 adet)")
    print("=" * 60)


if __name__ == "__main__":
    main()