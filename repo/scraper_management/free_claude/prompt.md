# GÖREV
Python ve Tkinter ile bir masaüstü "Scraper Yöneticisi" uygulaması yaz. Uygulama, bir ana klasör altındaki Python scraper dosyalarını bulup kategorili bir listede gösterecek. Seçilen scraper'ları, her biri için tanımlı Python ortamıyla (env) çalıştıracak ve ilerlemeyi gösterecek.

# TEKNOLOJİ VE KURALLAR
- Python 3.10+, Tkinter. Arayüz dili Türkçe.
- Scraper'ları ASLA arayüz iş parçacığında çalıştırma. Her scraper ayrı bir alt süreç (subprocess / QProcess) olarak, kendi env'inin python.exe'siyle çalışsın.
- Tek dosya yerine modüler yapı kullan (aşağıdaki dosya yapısına bak).
- Tüm ayarlar JSON dosyasında tutulsun (settings.json). Uygulama açılışında okunsun, değişince kaydedilsin.
- Kod okunabilir olsun: tip ipuçları (type hints), kısa docstring'ler, sihirli sayı yok.
- Windows öncelikli (yollar için pathlib kullan).

# PENCERE YERLEŞİMİ (yukarıdan aşağıya, bu sırayla)

## 1) Menü çubuğu — 4 sekme
Başlıklar: Dosya / Düzenle / Görünüm / Modüller.
Şu an menülerin İÇİ BOŞ kalsın. Her menü için kodda, ileride doldurulacak ayrı bir fonksiyon ve TODO notu olsun:
- Dosya (sonra eklenecek): Scraper Ekle, Tümünü Seç, Tümünü Çalıştır, Seçilenleri Çalıştır, Ana Klasörü Aç, Log Klasörünü Aç, Ayarlar.
  Ayarlar içeriği (sonra eklenecek, genişletilebilir olsun): scraper ana klasörü, env klasörü, scraper dosya kalıbı (varsayılan *scraper.py), hariç tutulacak klasör ve dosyalar, paralel çalışma sayısı (örn. aynı anda 5), export yolu.
- Düzenle (sonra eklenecek): Scraper Oluştur, Scraper Kontrol.
- Görünüm (sonra eklenecek): Sekmeleri Aç (kategori ağacını tam göster), Sekmeleri Kapat (sadece kategorileri göster).
  Bunun için MainWindow içinde expand_all() ve collapse_all() metotları hazır olsun.
- Modüller (sonra eklenecek): 7z Sıkıştır (py7zr), daha sonra yeni modüller.
  Modüller için plugin benzeri bir yapı düşün: modules/ klasöründeki her modül kendini menüye kaydedebilsin.

## 2) Araç çubuğu (menünün hemen altı)
- "Tümünü Seç" onay kutusu (CheckBox). İşaretlenince FİLTREDE GÖRÜNEN tüm scraper'ları seçer, kaldırılınca hepsinin seçimini kaldırır. Elle yapılan seçimlere göre üç durumlu (kısmi seçim) davranabilir.
- "▶ Seçilenleri Çalıştır" butonu. Seçili scraper yoksa kullanıcıya kısa bir uyarı göster.

## 3) Arama / filtre satırı (araç çubuğunun hemen altı)
- Arama kutusu: placeholder "Scraper ara", yazdıkça anında filtreler (scraper adı ve yolda arar).
- Kategori açılır listesi: "Tüm Kategoriler" + bulunan klasör kategorileri.
- Env açılır listesi: "Tüm Env'ler" + bulunan env'ler.
- "Temizle" butonu: üç filtreyi sıfırlar.
- Filtre sonucunda hiç scraper kalmayan kategoriler gizlensin.

