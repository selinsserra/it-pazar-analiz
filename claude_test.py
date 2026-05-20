"""
Claude API ilk test istegi.
Amac: API anahtarinin calistigini ve baglantinin saglikli oldugunu dogrulamak.
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
API_KEY = os.getenv("ANTHROPIC_API_KEY")

print(f"API key yuklendi mi? {'EVET' if API_KEY else 'HAYIR'}")
print(f"Anahtar prefix: {API_KEY[:10] if API_KEY else 'YOK'}...")
print()

if not API_KEY:
    print("HATA: ANTHROPIC_API_KEY .env dosyasinda bulunamadi!")
    exit()

# Claude istemcisini olustur
client = Anthropic(api_key=API_KEY)

print("Claude'a test mesaji gonderiliyor...")
print()

# Basit bir test mesaji
mesaj = client.messages.create(
    model="claude-sonnet-4-5",          # Hizli ve uygun maliyetli model
    max_tokens=200,                       # Kisa cevap istiyoruz
    messages=[
        {
            "role": "user",
            "content": "Merhaba! Tek cumleyle kendini tanit ve bu projeye yardim edebilecegini soyle. Turkce cevap ver."
        }
    ]
)

# Cevabi yazdir
print("=" * 60)
print("CLAUDE'UN CEVABI:")
print("=" * 60)
print(mesaj.content[0].text)
print()
print("=" * 60)
print(f"Kullanilan token: giris={mesaj.usage.input_tokens}, cikis={mesaj.usage.output_tokens}")
print(f"Tahmini maliyet: ~${(mesaj.usage.input_tokens * 0.000003 + mesaj.usage.output_tokens * 0.000015):.6f}")