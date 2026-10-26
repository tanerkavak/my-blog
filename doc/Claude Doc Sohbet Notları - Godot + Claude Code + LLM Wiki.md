# Godot + Claude Code + LLM Wiki: Sohbet Notları

*Claude ile C#, GDScript ve Python çalışma ortamı, CLAUDE.md, LLM Wiki deseni ve token kullanımı üzerine sohbetin derlenmiş hali*

## 1. Çalışma ortamı ve klasör yapısı

Claude Code'u terminalden, **proje kök klasöründe** çalıştır. Claude o klasördeki dosyaları görür ve kök dizindeki `CLAUDE.md` dosyasını her oturumda okur. Projenin kuralları, komutları ve yapısı orada durur, böylece her seferinde baştan anlatmazsın. Kurulum komutu zamanla değişebilir, güncel adımlar için docs.claude.com adresindeki Claude Code bölümüne bak. Aşağıdaki yapı Godot 4 (.NET sürümü) varsayımıyla hazırlandı.

### Önerilen klasör yapısı

```
my-game/
├── CLAUDE.md                 # Claude'un kalıcı hafızası
├── project.godot
├── MyGame.csproj / .sln      # C# için
├── .gitignore                # .godot/, .mono/, bin/, obj/, .venv/
│
├── scenes/                   # .tscn dosyaları
├── scripts/
│   ├── csharp/               # Oyun mantığı, performans gerektirenler
│   └── gdscript/             # Hızlı prototip, UI, küçük davranışlar
├── assets/                   # sprite, ses, font
├── addons/
│
├── tools/                    # Python tarafı (Godot dışı)
│   ├── .venv/
│   ├── requirements.txt
│   ├── export_data.py
│   └── tests/
│
├── data/                     # JSON, CSV gibi ham veri
└── docs/                     # tasarım notları
```

Python'u `tools/` altında tutmak iyi bir fikir: Godot'un kendi dosyalarıyla karışmaz ve kendi sanal ortamı (venv) olur.

### Araç kurulumu

