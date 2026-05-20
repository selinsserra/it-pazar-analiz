# Global IT İş İlanı Pazar Analiz Sistemi

Yapay zeka, bulut teknolojileri ve veri mühendisliği gibi alanların hızla dönüştüğü IT sektöründe hangi becerilerin yükselişte olduğunu, hangilerinin geri planda kaldığını ve coğrafyaya göre nasıl farklılaştığını takip etmek için geliştirilmiş **uçtan uca otomatik bir pazar analiz sistemi**.

## Sistem Nasıl Çalışır?
Her hafta:
- **Adzuna API**'den UK, Almanya ve ABD'deki 900+ IT iş ilanı toplanır
- **pandas** ile 60+ teknik skill için regex tabanlı yetkinlik çıkarımı, maaş dağılımı ve ülke karşılaştırması yapılır
- **Anthropic Claude API** ile pazar yorumu ve anomali tespiti üretilir
- **matplotlib** grafikleri ile zenginleştirilmiş **HTML rapor** oluşturulur
- **SMTP** üzerinden e-posta olarak gönderilir
- **GitHub Actions** ile her Pazartesi 09:00'da otomatik çalışır

## Teknolojiler

**Diller & Kütüphaneler:** Python, pandas, requests, regex, matplotlib, smtplib, python-dotenv
**API & Veri:** Anthropic Claude API, Adzuna REST API, JSON, CSV
**DevOps & Otomasyon:** Git, GitHub, GitHub Actions (CI/CD), YAML
**Diğer:** HTML Email Templates, .env / Environment Variables

## Proje Yapısı

## Manuel Çalıştırma

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# .env dosyasını oluştur (örnek için .env.example'a bak)

python3 main_scraper.py      # 1. Veri topla
python3 analyzer.py           # 2. Analiz et
python3 ai_analyzer.py        # 3. AI yorumu üret
python3 chart_generator.py    # 4. Grafikleri üret
python3 report_builder.py     # 5. HTML raporu üret
python3 email_sender.py       # 6. E-posta gönder
```

## Veri Kalitesi Notları

- Almanya'da iş ilanlarında maaş bilgisi sadece %7 oranında mevcut (kültürel sebep), maaş analizleri yalnız UK ve ABD üzerinden yapılır
- Skill çıkarımı, Adzuna API'nin sunduğu özet açıklama üzerinden yapılır; gerçek skill talebi raporlanan orandan daha yüksek olabilir

## Lisans

Kişisel öğrenme projesi.