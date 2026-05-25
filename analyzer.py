"""
IT Is Ilani Pazar Analizi
Parca 3A: Veri yukleme + temel istatistikler

Calistir: python3 analyzer.py
"""

import pandas as pd
from datetime import date
import os
import glob
import re




# =============== VERI YUKLEME ===============

def en_son_csv_dosyasini_bul() -> str:
    """
    data/ klasorundeki en yeni ilanlar_*.csv dosyasini bulur.
    Boylece yarin yeni CSV gelirse o kullanilir.
    """
    dosyalar = glob.glob("data/ilanlar_*.csv")
    if not dosyalar:
        raise FileNotFoundError("data/ klasorunde CSV bulunamadi! Once main_scraper.py calistir.")
    return max(dosyalar)  # alfabetik max = en yeni tarih


def veriyi_yukle(dosya_yolu: str) -> pd.DataFrame:
    """CSV'yi DataFrame'e yukler."""
    df = pd.read_csv(dosya_yolu)
    return df


# =============== TEMEL ANALIZLER ===============

def temel_ozet(df: pd.DataFrame) -> None:
    """Veri setinin genel saglik raporunu yazdirir."""
    print("=" * 70)
    print("VERI SETI OZETI")
    print("=" * 70)
    print(f"Toplam ilan sayisi: {len(df):,}")
    print(f"Sutun sayisi: {len(df.columns)}")
    print(f"Cekim tarihi: {df['cekim_tarihi'].iloc[0]}")
    print(f"En eski ilan: {df['ilan_tarihi'].min()}")
    print(f"En yeni ilan: {df['ilan_tarihi'].max()}")
    print()


def ulke_dagilimi(df: pd.DataFrame) -> None:
    """Ulkelere gore ilan dagilimini gosterir."""
    print("=" * 70)
    print("ULKE BAZINDA ILAN DAGILIMI")
    print("=" * 70)
    
    sayim = df["ulke"].value_counts()
    yuzdelik = df["ulke"].value_counts(normalize=True) * 100
    
    print(f"{'Ulke':<12} {'Ilan':>8} {'Oran':>8}")
    print("-" * 30)
    for ulke in sayim.index:
        print(f"{ulke:<12} {sayim[ulke]:>8} {yuzdelik[ulke]:>7.1f}%")
    print()


def arama_dagilimi(df: pd.DataFrame) -> None:
    """Hangi rolde kac ilan var?"""
    print("=" * 70)
    print("ANA GRUP BAZINDA ILAN DAGILIMI")
    print("=" * 70)
    
    sayim = df["ana_grup"].value_counts()
    print(sayim.to_string())
    print()


def ulke_x_rol_caprazi(df: pd.DataFrame) -> None:
    """Hangi ulkede hangi rol kac ilan? (capraz tablo)"""
    print("=" * 70)
    print("ULKE x ROL CAPRAZ TABLOSU")
    print("=" * 70)
    
    capraz = pd.crosstab(df["ulke"], df["ana_grup"])
    print(capraz.to_string())
    print()


def en_aktif_sirketler(df: pd.DataFrame, top_n: int = 10) -> None:
    """En cok ilan veren sirketleri listeler."""
    print("=" * 70)
    print(f"EN AKTIF {top_n} SIRKET")
    print("=" * 70)
    
    # Bos sirket isimlerini cikar
    df_temiz = df[df["sirket"].notna() & (df["sirket"] != "")]
    sayim = df_temiz["sirket"].value_counts().head(top_n)
    
    print(f"{'Sirket':<45} {'Ilan':>5}")
    print("-" * 52)
    for sirket, adet in sayim.items():
        # Cok uzun sirket ismini kisalt
        kisa_isim = sirket[:42] + "..." if len(sirket) > 45 else sirket
        print(f"{kisa_isim:<45} {adet:>5}")
    print()


def sehir_dagilimi(df: pd.DataFrame, top_n: int = 15) -> None:
    """En cok ilan olan sehirler."""
    print("=" * 70)
    print(f"EN AKTIF {top_n} SEHIR/KONUM")
    print("=" * 70)
    
    # Konumu temizle: virgulden once gelen kismi al (ilk parca = sehir)
    df_temiz = df.copy()
    df_temiz["sehir"] = df_temiz["konum"].fillna("").str.split(",").str[0].str.strip()
    df_temiz = df_temiz[df_temiz["sehir"] != ""]
    
    sayim = df_temiz["sehir"].value_counts().head(top_n)
    
    print(f"{'Sehir':<35} {'Ilan':>5}")
    print("-" * 42)
    for sehir, adet in sayim.items():
        print(f"{sehir:<35} {adet:>5}")
    print()