- **Godot 4 .NET sürümü** ve **.NET SDK** (Godot'un istediği sürüm)
- **Python 3.x** ve `tools/` içinde `python -m venv .venv`
- **Git**: Claude'un yaptığı değişiklikleri geri alabilmek için şart, ilk gün `git init` yap
- **VS Code** veya **Rider**: C# için Rider ya da VS Code + C# Dev Kit, GDScript için VS Code'a Godot eklentisi

### Çalışma düzeni

1. Her görevde `git commit` yap, sonra Claude'a görev ver.
2. Görevi küçük tut: "envanter sistemini yaz" yerine "Item sınıfını ve envanter listesini yaz, sonra UI'ı bağlarız".
3. Claude'dan kodu yazdırdıktan sonra çalıştırıp test etmesini iste (`dotnet build`, `pytest`).
4. `.tscn` dosyaları metin tabanlı ama kırılgan. Sahne düzenlemeyi Godot editöründe yapmak, Claude'a script yazdırmak daha güvenli.

## 2. CLAUDE.md içeriği ne olmalı

CLAUDE.md'nin amacı, Claude'un koda bakarak kendi başına çıkaramayacağı bilgileri vermek. Kısa tut, çünkü her oturumda baştan okunur ve uzadıkça önemli kurallar kaybolur. Birkaç yüz satırı geçmemesi iyi olur.

### İçermesi gerekenler

1. **Projenin ne olduğu**: 2-3 cümle (oyun türü, motor sürümü, hedef platform)
2. **Teknoloji ve sürümler**: Godot, .NET, Python sürümü
3. **Klasör yapısı**: hangi klasörde ne var, hangi dil nerede
4. **Komutlar**: derleme, test, çalıştırma (Claude'un kendini doğrulaması için en değerli kısım)
5. **Kod kuralları**: isimlendirme, dil seçimi, mimari tercihler
6. **Dokunulmayacaklar**: elle düzenlenmemesi gereken dosyalar
7. **Mevcut durum**: ne bitti, ne üzerinde çalışılıyor, sıradaki iş

### İçermemesi gerekenler

- Koddan zaten okunabilen şeyler (her sınıfın ne yaptığı gibi)
- Uzun açıklamalar ve tasarım belgeleri (bunlar `docs/` altına, CLAUDE.md'den link ver)
- Genel tavsiyeler ("temiz kod yaz" gibi), çünkü somut olmayan kural işe yaramaz

### Şablon

```markdown
# MyGame

Godot 4.3 (.NET) ile yapılan 2D platformer. Hedef: PC (Windows/Linux).

## Teknoloji
- Godot 4.3 .NET, .NET SDK 8.0
- Python 3.12 (sadece tools/ altında)

## Klasör yapısı
- scenes/            .tscn sahneler
- scripts/csharp/    oyun mantığı, sistemler
- scripts/gdscript/  UI ve küçük sahne betikleri
- tools/             Python araçları (kendi .venv'i var)
- data/              ham JSON/CSV verileri

## Komutlar
- C# derle:        dotnet build
- Python test:     cd tools && .venv/bin/pytest
- Veri dönüştür:   cd tools && .venv/bin/python export_data.py
- Godot headless:  godot --headless --quit

## Kurallar
- Oyun mantığı C#, UI ve basit sahne betikleri GDScript, araçlar Python.
- Bir node'a tek script, iki dili aynı node'da karıştırma.
- İsimlendirme: C# PascalCase, GDScript snake_case, Python PEP8.
- Singleton yerine sinyal/event kullan.
- Yeni özellikte önce kısa plan sun, onay sonrası yaz.

## Dokunma
- project.godot ve .tscn dosyalarını sadece ben istersem düzenle.
- .godot/, bin/, obj/ klasörleri üretilmiş dosyalardır.

## Mevcut durum
- Bitti: oyuncu hareketi, kamera
- Üzerinde çalışılan: envanter sistemi (scripts/csharp/Inventory/)
- Sıradaki: düşman AI
```

### İpuçları

- **`/init` komutu**: Claude Code'da çalıştırırsan Claude projeyi tarayıp ilk taslağı kendisi çıkarır. Sonra sen düzeltirsin.
- **Güncel tut**: Özellikle "Mevcut durum" bölümünü. Eskimiş bilgi, hiç bilgi olmamasından kötüdür.
- **Hatadan öğren**: Claude aynı hatayı tekrarlıyorsa bunu bir kural olarak ekle.
- **Katmanlı kullanım**: Alt klasörlere de ayrı CLAUDE.md koyabilirsin (örneğin `tools/CLAUDE.md` içinde sadece Python kuralları).

## 3. LLM Wiki nedir

Paylaştığın belge, Andrej Karpathy tarzı bir fikir dosyası olan "LLM Wiki" deseni. Kendi bilgi tabanını LLM ile nasıl kuracağını anlatıyor. Belirli bir yazılım ya da hazır şablon değil, kendi LLM ajanına (Claude Code gibi) verip birlikte uyarlamak için yazılmış soyut bir fikir.

### Temel fikir

Normal yöntemde (RAG, dosya yükleme) LLM her soruda belgeleri baştan tarar ve bilgi birikmez. Bu desende LLM, ham kaynakları okuyup **kalıcı bir markdown wiki** yazar ve günceller. Yeni bir kaynak eklediğinde ilgili sayfaları günceller, çelişkileri işaretler, sayfalar arası bağlantıları kurar. Bilgi bir kez derlenir ve güncel tutulur. Sen kaynak seçer ve soru sorarsın, yazma ve düzenleme işini LLM yapar.

### Üç katman

1. **Ham kaynaklar**: makaleler, PDF'ler, notlar. LLM bunları sadece okur, asla değiştirmez.
2. **Wiki**: LLM'in yazdığı markdown sayfaları (özetler, kavram ve varlık sayfaları, karşılaştırmalar).
3. **Şema**: `CLAUDE.md` gibi bir dosya. Wiki'nin nasıl yapılandığını ve LLM'in hangi iş akışlarını izleyeceğini anlatır.

### Tipik klasör yapısı

```
my-wiki/
├── CLAUDE.md          # Şema: kurallar ve iş akışları
├── index.md           # Wiki'nin içerik kataloğu
├── log.md             # Kronolojik kayıt (sadece sona eklenir)
│
├── raw/               # Ham kaynaklar (değiştirilmez)
│   ├── articles/
│   └── assets/
│
└── wiki/              # LLM'in yazdığı sayfalar
    ├── sources/       # Her kaynağın özeti
    ├── entities/      # Kişi, yer, araç, karakter sayfaları
    ├── concepts/      # Kavram sayfaları
    └── analyses/      # Sorulardan çıkan karşılaştırma ve analizler
```

- **index.md**: Her sayfaya link ve tek satırlık özet içerir. LLM soru gelince önce buna bakıp ilgili sayfalara iner.
- **log.md**: Her kayıt `## [2026-04-02] ingest | Başlık` gibi tutarlı bir önekle başlar.

### Üç temel işlem

- **Ingest**: Yeni kaynağı `raw/` içine koyarsın, LLM okur, özet yazar, ilgili sayfaları günceller, index ve log'a ekler.
- **Query**: Wiki'ye soru sorarsın, LLM sayfaları okuyup kaynak göstererek yanıtlar. İyi cevaplar yeni sayfa olarak wiki'ye geri kaydedilebilir.
- **Lint**: Periyodik sağlık kontrolü. Çelişkiler, eskimiş bilgiler, bağlantısız sayfalar, eksik kavramlar aranır.

### Önerilen araçlar

Obsidian (okuma ve graph görünümü), Obsidian Web Clipper (web makalelerini markdown'a çevirir), Git (sürüm geçmişi), isteğe bağlı olarak qmd (büyüyen wiki için yerel arama).

## 4. Ham kaynakları kim ekler, nasıl hazırlanır

Ham kaynakları sen eklersin. Desende senin işin kaynakları seçip `raw/` klasörüne koymak, LLM'in işi de onları okuyup wiki'ye işlemek. LLM `raw/` içine kendi kendine bir şey indirip eklemez, ama istersen "şu konuda açık kaynak bul" diyebilirsin.

### Ne ekleyebilirsin

- C# kitapları (PDF, EPUB)
- Godot resmi dokümantasyonu, Microsoft Learn sayfaları (Obsidian Web Clipper ile markdown'a çevirip)
- Kendi notların, makaleler, video özetleri
- Kendi kod örneklerin

Kitapları kendi kullanımın için eklemen sorun değil. Wiki'yi başkalarıyla paylaşacaksan telifli kitap içeriğini wiki'ye kopyalama, özet ve kendi sözlerinle yazılmış notlar paylaşılabilir.

### Kitapları dönüştür

Kalın bir PDF veya EPUB'u olduğu gibi vermek verimsiz olur. Büyük dosyalar bağlamı doldurur ve PDF'ten çıkan metin bozuk olabilir.

1. **EPUB'u markdown'a çevir**: `pandoc kitap.epub -t markdown -o kitap.md`
2. **PDF'i metne çevir**: `pdftotext` veya `marker` gibi bir araç (taranmış PDF ise OCR gerekir)
3. **Bölümlere ayır**: Her bölüm ayrı dosya olsun (`ch01-types.md`, `ch02-classes.md`...)

Bu dönüştürme işini Claude Code'a da yaptırabilirsin.

### Önerilen düzen

```
raw/
├── books/
│   └── csharp-in-depth/
│       ├── ch01.md
│       └── ch02.md
├── docs/            # Godot ve Microsoft dokümanları
├── articles/
└── assets/
```

Bir kitabı tek seferde değil, **bölüm bölüm** işle: "raw/books/csharp-in-depth/ch01.md dosyasını ingest et." Her bölümden sonra çıkan sayfalara göz atıp yönlendirmen, wiki'nin kalitesini belirler.

## 5. Proje için CLAUDE.md şeması (kod + wiki)

Claude kendi eğitim bilgisini de bilir, bu yüzden "önce wiki ve kaynaklara bak, kaynakta yoksa bunu açıkça belirt" kuralını şemaya yazmak gerekir. Wiki'yi tasarlamak ve bakımını yapmak Claude'un işi, sen sadece kaynak ekler ve soru sorarsın. Kod ve wiki'yi aynı depoda tutmak, Claude'un kod yazarken wiki'yi okumasını sağlar.

### Klasör yapısı

```
my-game/
├── CLAUDE.md
├── raw/                  # Sen eklersin, Claude dokunmaz
│   ├── books/
│   ├── docs/
│   ├── articles/
│   └── assets/
├── wiki/                 # Claude yazar
│   ├── index.md
│   ├── log.md
│   ├── sources/
│   ├── concepts/
│   ├── patterns/
│   └── decisions/
├── scenes/
├── scripts/csharp/
├── scripts/gdscript/
└── tools/                # Python
```

### CLAUDE.md şeması

```markdown
# Proje: MyGame + Bilgi Tabanı

Godot 4.x (.NET) oyunu. C# (oyun mantığı), GDScript (UI, küçük betikler),
Python (tools/ altında araçlar). Bu depo aynı zamanda bir LLM Wiki içerir:
raw/ kaynaklar, wiki/ derlenmiş bilgi.

## Katmanlar
- raw/  : Kullanıcının eklediği kaynaklar. ASLA değiştirme, silme, yeniden adlandırma.
- wiki/ : Sahibi sensin. Sayfaları sen yazar ve güncellersin, kullanıcı okur.
- Kod   : scripts/, scenes/, tools/

## Altın kural: kaynak önceliği
1. Kod yazmadan veya bir soruyu yanıtlamadan önce wiki/index.md'yi oku,
   ilgili wiki sayfalarına, gerekirse raw/ kaynaklarına bak.
2. Cevapta kullandığın bilginin dayandığı sayfayı veya kaynağı belirt
   (örn. "wiki/concepts/signals.md", "raw/books/csharp/ch04.md").
3. Bilgi wiki ve kaynaklarda yoksa kendi bilginle yanıtlayabilirsin ama
   şu etiketi koy: "[Kaynak dışı]". Sonra bunu wiki'ye eklemeyi öner.
4. Kaynaklar birbiriyle veya kendi bilginle çelişirse sessizce seçme,
   çelişkiyi kullanıcıya göster.

## Wiki yapısı
- wiki/index.md    : Tüm sayfaların kataloğu. Her satır: link + tek cümle özet.
                     Kategorilere ayır. Her ingest sonrası güncelle.
- wiki/log.md      : Sadece sona eklenir. Biçim:
                     ## [YYYY-MM-DD] ingest | Başlık
                     ## [YYYY-MM-DD] query  | Soru
                     ## [YYYY-MM-DD] lint   | Özet
- wiki/sources/    : Her kaynak dosyası için bir özet sayfası.
- wiki/concepts/   : Kavramlar (generics, signals, state machine...).
- wiki/patterns/   : Oyun/kod desenleri ve çalışan örnekler.
- wiki/decisions/  : Bu projede aldığımız mimari kararlar ve gerekçeleri.

## Sayfa biçimi
Her wiki sayfası şu frontmatter ile başlar:
---
title:
type: source | concept | pattern | decision
tags: []
sources: [raw/... yolları]
updated: YYYY-MM-DD
---
Sayfalar arası bağlantı için [[sayfa-adi]] kullan. Dosya adları küçük harf,
kısa çizgili (örn. dependency-injection.md).

## İş akışları

### Ingest ("şu kaynağı ingest et")
1. Kaynağı oku. Önemli çıkarımları kullanıcıya kısaca anlat.
2. wiki/sources/ altına özet sayfası yaz.
3. İlgili concept/pattern sayfalarını güncelle, yoksa oluştur.
4. Çelişki veya eskimiş bilgi varsa sayfada işaretle.
5. index.md ve log.md'yi güncelle.
6. Hangi sayfaların değiştiğini listele.
Bir seferde tek kaynak (veya tek bölüm) işle, kullanıcı istemedikçe toplu işleme.

### Query ("şunu sor")
1. index.md'yi oku, ilgili sayfalara in.
2. Kaynak göstererek yanıtla.
3. Değerli bir analiz çıktıysa wiki'ye sayfa olarak kaydetmeyi öner.

### Kodlama ("şunu yaz")
1. İlgili wiki sayfalarını oku, yaklaşımı kısaca planla ve onay iste.
2. Kodu yaz, hangi wiki sayfasına dayandığını belirt.
3. Çalıştırıp doğrula (komutlar aşağıda).
4. Önemli bir mimari karar alındıysa wiki/decisions/ altına yaz.

### Lint ("wiki'yi kontrol et")
Çelişkileri, eskimiş iddiaları, bağlantısız sayfaları, eksik kavram
sayfalarını ve eksik çapraz bağlantıları tara. Rapor ver, düzeltmeleri
onayla sonra uygula.

## Kod kuralları
- Oyun mantığı C#, UI ve basit sahne betikleri GDScript, araçlar Python.
- Bir node'a tek script. İki dili aynı node'da karıştırma.
- İsimlendirme: C# PascalCase, GDScript snake_case, Python PEP8.
- Singleton yerine sinyal/event tercih et.

## Komutlar
- C# derle:      dotnet build
- Python test:   cd tools && .venv/bin/pytest
- Godot headless: godot --headless --quit

## Dokunma
- raw/ içindeki hiçbir dosya.
- project.godot ve .tscn dosyaları (kullanıcı istemedikçe).
- .godot/, bin/, obj/ (üretilmiş dosyalar).

## Mevcut durum
- Wiki boş, ilk kaynaklar ekleniyor.
- Sıradaki: ilk kaynağı ingest et.
```

### Başlangıç adımları

1. Klasörleri oluştur, `git init` yap, şemayı `CLAUDE.md` olarak kaydet.
2. İlk kaynağı (örneğin bir C# kitap bölümü, markdown'a çevrilmiş halde) `raw/books/` içine koy.
3. Claude Code'u kök klasörde aç ve şunu yaz: `raw/books/.../ch01.md dosyasını ingest et.`
4. Oluşan wiki sayfalarına bak, beğenmediğin yer varsa şemayı güncelle. Şema zamanla senin tarzına göre olgunlaşır.

## 6. Nasıl çalıştırılır

### Claude Code'u kur

Claude Code, terminalde çalışan bir araç. Kurulum komutu zamanla değişebiliyor, güncel komutu **docs.claude.com** adresindeki Claude Code "Setup/Quickstart" sayfasından kopyala. Genelde şunlar gerekir:

- Bir Claude hesabı (Pro/Max aboneliği ya da API erişimi)
- Windows'ta çoğunlukla WSL veya Git Bash, macOS/Linux'ta doğrudan terminal
- Eski npm yöntemi için Node.js

Kurduktan sonra terminalde `claude --version` yazarak çalıştığını kontrol et.

### Proje klasörünü hazırla

```bash
mkdir my-game && cd my-game
git init
mkdir -p raw/books raw/docs raw/articles raw/assets
mkdir -p wiki/sources wiki/concepts wiki/patterns wiki/decisions
mkdir -p scripts/csharp scripts/gdscript scenes tools
```

Sonra `CLAUDE.md` dosyası oluştur ve şemayı yapıştır. `wiki/index.md` ve `wiki/log.md` dosyalarını boş açabilirsin, Claude doldurur. İlk commit'i at:

```bash
git add . && git commit -m "ilk yapı"
```

### İlk kaynağı ekle ve başlat

Bir C# kitabını markdown'a çevir (EPUB için pandoc örneği):

```bash
pandoc kitap.epub -t markdown -o raw/books/csharp-kitap.md
```

Sonra Claude Code'u proje kökünde başlat:

```bash
cd my-game
claude
```

İlk açılışta giriş yapman istenir. Claude, bulunduğun klasördeki `CLAUDE.md` dosyasını otomatik okur. Claude Code'un içinde normal sohbet gibi yazarsın:

```
raw/books/csharp-kitap.md dosyasının ilk bölümünü ingest et.
```

Claude dosyaları okuyup `wiki/` altına sayfalar yazmak için izin ister. Her değişikliği onaylayabilir ya da reddedebilirsin. Sonra örneğin: `Wiki'deki generics sayfasını kullanarak bir Inventory<T> sınıfı yaz.`

### Wiki'yi okumak için (isteğe bağlı)

Obsidian'ı kur, "Open folder as vault" ile `wiki/` klasörünü (ya da tüm proje klasörünü) aç. Claude bir tarafta yazarken sen diğer tarafta sayfaları ve bağlantı grafiğini görürsün. Zorunlu değil, düz markdown dosyalarını herhangi bir editörde de okuyabilirsin.

### Güvenli çalışma alışkanlıkları

- Her işlemden sonra `git commit` yap, Claude bir şeyi bozarsa geri dönebilirsin.
- İlk günlerde Claude'un izin isteklerini tek tek oku, hepsine körü körüne "evet" deme.
- `raw/` klasörünü bozmamasını şema sağlıyor, ama git sana ikinci bir güvence verir.

## 7. Toplu ingest ve kodlamada wiki kullanımı

### "raw/ içindeki tüm kaynakları ingest et" denebilir mi?

Diyebilirsin, çalışır, ama ilk seferde önerilmez.

- Çok kaynak tek seferde bağlamı doldurur, kalite düşer ve Claude ortalarda yüzeysel kalabilir.
- Hatalı bir alışkanlık (kötü sayfa biçimi, yanlış kategori) 30 kaynağa yayılır, düzeltmesi zorlaşır.
- Sayfaları kontrol etme şansın kalmaz.

Önerilen yol:

1. **İlk 1-2 kaynağı tek tek ingest et**, çıkan sayfaları oku, beğenmediğini söyle, gerekirse `CLAUDE.md`'yi düzelt.
2. Düzen oturunca toplu işle:

```
raw/docs/ klasöründeki henüz ingest edilmemiş tüm dosyaları sırayla ingest et.
Her dosyadan sonra log.md'ye yaz. Her 3 dosyada bir dur ve özet ver.
```

"Henüz ingest edilmemiş" ifadesi önemli. Claude `wiki/log.md` ve `wiki/sources/` içine bakıp hangilerinin işlendiğini anlar. Kitaplarda bölüm bölüm git, tek dev dosya verme.

### Kodlama yaparken wiki nasıl kullanılır

Ayrı bir şey yapman gerekmiyor. `CLAUDE.md` her oturumda otomatik okunur ve içindeki kural ("önce index.md'yi oku") sayesinde Claude kod yazmadan önce wiki'ye bakar. Sen normal istek yazarsın:

```
Oyuncu envanteri için C# sınıfı yaz.
```

Claude şunu yapar: `wiki/index.md` oku, ilgili sayfaları aç (generics, collections, signals...), plan sun, kod yaz, hangi sayfaya dayandığını belirt. Yönlendirmek istersen açıkça söyle:

```
wiki/concepts/signals.md ve wiki/patterns/state-machine.md sayfalarına
dayanarak düşman AI'ı yaz. Wiki'de olmayan bir şey kullanırsan
[Kaynak dışı] diye işaretle.
```

Sayfaya doğrudan işaret etmek, Claude'un yanlış sayfa seçme ihtimalini sıfırlar.

### Kodlama sonrası geri besleme

Kodlama sırasında öğrendiklerin ve aldığın kararlar da wiki'ye girsin: `Bu envanter tasarımında aldığımız kararları wiki/decisions/ altına yaz.` Böylece birkaç hafta sonra "neden böyle yaptık?" sorusunun cevabı wiki'de durur.

Wiki büyüdükçe index.md uzar. Birkaç yüz sayfaya kadar sorun olmaz. Sonrasında Claude'a "wiki'yi lint et" de ve arama aracı (qmd gibi) eklemeyi düşün.

## 8. İndeksi bölme

Fikir doğru: index büyüyünce bölmek gerekir. Ama **sayıya göre** (index001, index002) bölmek yerine **konuya göre** bölmek daha iyi.

### Sayıya göre bölmenin sorunu

`index001.md` ile `index002.md`'nin içinde ne olduğu dosya adından anlaşılmaz. Claude "generics" sayfasını ararken hangisine bakacağını bilemez, hepsini okumak zorunda kalır ve bölmenin faydası kalmaz. Ayrıca bir sayfa eklendiğinde hangi dosyaya gireceği de belirsiz olur.

### Kategori bazlı, iki katmanlı yapı

```
wiki/
├── index.md                  # Ana harita: sadece alt indekslere yönlendirir
├── indexes/
│   ├── csharp.md
│   ├── godot.md
│   ├── gdscript.md
│   ├── python.md
│   ├── patterns.md
│   └── decisions.md
```

`index.md` kısa kalır, her alt indeksin ne içerdiğini tek satırda anlatır:

```markdown
# Wiki Ana İndeks
- [[indexes/csharp]]   : C# dili, generics, LINQ, async, delegates (42 sayfa)
- [[indexes/godot]]    : Godot motoru, sahne, node, sinyal sistemi (31 sayfa)
- [[indexes/patterns]] : Oyun ve kod desenleri (18 sayfa)
```

Claude önce ana indeksi okur, konuya uyan alt indekse gider, oradan sayfaya iner. Üç adım ama her adım küçük.

### Eşik sayısı

500 sayfa fazla. Bir indeks satırı yaklaşık 20-30 token tutar, 500 satır 10-15 bin token eder ve her sorguda bunu okumak gereksiz yük olur. Alt indeks başına **100-150 sayfa** makul bir üst sınırdır. Bir kategori bu sınıra gelince alt kategorilere böl (örneğin `csharp.md` → `csharp-async.md`, `csharp-collections.md`).

### Şemaya eklenecek kural

```markdown
## İndeks yapısı
- wiki/index.md yalnızca alt indeksleri listeler (her biri için tek satır özet + sayfa sayısı).
- Sayfa kategorisine göre wiki/indexes/<kategori>.md dosyasına eklenir.
- Bir alt indeks 120 satırı geçerse konuya göre ikiye böl, ana indeksi güncelle.
- Her ingest sonrası hem ilgili alt indeksi hem ana indeksteki sayfa sayısını güncelle.
- Sorguda önce index.md, sonra ilgili alt indeks, sonra sayfa okunur.
```

Bu bölmeyi hemen yapmana gerek yok. İlk 50-100 sayfaya kadar tek `index.md` yeterli. Büyüme başlayınca Claude'a "index.md'yi şemadaki alt indeks yapısına göre böl" demen yeter.

## 9. Kendi kodunu ve mekaniklerini wiki'ye ekleme

Godot'ta yazdığın bir kodu ve mekanik bilgilerini "wiki'ye ekle" dersen Claude ekler. Bunun için kaynağın `raw/` içinde olması gerekmez, Claude kodu zaten projede görebilir. Ama şemada tanımlamazsan her seferinde farklı yere farklı biçimde yazabilir.

### Nasıl söylersin

```
scripts/csharp/Inventory/ altındaki kodu oku ve envanter mekaniğini
wiki'ye ekle: nasıl çalıştığı, aldığımız kararlar, kullandığımız desenler.
```

Ya da mekaniği kendi sözlerinle anlatıp "bunu wiki'ye yaz" diyebilirsin.

### Nereye yazılır

```
wiki/
├── mechanics/     # Bu oyunun mekanikleri (envanter, dövüş, hareket...)
├── patterns/      # Genel desenler (kodundan çıkardıkların dahil)
└── decisions/     # "Neden böyle yaptık" kararları
```

- **mechanics/**: Mekaniğin ne yaptığı, hangi sınıflar ve sahneler ilgili, nasıl kullanılır, bilinen sınırlamalar
- **decisions/**: Neden C# seçildi, neden sinyal kullanıldı gibi gerekçeler
- **patterns/**: Başka yerde de kullanabileceğin genel çözümler

### Şemaya eklenecek bölüm

```markdown
## Kendi kodumuzu ve mekaniklerimizi belgeleme
Kullanıcı "şu mekaniği wiki'ye ekle" dediğinde:
1. İlgili kodu (scripts/, scenes/) ve kullanıcının anlattıklarını oku.
2. wiki/mechanics/<ad>.md sayfası yaz. İçerik: amaç, nasıl çalışır,
   ilgili dosyalar (yol olarak), kullanılan desenler, bilinen sınırlamalar.
3. Frontmatter'daki sources alanına kod dosyalarının yollarını yaz.
4. Alınan tasarım kararlarını wiki/decisions/ altına ayrı sayfa yap.
5. Kodun dayandığı wiki kavram sayfalarına [[bağlantı]] ver.
6. İlgili alt indeksi ve log.md'yi güncelle.
Kod değiştiğinde ilgili mechanics sayfasının güncel olup olmadığını kontrol et.
```

### Dikkat edilecek nokta

Kod değişir, wiki sayfası kendiliğinden değişmez. Mekanik sonradan değişirse sayfa eskir ve eskimiş bilgi, olmayan bilgiden kötüdür. Büyük bir değişiklikten sonra "Inventory mekaniği değişti, wiki sayfasını güncelle" de, periyodik lint sırasında da "mechanics/ sayfalarını güncel koda karşı kontrol et" de. Böylece yeni bir özellik yazarken Claude önce bu sayfaları okuyup mevcut sistemlerle uyumlu kod üretir.

## 10. Token kullanımı

Wiki hem token harcatır hem de uzun vadede tasarruf ettirir. Dengeyi yönetmek senin elinde.

### Token nereye gider

1. **CLAUDE.md**: Her oturumda baştan okunur. Şemayı uzun tutarsan her oturumun başında bu yük kadar token harcanır.
2. **Index okuma**: Her sorguda önce index okunur. Bu yüzden alt indekslere bölmek önemli.
3. **Wiki sayfaları**: Claude ilgili sayfaları açıp okur. Sayfa ne kadar uzunsa o kadar token gider.
4. **Ingest**: En pahalı işlem. Kaynağın tamamı okunur, sonra 10-15 sayfa okunup yeniden yazılır.
5. **Sohbet geçmişi**: Oturum uzadıkça önceki her mesaj bağlamda kalır ve her yeni istekte yeniden işlenir.

### Tasarruf sağlayan taraf

Wiki olmasa her yeni özellikte Claude'a mimariyi, kararları, kitaptaki ilgili bölümü baştan anlatmak ya da ham kaynağı yeniden okutmak zorunda kalırsın. Wiki'de bilgi bir kez derlenir, sonra özet ve kısa sayfalar okunur.

### Token'ı kontrol altında tutma yolları

- **Sayfaları kısa tut**: Şemaya "bir sayfa 1-2 ekranı geçmesin, uzarsa böl" kuralı ekle.
- **Alt indeks yapısı**: Wiki'yi konuya göre alt indekslere böl.
- **Tek kaynak, tek bölüm ingest**: Dev dosyaları bölümlere ayır.
- **Odaklı istek ver**: "Tüm wiki'ye bak" yerine "şu iki sayfaya dayanarak yaz" de.
- **Oturumları temiz tut**: Konu değişince yeni oturum aç ya da `/clear` ile geçmişi temizle.
- **Önce küçük dene**: Küçük bir ingest yap, harcamayı gör, sonra büyüt.

### Harcamayı nasıl göreceksin

Claude Code içinde kullanım ve bağlam durumunu gösteren komutlar var (örneğin `/cost` ve `/context` gibi), ama komut adlarını güncel dokümandan kontrol et, sürümden sürüme değişebiliyor. Abonelik (Pro/Max) kullanıyorsan token yerine kullanım limitine takılırsın. API kullanıyorsan doğrudan token başına ödersin.

Pratik başlangıç: ilk bir kitap bölümünü ingest et, harcamanın ne kadar olduğuna bak, ona göre toplu ingest'in sana uygun olup olmadığına karar ver.
