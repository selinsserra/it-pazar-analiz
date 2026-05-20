"""
Hafta 5 - Parca 5A
Analiz JSON'undan grafikler uretir, PNG olarak kaydeder.

Calistir: python3 chart_generator.py
Cikti:    data/chart_*.png
"""

import json
import glob
import os
from datetime import date
import matplotlib
matplotlib.use("Agg")  # GUI olmadan calismasi icin (sunucu/cron icin onemli)
import matplotlib.pyplot as plt


# =============== AYARLAR ===============

# Renk paleti (CV'de profesyonel duracak)
RENK_ANA = "#1F4E79"      # koyu mavi
RENK_VURGU = "#2E75B6"    # acik mavi
RENK_ARKAPLAN = "#F5F5F5" # acik gri


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
    
    # En cok arananı 10 tane al
    sirali = sorted(skiller.items(), key=lambda x: x[1], reverse=True)[:10]
    isimler = [s[0] for s in sirali]
    sayilar = [s[1] for s in sirali]
    
    # Yatay bar chart (uzun isimler daha okunakli)
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=RENK_ARKAPLAN)
    ax.set_facecolor(RENK_ARKAPLAN)
    
    # Tersten ciz ki en yuksek en ustte olsun
    isimler_ters = isimler[::-1]
    sayilar_ters = sayilar[::-1]
    
    bars = ax.barh(isimler_ters, sayilar_ters, color=RENK_ANA, edgecolor=RENK_VURGU)
    
    # Sayilari bar'larin ucuna yaz
    for bar, sayi in zip(bars, sayilar_ters):
        ax.text(bar.get_width() + max(sayilar) * 0.01, bar.get_y() + bar.get_height()/2,
                f"{sayi}", va="center", fontsize=10, color=RENK_ANA, fontweight="bold")
    
    ax.set_xlabel("Ilan Sayisi", fontsize=11, color="#333333")
    ax.set_title("En Cok Aranan 10 Skill (UK + Almanya + ABD)",
                 fontsize=14, fontweight="bold", color=RENK_ANA, pad=15)
    
    # Grid ve cerceveyi sadelestir
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(dosya_yolu, dpi=120, bbox_inches="tight", facecolor=RENK_ARKAPLAN)
    plt.close()
    print(f"  ✓ Grafik kaydedildi: {dosya_yolu}")


# =============== GRAFIK 2: ULKEYE GORE MAAS ===============

def grafik_maas_karsilastirma(analiz: dict, dosya_yolu: str) -> None:
    """UK ve ABD'de rol bazinda ortalama maas karsilastirma."""
    maas_stats = analiz.get("maas_istatistikleri", {})
    
    if not maas_stats:
        print("  ! Maas istatistigi yok, grafik atlandi")
        return
    
    # Veriyi rol bazinda topla
    roller = ["data analyst", "data scientist", "python developer"]
    uk_maaslar = []
    us_maaslar = []
    
    for rol in roller:
        uk_key = f"UK_{rol}"
        us_key = f"ABD_{rol}"
        uk_maaslar.append(maas_stats.get(uk_key, {}).get("ort", 0))
        us_maaslar.append(maas_stats.get(us_key, {}).get("ort", 0))
    
    # Grouped bar chart
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=RENK_ARKAPLAN)
    ax.set_facecolor(RENK_ARKAPLAN)
    
    x_pozisyon = range(len(roller))
    bar_genislik = 0.35
    
    bars_uk = ax.bar([x - bar_genislik/2 for x in x_pozisyon], uk_maaslar,
                     bar_genislik, label="UK (GBP)", color=RENK_VURGU, edgecolor=RENK_ANA)
    bars_us = ax.bar([x + bar_genislik/2 for x in x_pozisyon], us_maaslar,
                     bar_genislik, label="ABD (USD)", color=RENK_ANA, edgecolor=RENK_VURGU)
    
    # Sayilari bar'larin ustune yaz
    for bars in [bars_uk, bars_us]:
        for bar in bars:
            yukseklik = bar.get_height()
            if yukseklik > 0:
                ax.text(bar.get_x() + bar.get_width()/2, yukseklik + max(max(uk_maaslar), max(us_maaslar)) * 0.01,
                        f"{int(yukseklik):,}", ha="center", fontsize=9, color="#333333")
    
    ax.set_xticks(x_pozisyon)
    ax.set_xticklabels([r.title() for r in roller], fontsize=11)
    ax.set_ylabel("Ortalama Maas", fontsize=11, color="#333333")
    ax.set_title("Rol Bazinda Ortalama Maas: UK vs ABD",
                 fontsize=14, fontweight="bold", color=RENK_ANA, pad=15)
    ax.legend(loc="upper left", framealpha=0.9)
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(dosya_yolu, dpi=120, bbox_inches="tight", facecolor=RENK_ARKAPLAN)
    plt.close()
    print(f"  ✓ Grafik kaydedildi: {dosya_yolu}")


# =============== ANA AKIS ===============

def main():
    print("=" * 60)
    print("GRAFIK URETIMI BASLIYOR")
    print("=" * 60)
    
    analiz = en_son_analiz_yukle()
    print(f"Veri: {analiz.get('toplam_ilan')} ilan")
    print()
    
    os.makedirs("data", exist_ok=True)
    bugun = date.today()
    
    print("[1/2] Top Skill grafigi:")
    grafik_top_skiller(analiz, f"data/chart_skiller_{bugun}.png")
    
    print("\n[2/2] Maas Karsilastirma grafigi:")
    grafik_maas_karsilastirma(analiz, f"data/chart_maaslar_{bugun}.png")
    
    print("\n" + "=" * 60)
    print("✓ TUM GRAFIKLER URETILDI")
    print("=" * 60)


if __name__ == "__main__":
    main()