## 4) Ana liste (pencerenin büyük bölümü)
QTreeWidget kullan. Üst düzey öğeler kategori (klasör), alt öğeler scraper'lardır.
- Kategori satırı: seçme kutusu (üç durumlu, otomatik), klasör simgesi, kategori adı ve scraper sayısı. Örn: "E-Ticaret (3)". Kutusu çocukları toplu seçer.
- Scraper satırı sütunları:
  1. Seçme kutusu + Scraper adı (örn. trendyol_scraper.py)
  2. Dosya yolu (KISALTILMIŞ; ortası "…" ile kesilsin, tam yol ipucunda (tooltip) görünsün)
  3. Env (KISALTILMIŞ; tam yol tooltip'te)
  4. Dosya sayısı (scraper'ın bulunduğu klasördeki dosya sayısı, ortalanmış)
- Sütun genişlikleri: ad ve yol esnek, env ve dosya sayısı içeriğe göre.
- Çift tıklama: scraper'ın klasörünü açsın. Sağ tık menüsü: Çalıştır, Klasörü Aç, Log'u Aç, Yolu Kopyala (içerik sonra genişletilebilir).
- Satır durum rengi/simgesi (hazır, çalışıyor, bitti, hata) için bir sütun veya ikon alanı ayır; şimdilik sadece altyapısı olsun.

## 5) Alt durum çubuğu (pencerenin en altı)
- Sol: durum metni. Örn: "Hazır" veya "Çalışıyor: trendyol_scraper.py (1 / 3)".
- Sağ: "Seçili: x / y" sayacı.
- En sağ: ilerleme çubuğu (QProgressBar) ve yüzde.

# TARAMA MANTIĞI
- Ayarlardaki "scraper ana klasörü" altını özyinelemeli tara.
- Dosya kalıbı ayarlardan gelsin (varsayılan *scraper.py).
- Ayarlardaki hariç tutulacak klasör ve dosyaları atla (örn. __pycache__, .git, venv, envs).
- Kategori = scraper'ın bulunduğu ilk üst düzey klasör (ana klasörün hemen altındaki klasör adı).
- Dosya sayısı = scraper dosyasının bulunduğu klasördeki dosya sayısı (alt klasörler dahil değil, bunu ayar yapılabilir bırak).
- Env eşleştirme sırası: (1) scraper klasöründe .venv veya venv varsa onu kullan, (2) yoksa ayarlardaki env klasöründe scraper'a/kategoriye eşleşen env, (3) o da yoksa varsayılan env. Hangi env'in bulunduğu listede gösterilsin.
- Tarama arayüzü dondurmasın (QThread veya QRunnable). Büyük klasörlerde durum çubuğunda "Taranıyor…" yazsın.

# ÇALIŞTIRMA MANTIĞI
- "Seçilenleri Çalıştır": seçili scraper'ları kuyruğa al ve en fazla "paralel çalışma sayısı" kadarını aynı anda çalıştır (QThreadPool veya kendi kuyruk yöneticin).
- Her scraper: kendi env'inin python.exe'siyle, çalışma klasörü scraper'ın klasörü olacak şekilde başlatılsın.
- stdout/stderr, log klasörüne scraper_adı_tarih.log olarak yazılsın.
- İlerleme = biten scraper sayısı / toplam. Durum çubuğunda ve ilerleme çubuğunda canlı güncellensin.
- Hata olan scraper listede işaretlensin, diğerleri çalışmaya devam etsin.
- Bir "Durdur" altyapısı hazır olsun (şimdilik arayüzde buton olmasa da fonksiyon olarak).

# AYARLAR (settings.json örnek şema)
{
  "scraper_root": "D:/Scrapers",
  "env_root": "D:/Scrapers/envs",
  "scraper_pattern": "*scraper.py",
  "exclude": ["__pycache__", ".git", "venv", "envs"],
  "max_parallel": 5,
  "export_path": "D:/Scrapers/export",
  "log_path": "D:/Scrapers/logs"
}

# DOSYA YAPISI
scraper_manager/
  main.py                 # uygulamayı başlatır
  settings.json
  core/
    settings.py           # ayarları okur/yazar
    scanner.py            # klasör tarama, kategori/env/dosya sayısı bulma
    runner.py             # kuyruk, paralel çalıştırma, log
    models.py             # ScraperInfo dataclass (name, category, path, env, file_count, status)
  ui/
    main_window.py        # ana pencere, menü, araç çubuğu, durum çubuğu
    filter_bar.py         # arama/filtre satırı
    scraper_tree.py       # kategori ağacı
    settings_dialog.py    # sonra doldurulacak
  modules/
    __init__.py           # modül kayıt altyapısı
    zip7.py               # sonra doldurulacak (py7zr)

# GÖRSEL STİL
- Sade, düz (flat) tasarım; Fusion stili, gereksiz gölge ve süs yok.
- Hem açık hem koyu temada okunaklı olsun.
- Satırlar arası ince ayırıcı çizgiler, kategori satırları hafif farklı arka planla ayrışsın.
- Yazı: sistem yazı tipi, 9–10 pt. Başlıklar ve menüler cümle düzeninde (ilk harf büyük).

# BEKLENEN ÇIKTI
1. Yukarıdaki dosya yapısıyla çalışan, çalıştırılabilir proje.
2. Menüler boş ama altyapısı hazır; araç çubuğu, filtre, liste ve durum çubuğu tamamen çalışır.
3. Taramayı gerçek klasörlerde çalıştıran scanner, çalıştırma için runner.
4. Kısa README: kurulum (pip install Tkinter py7zr), çalıştırma ve ayarlar.
5. Önce kısa bir plan yaz, sonra kodu dosya dosya ver.