def maas_bilgisi_oran(df: pd.DataFrame) -> None:
    """Maas bilgisi olan ilanlarin orani (ulkeye gore)."""
    print("=" * 70)
    print("MAAS BILGISI BULUNMA ORANI")
    print("=" * 70)
    
    print(f"{'Ulke':<12} {'Maasli':>8} {'Toplam':>8} {'Oran':>8}")
    print("-" * 38)
    for ulke in df["ulke"].unique():
        ulke_df = df[df["ulke"] == ulke]
        maasli = ulke_df["maas_min"].notna().sum()
        toplam = len(ulke_df)
        oran = (maasli / toplam) * 100 if toplam > 0 else 0
        print(f"{ulke:<12} {maasli:>8} {toplam:>8} {oran:>7.1f}%")
    print()

# =============== SKILL CIKARIMI ===============

# Aradigimiz skill'lerin listesi
# Her skill: (gosterilecek_isim, regex_pattern_listesi)
# regex pattern'lerinde \b = "kelime siniri" (tam kelime eslesmesi)
SKILL_LISTESI = {
    # =========================================================
    # PROGRAMLAMA DILLERI
    # =========================================================
    "Python":       [r"\bpython\b"],
    "Java":         [r"\bjava\b(?!script)"],
    "JavaScript":   [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript":   [r"\btypescript\b", r"\bts\b"],
    "C++":          [r"\bc\+\+"],
    "C#":           [r"\bc#\b", r"\bc-sharp\b"],
    "Go":           [r"\bgolang\b", r"\bgo lang\b"],
    "Rust":         [r"\brust\b"],
    "Ruby":         [r"\bruby\b"],
    "PHP":          [r"\bphp\b"],
    "Scala":        [r"\bscala\b"],
    "R":            [r"\br language\b", r"\br programming\b"],
    "Bash":         [r"\bbash\b"],
    "PowerShell":   [r"\bpowershell\b", r"\bpower shell\b"],

    # =========================================================
    # VERI & ANALITIK
    # =========================================================
    "SQL":          [r"\bsql\b"],
    "PostgreSQL":   [r"\bpostgresql\b", r"\bpostgres\b"],
    "MySQL":        [r"\bmysql\b"],
    "MongoDB":      [r"\bmongodb\b", r"\bmongo\b"],
    "Redis":        [r"\bredis\b"],
    "Elasticsearch":[r"\belasticsearch\b", r"\belastic search\b"],
    "Cassandra":    [r"\bcassandra\b"],
    "DynamoDB":     [r"\bdynamodb\b", r"\bdynamo db\b"],
    "Snowflake":    [r"\bsnowflake\b"],
    "BigQuery":     [r"\bbigquery\b", r"\bbig query\b"],
    "Redshift":     [r"\bredshift\b", r"\bamazon redshift\b"],
    "Databricks":   [r"\bdatabricks\b"],
    "Delta Lake":   [r"\bdelta lake\b"],
    "Iceberg":      [r"\bapache iceberg\b", r"\biceberg\b"],
    "Trino":        [r"\btrino\b", r"\bpresto db?\b"],
    "Tableau":      [r"\btableau\b"],
    "Power BI":     [r"\bpower bi\b", r"\bpowerbi\b"],
    "Looker":       [r"\blooker\b"],
    "Metabase":     [r"\bmetabase\b"],
    "DAX":          [r"\bdax formula\b", r"\bdax measure\b"],
    "Excel":        [r"\bexcel\b", r"\bms excel\b"],

    # =========================================================
    # ML & AI
    # =========================================================
    "Machine Learning":  [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning":     [r"\bdeep learning\b"],
    "TensorFlow":        [r"\btensorflow\b", r"\btensor flow\b"],
    "PyTorch":           [r"\bpytorch\b", r"\bpy torch\b"],
    "Scikit-learn":      [r"\bscikit-learn\b", r"\bsklearn\b"],
    "XGBoost":           [r"\bxgboost\b"],
    "LightGBM":          [r"\blightgbm\b", r"\blight gbm\b"],
    "NLP":               [r"\bnlp\b", r"\bnatural language processing\b"],
    "Computer Vision":   [r"\bcomputer vision\b"],
    "LLM":               [r"\bllm\b", r"\blarge language model\b"],
    "Generative AI":     [r"\bgenerative ai\b", r"\bgen ai\b", r"\bgenai\b"],
    "Prompt Engineering":[r"\bprompt engineering\b"],
    "Hugging Face":      [r"\bhugging face\b", r"\bhuggingface\b"],
    "LangChain":         [r"\blangchain\b"],
    "RAG":               [r"\bretrieval.augmented generation\b", r"\brag pipeline\b"],
    "OpenAI":            [r"\bopenai\b", r"\bopenai api\b"],
    "Vector Database":   [r"\bvector database\b", r"\bvector db\b"],
    "Pinecone":          [r"\bpinecone\b"],
    "Weaviate":          [r"\bweaviate\b"],
    "MLflow":            [r"\bmlflow\b"],
    "Kubeflow":          [r"\bkubeflow\b"],
    "Weights & Biases":  [r"\bweights & biases\b", r"\bwandb\b"],

    # =========================================================
    # CLOUD - AWS
    # =========================================================
    "AWS":             [r"\baws\b", r"\bamazon web services\b"],
    "AWS Lambda":      [r"\baws lambda\b", r"\blambda function\b"],
    "AWS S3":          [r"\baws s3\b", r"\bs3 bucket\b", r"\bamazon s3\b"],
    "AWS EC2":         [r"\baws ec2\b", r"\bec2 instance\b"],
    "AWS EKS":         [r"\baws eks\b", r"\beks cluster\b"],
    "AWS RDS":         [r"\baws rds\b", r"\brds database\b"],
    "AWS Glue":        [r"\baws glue\b", r"\bglue etl\b"],
    "AWS SageMaker":   [r"\bsagemaker\b", r"\baws sagemaker\b"],

    # =========================================================
    # CLOUD - AZURE
    # =========================================================
    "Azure":              [r"\bazure\b"],
    "Azure Functions":    [r"\bazure functions?\b"],
    "Azure DevOps":       [r"\bazure devops\b"],
    "Azure Data Factory": [r"\bazure data factory\b", r"\badf pipeline\b"],
    "Azure AKS":          [r"\bazure aks\b", r"\baks cluster\b"],
    "Azure Synapse":      [r"\bsynapse analytics?\b", r"\bazure synapse\b"],

    # =========================================================
    # CLOUD - GCP
    # =========================================================
    "GCP":              [r"\bgcp\b", r"\bgoogle cloud\b"],
    "GCP Dataflow":     [r"\bgcp dataflow\b", r"\bdataflow pipeline\b"],
    "GCP Vertex AI":    [r"\bvertex ai\b"],
    "GCP Cloud Run":    [r"\bcloud run\b"],

    # =========================================================
    # DEVOPS & CI/CD
    # =========================================================
    "Docker":         [r"\bdocker\b"],
    "Kubernetes":     [r"\bkubernetes\b", r"\bk8s\b"],
    "Terraform":      [r"\bterraform\b"],
    "Ansible":        [r"\bansible\b"],
    "Helm":           [r"\bhelm chart\b", r"\bhelm\b"],
    "Puppet":         [r"\bpuppet\b"],
    "Chef":           [r"\bchef config\b"],
    "CI/CD":          [r"\bci/cd\b", r"\bcicd\b"],
    "GitLab CI":      [r"\bgitlab ci\b", r"\bgitlab cicd\b"],
    "GitHub Actions": [r"\bgithub actions?\b"],
    "CircleCI":       [r"\bcircleci\b", r"\bcircle ci\b"],
    "ArgoCD":         [r"\bargocd\b", r"\bargo cd\b"],
    "Jenkins":        [r"\bjenkins\b"],
    "Git":            [r"\bgit\b(?!hub|lab)"],
    "GitHub":         [r"\bgithub\b"],

    # =========================================================
    # OBSERVABILITY
    # =========================================================
    "Prometheus":     [r"\bprometheus\b"],
    "Grafana":        [r"\bgrafana\b"],
    "Datadog":        [r"\bdatadog\b"],
    "New Relic":      [r"\bnew relic\b", r"\bnewrelic\b"],
    "ELK Stack":      [r"\belk stack\b", r"\belasticsearch logstash\b"],
    "OpenTelemetry":  [r"\bopentelemetry\b", r"\botel framework\b"],

    # =========================================================
    # CYBERSECURITY
    # =========================================================
    "SIEM":                [r"\bsiem\b", r"\bsecurity information.event\b"],
    "SOC":                 [r"\bsoc analyst\b", r"\bsecurity operations center\b"],
    "IAM":                 [r"\biam\b", r"\bidentity.access management\b"],
    "Zero Trust":          [r"\bzero trust\b"],
    "OWASP":               [r"\bowasp\b"],
    "Penetration Testing": [r"\bpenetration test\b", r"\bpentest\b", r"\bpen-test\b"],
    "Splunk":              [r"\bsplunk\b"],
    "CrowdStrike":         [r"\bcrowdstrike\b"],
    "Wireshark":           [r"\bwireshark\b"],
    "Burp Suite":          [r"\bburp suite\b", r"\bburpsuite\b"],
    "NIST":                [r"\bnist framework\b", r"\bnist 800\b"],
    "ISO 27001":           [r"\biso 27001\b", r"\biso27001\b"],
    "SOC 2":               [r"\bsoc 2\b", r"\bsoc-2\b"],
    "GDPR":                [r"\bgdpr\b"],
    "Vulnerability":       [r"\bvulnerability assessment\b", r"\bvuln scan\b"],
    "Threat Intelligence": [r"\bthreat intelligence\b", r"\bthreat intel\b"],

    # =========================================================
    # FRONTEND
    # =========================================================
    "React":          [r"\breact\.?js\b", r"\breact\b"],
    "Vue.js":         [r"\bvue\.?js\b"],
    "Next.js":        [r"\bnext\.?js\b"],
    "Svelte":         [r"\bsvelte\b"],
    "Angular":        [r"\bangular\b"],
    "Tailwind":       [r"\btailwind\b", r"\btailwind css\b"],

    # =========================================================
    # BACKEND
    # =========================================================
    "Node.js":        [r"\bnode\.?js\b", r"\bnodejs\b"],
    "NestJS":         [r"\bnest\.?js\b"],
    "Express":        [r"\bexpress\.?js\b"],
    "Django":         [r"\bdjango\b"],
    "Flask":          [r"\bflask\b"],
    "FastAPI":        [r"\bfastapi\b", r"\bfast api\b"],
    "Spring":         [r"\bspring boot\b", r"\bspring framework\b"],

    # =========================================================
    # VERI MUHENDISLIGI
    # =========================================================
    "Spark":          [r"\bspark\b", r"\bapache spark\b"],
    "Airflow":        [r"\bairflow\b", r"\bapache airflow\b"],
    "Kafka":          [r"\bkafka\b", r"\bapache kafka\b"],
    "Hadoop":         [r"\bhadoop\b"],
    "ETL":            [r"\betl\b", r"\bextract.{0,5}transform.{0,5}load\b"],
    "dbt":            [r"\bdbt\b"],
    "Fivetran":       [r"\bfivetran\b"],
    "Airbyte":        [r"\bairbyte\b"],
    "Apache Beam":    [r"\bapache beam\b"],
    "RabbitMQ":       [r"\brabbitmq\b", r"\brabbit mq\b"],
    "Streaming":      [r"\bdata streaming\b", r"\bstream processing\b"],

    # =========================================================
    # API & MIMARI
    # =========================================================
    "REST API":       [r"\brest api\b", r"\brestful\b"],
    "GraphQL":        [r"\bgraphql\b"],
    "gRPC":           [r"\bgrpc\b"],
    "Microservices":  [r"\bmicroservices?\b", r"\bmicro service\b"],
    "Event-Driven":   [r"\bevent.driven\b", r"\bevent driven architecture\b"],

    # =========================================================
    # GENEL & DIGER
    # =========================================================
    "Linux":          [r"\blinux\b"],
    "Agile":          [r"\bagile\b"],
    "Scrum":          [r"\bscrum\b"],
    "Pandas":         [r"\bpandas\b"],
    "NumPy":          [r"\bnumpy\b"],
    "Load Balancing": [r"\bload balanc\b", r"\bnginx\b", r"\bhaproxy\b"],
    "Networking":     [r"\btcp/ip\b", r"\bnetworking protocols?\b"],
}


def metinden_skill_cikar(metin: str) -> list:
    """
    Verilen metinde gecen skill'leri bulur ve listesini doner.
    Buyuk/kucuk harf duyarsizdir.
    """
    if not isinstance(metin, str) or not metin.strip():
        return []
    
    metin_lower = metin.lower()
    bulunan_skillerden = []
    
    for skill_adi, pattern_listesi in SKILL_LISTESI.items():
        # Bu skill icin tanimli pattern'lerden herhangi biri eslesirse, skill bulundu
        for pattern in pattern_listesi:
            if re.search(pattern, metin_lower):
                bulunan_skillerden.append(skill_adi)
                break  # Bu skill bulundu, digerlerini denemeye gerek yok
    
    return bulunan_skillerden


def skill_cikarma_analizi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tum ilanlarin aciklamalarindan skill'leri cikarir,
    df'e yeni 'skiller' kolonu ekler.
    """
    print("=" * 70)
    print("SKILL CIKARIMI YAPILIYOR...")
    print("=" * 70)
    
    df = df.copy()
    df["skiller"] = (df["ilan_basligi"].fillna("") + " " + df["aciklama"].fillna("")).apply(metinden_skill_cikar)
    df["skill_sayisi"] = df["skiller"].apply(len)
    
    # Genel istatistikler
    skill_li_ilan = (df["skill_sayisi"] > 0).sum()
    print(f"En az 1 skill bulunan ilan: {skill_li_ilan} / {len(df)} ({skill_li_ilan*100/len(df):.1f}%)")
    print(f"Ortalama ilan basina skill: {df['skill_sayisi'].mean():.1f}")
    print(f"Maksimum skill bulunan ilan: {df['skill_sayisi'].max()}")
    print()
    
    return df


def en_cok_aranan_skiller(df: pd.DataFrame, top_n: int = 20) -> None:
    """En cok talep edilen skill'leri listeler."""
    print("=" * 70)
    print(f"EN COK ARANAN {top_n} SKILL")
    print("=" * 70)
    
    # Tum skill listelerini tek bir listeye birlestir
    tum_skiller = []
    for skill_listesi in df["skiller"]:
        tum_skiller.extend(skill_listesi)
    
    # value_counts ile say
    skill_serisi = pd.Series(tum_skiller)
    sayim = skill_serisi.value_counts().head(top_n)
    
    # Yuzde olarak da hesapla (kac ilanda gectigine gore)
    print(f"{'Skill':<25} {'Ilan':>6} {'Oran':>8}")
    print("-" * 42)
    for skill, adet in sayim.items():
        oran = (adet / len(df)) * 100
        print(f"{skill:<25} {adet:>6} {oran:>7.1f}%")
    print()


def ulke_bazinda_top_skiller(df: pd.DataFrame, top_n: int = 5) -> None:
    """Her ulke icin en cok aranan skill'ler."""
    print("=" * 70)
    print(f"HER ULKEDE EN COK ARANAN {top_n} SKILL")
    print("=" * 70)
    
    for ulke in df["ulke"].unique():
        ulke_df = df[df["ulke"] == ulke]
        
        # Tum skill'leri topla
        tum_skiller = []
        for skill_listesi in ulke_df["skiller"]:
            tum_skiller.extend(skill_listesi)
        
        if not tum_skiller:
            print(f"\n{ulke}: Skill bulunamadi")
            continue
        
        sayim = pd.Series(tum_skiller).value_counts().head(top_n)
        print(f"\n{ulke}:")
        for skill, adet in sayim.items():
            oran = (adet / len(ulke_df)) * 100
            print(f"  {skill:<22} {adet:>4} ({oran:.0f}%)")
    print()


def rol_bazinda_top_skiller(df: pd.DataFrame, top_n: int = 5) -> None:
    """Her ana grup icin en cok aranan skill'ler."""
    print("=" * 70)
    print(f"HER ANA GRUPTA EN COK ARANAN {top_n} SKILL")
    print("=" * 70)
    
    for rol in df["ana_grup"].unique():
        rol_df = df[df["ana_grup"] == rol]
        
        tum_skiller = []
        for skill_listesi in rol_df["skiller"]:
            tum_skiller.extend(skill_listesi)
        
        if not tum_skiller:
            continue
        
        sayim = pd.Series(tum_skiller).value_counts().head(top_n)
        print(f"\n{rol.upper()}:")
        for skill, adet in sayim.items():
            oran = (adet / len(rol_df)) * 100
            print(f"  {skill:<22} {adet:>4} ({oran:.0f}%)")
    print()

    # =============== MAAS ANALIZI (PARCA 3C) ===============

def maas_istatistikleri(df: pd.DataFrame) -> dict:
    """Ulke ve rol bazinda maas istatistikleri (sadece maasli ilanlar)."""
    print("=" * 70)
    print("MAAS ISTATISTIKLERI")
    print("=" * 70)
    print("(Not: 4 ulke - UK/GBP, ABD/USD, Almanya/EUR, Polonya/PLN. Hindistan/INR olcek farki nedeniyle haric.)")    
    print()
    
    sonuc = {}
    
    # Maasli ilanlar (UK ve ABD)
    # Hindistan INR olcegi farkli, maas analizinden hariç
    maasli = df[df["maas_min"].notna() & df["ulke"].isin(["UK", "ABD", "Almanya", "Polonya"])].copy()
    maasli["maas_ortalama"] = (maasli["maas_min"] + maasli["maas_max"]) / 2
    
    print(f"{'Ulke':<8} {'Rol':<20} {'Adet':>5} {'Min':>10} {'Ort':>10} {'Maks':>10}")
    print("-" * 70)
    
    for ulke in ["UK", "ABD", "Almanya", "Polonya"]:
        for rol in df["ana_grup"].unique():
            alt = maasli[(maasli["ulke"] == ulke) & (maasli["ana_grup"] == rol)]
            if len(alt) == 0:
                continue
            min_m = alt["maas_ortalama"].min()
            ort_m = alt["maas_ortalama"].mean()
            maks_m = alt["maas_ortalama"].max()
            print(f"{ulke:<8} {rol:<20} {len(alt):>5} {min_m:>10,.0f} {ort_m:>10,.0f} {maks_m:>10,.0f}")
            
            sonuc[f"{ulke}_{rol}"] = {
                "adet": len(alt),
                "min": round(min_m),
                "ort": round(ort_m),
                "maks": round(maks_m)
            }
    print()
    return sonuc


def skill_maas_iliskisi(df: pd.DataFrame, top_n: int = 10) -> dict:
    """En sik gecen skill'lerin ortalama maasi (UK + ABD)."""
    print("=" * 70)
    print(f"SKILL BAZINDA ORTALAMA MAAS (UK + ABD, EN SIK {top_n} SKILL)")
    print("=" * 70)
    
    maasli = df[df["maas_min"].notna() & df["ulke"].isin(["UK", "ABD", "Almanya", "Polonya"])].copy()
    maasli["maas_ortalama"] = (maasli["maas_min"] + maasli["maas_max"]) / 2
    
    # En sik gecen skiller
    tum_skiller = []
    for sl in maasli["skiller"]:
        tum_skiller.extend(sl if isinstance(sl, list) else [])
    en_sik = pd.Series(tum_skiller).value_counts().head(top_n).index.tolist()
    
    sonuc = {}
    print(f"{'Skill':<22} {'Adet':>5} {'Ort. Maas':>12}")
    print("-" * 42)
    for skill in en_sik:
        skill_li = maasli[maasli["skiller"].apply(lambda x: skill in x if isinstance(x, list) else False)]
        if len(skill_li) == 0:
            continue
        ort = skill_li["maas_ortalama"].mean()
        print(f"{skill:<22} {len(skill_li):>5} {ort:>12,.0f}")
        sonuc[skill] = {"adet": len(skill_li), "ort_maas": round(ort)}
    print()
    return sonuc


def json_ozet_uret(df: pd.DataFrame, maas_stats: dict, skill_maas: dict) -> None:
    """Hafta 4'te Claude'a gonderecegimiz ozet veriyi JSON dosyasina kaydet."""
    import json
    
    # En cok aranan 20 skill
    tum_skiller = []
    for sl in df["skiller"]:
        tum_skiller.extend(sl if isinstance(sl, list) else [])
    top_skiller = pd.Series(tum_skiller).value_counts().head(20).to_dict()
    
    # Ulke + rol carpaz
    capraz = pd.crosstab(df["ulke"], df["ana_grup"]).to_dict()
    
    ozet = {
        "cekim_tarihi": str(df["cekim_tarihi"].iloc[0]),
        "toplam_ilan": len(df),
        "skill_bulunan_ilan": int((df["skill_sayisi"] > 0).sum()),
        "skill_bulunma_orani_yuzde": round((df["skill_sayisi"] > 0).sum() * 100 / len(df), 1),
        "ulke_dagilimi": df["ulke"].value_counts().to_dict(),
        "rol_dagilimi": df["ana_grup"].value_counts().to_dict(),
        "en_cok_aranan_skiller": top_skiller,
        "maas_istatistikleri": maas_stats,
        "skill_maas_iliskisi": skill_maas,
        "notlar": [
            "Maas analizi 4 ulkeyi kapsar: UK (GBP), ABD (USD), Almanya (EUR), Polonya (PLN). Para birimleri farkli, dogrudan karsilastirma yapmadan once normalize edilmelidir.",
            "Hindistan (INR) maas analizinden haric tutuldu cunku INR olcegi diger 4 ulkeden cok farkli.",
            "Almanya'da maas bilgisi orani diger ulkelerden dusuk (kulturel sebep, isverenler ilanlarda maas paylasmaz), Almanya istatistikleri daha kucuk ornek uzerinden.",
            f"Skill cikarimi {round((df['skill_sayisi'] > 0).sum() * 100 / len(df), 1)}% oraninda basarili (155+ skill icin regex tabanli)."
        ]
    }
    
    os.makedirs("data", exist_ok=True)
    dosya = f"data/analiz_{date.today()}.json"
    with open(dosya, "w", encoding="utf-8") as f:
        json.dump(ozet, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✓ JSON ozet kaydedildi: {dosya}")
    print(f"✓ Dosya boyutu: {os.path.getsize(dosya):,} bayt")
    print("=" * 70)

# =============== ANA AKIS ===============

def main():
    # En son CSV'yi bul
    csv_yolu = en_son_csv_dosyasini_bul()
    print(f"Veri kaynagi: {csv_yolu}\n")
    
    # Yukle
    df = veriyi_yukle(csv_yolu)

    # ==========================================================
    # VERI TEMIZLEME 1: Eski ilanlari filtrele (son 6 ay)
    # Pazar analizini guncel tutmak icin kritik
    # ==========================================================
    from datetime import datetime, timedelta
    
    ham_sayi = len(df)
    bugun = datetime.now()
    alt_sinir = (bugun - timedelta(days=180)).strftime("%Y-%m-%d")
    
    # ilan_tarihi string formatinda, direkt karsilastirilabilir (YYYY-MM-DD)
    df = df[df["ilan_tarihi"] >= alt_sinir].reset_index(drop=True)
    
    eski_atildi = ham_sayi - len(df)
    print(f"VERI TEMIZLEME 1: {eski_atildi} eski ilan (>180 gun) cikarildi -> {len(df)} ilan kaldi")
    print(f"  Tarih filtresi: {alt_sinir} ve sonrasi\n")
    
    # ==========================================================
    # VERI TEMIZLEME: Cift ilanlari kaldir
    # Ayni ilan birden fazla aramada yakalanmis olabilir
    # (ornek: bir Senior Cloud Engineer ilani hem 'cloud engineer'
    # hem 'cloud architect' aramasinda gelebilir)
    # ==========================================================
    ham_sayi = len(df)
    df = df.drop_duplicates(subset=["ilan_url"], keep="first").reset_index(drop=True)
    temiz_sayi = len(df)
    print(f"VERI TEMIZLEME: {ham_sayi - temiz_sayi} cift ilan kaldirildi ({ham_sayi} -> {temiz_sayi})\n")
    
    # Analizleri sirayla calistir
    temel_ozet(df)
    ulke_dagilimi(df)
    arama_dagilimi(df)
    ulke_x_rol_caprazi(df)
    en_aktif_sirketler(df, top_n=10)
    sehir_dagilimi(df, top_n=15)
    maas_bilgisi_oran(df)

    # Skill cikarimi (Parca 3B)
    df = skill_cikarma_analizi(df)
    en_cok_aranan_skiller(df, top_n=20)
    ulke_bazinda_top_skiller(df, top_n=5)
    rol_bazinda_top_skiller(df, top_n=5)

    # Parca 3C: Maas analizi + JSON cikti
    maas_stats = maas_istatistikleri(df)
    skill_maas = skill_maas_iliskisi(df, top_n=10)
    json_ozet_uret(df, maas_stats, skill_maas)
    
    print("=" * 70)
    print("PARCA 3C TAMAMLANDI - HAFTA 3 BITTI")
    print("=" * 70)
    print("Sirada: Skill cikarimi (Parca 3B)")


if __name__ == "__main__":
    main()