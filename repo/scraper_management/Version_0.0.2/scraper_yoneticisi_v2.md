# PROJE: Scraper Yöneticisi — Windows Masaüstü Uygulaması (Derlenebilir Teslim)

> **Doküman türü:** Üretim promptu (.md)
> **Hedef:** Visual Studio 2022 ile açılıp `dotnet build` ile hatasız derlenen, çalışan bir WPF uygulaması üretmek.
> **Sürüm:** v2.0 (geliştirilmiş)

---

## 0. Rol ve teslim biçimi (ZORUNLU)

Sen kıdemli bir **WPF + MVVM + .NET 8** geliştiricisisin. Görevin **açıklama veya taslak anlatmak değil**, doğrudan **Visual Studio 2022 ile açılıp `dotnet build` ile hatasız derlenen** eksiksiz bir proje üretmektir.

**Teslim kuralları (ihlal edilemez):**

- Her dosyayı **tam içerikle** yaz (`// ...` ile kesme, `TODO` bırakma, "benzer şekilde devam et" yasak).
- Tüm dosya yollarını **net başlıkla** belirt: `📄 Views/ScraperTableView.xaml` gibi.
- Her C# dosyasında **gerekli tüm `using`** ifadeleri bulunsun.
- Her XAML dosyasında **tüm xmlns tanımları** ve **kaynak (Resource) referansları** eksiksiz olsun.
- `MainWindow.xaml` içine tüm bileşenleri yığma; **her panel ayrı `UserControl`** olsun.
- Kod içinde **Türkçe arayüz metinleri**, **İngilizce sınıf/değişken adları** kullan.
- Uygulama ilk açılışta **örnek (mock) verilerle** dolu ve etkileşimli çalışsın.
- Gerçek Python çalıştırma ve py7zr işlemleri **arayüz seviyesinde bağlı ama "henüz etkin değil"** mesajı versin (servis katmanı hazır, çağrı `NotImplementedException` yerine bilgilendirici `MessageBox` döndürsün).

**Teslim sonunda zorunlu olarak şunları ver:**

1. `dotnet build` çıktısı (0 hata, 0 uyarı).
2. `dotnet run` sonrası **1920×1080 ve 1200×700** iki ekran görüntüsü tarifi (hangi panel nerede).
3. **Kontrol listesi tablosu** (bkz. §12) her madde ✅/❌ ile işaretli.
4. **Bilinen sınırlamalar** başlığı altında bu sürümde kapsam dışı bırakılanlar.

---

## 1. Görev ve hedef

Python tabanlı scraper dosyalarını merkezi olarak yönetmek için **Scraper Yöneticisi** adlı bir Windows masaüstü uygulaması oluştur.

- C# yalnızca **yönetim arayüzü ve kontrol katmanıdır**; Python dosyalarını C#'a çevirme.
- İlk sürüm: **tam işlevsel UI + örnek veri + tüm etkileşimler + derlenebilirlik**.
- Gerçek scraper çalıştırma, py7zr entegrasyonu → **sonraki aşama**, ancak servis arayüzleri **hazır ve DI'a kayıtlı** olacak.

---

## 2. Teknoloji ve kısıtlar

| Alan | Zorunlu seçim |
|------|---------------|
| Dil | C# 12 |
| UI | WPF (XAML) |
| Runtime | .NET 8 (`net8.0-windows`) |
| Mimari | **MVVM** (CommunityToolkit.Mvvm 8.x) |
| DI | `Microsoft.Extensions.DependencyInjection` |
| Ayarlar | JSON (`%AppData%\ScraperYonetici\settings.json`), `System.Text.Json` |
| Veri | In-memory mock servis (JSON seed dosyası `Resources/mock-scrapers.json`) |
| Paket yönetimi | NuGet — tüm paketler **açıkça listelensin** |
| Proje dosyası | `.csproj` tam içerikle |
| Çözüm | `.sln` tam içerikle |

**Yasaklar:** WinForms, WebView2, 3. parti UI kütüphanesi (MaterialDesign, MahApps, Fluent), harici görsel/ikon URL'i, gradient, blur, gölge, animasyon.

İkonlar için **Segoe MDL2 Assets** (sistem fontu) kullanılacak — `Glyph` özelliğiyle `TextBlock`.

---

## 3. Görsel tasarım (kesin)

- Pencere: **1920×1080** için optimize, min **1200×700**, yeniden boyutlandırılabilir.
- Tema: **koyu lacivert/mavi**, kompakt masaüstü paneli görünümü.
- Yazı tipi: **Segoe UI**, normal 12–13 px, başlık 12 px.
- Köşe yuvarlama: en fazla **2 px** (kareye yakın).
- Bölme çizgileri: 1 px, renk `#24415F`.

### 3.1 Renk paleti

XAML `SolidColorBrush` olarak `Themes/Colors.xaml` içinde tanımlanacak:

```
ArkaPlan            #081321
Panel               #0C1929
PanelIkincil        #102137
TabloBaslik         #172B42
Kenarlik            #24415F
MetinAna            #DCE7F5
MetinIkincil        #91A7C1
VurguMavi           #2585E8
CalistirmaYesil     #00A875
HataKirmizi         #C73545
UyariTuruncu        #E5A13B
```

Tüm renkler **`DynamicResource`** ile bağlanacak (hard-coded `#hex` XAML içinde kullanılmayacak).

---

## 4. Ana pencere yerleşimi (kesin yapı)

`MainWindow.xaml` yalnızca **5 satırlı Grid + bileşen barındırıcısı** olacak. Her bölüm ayrı `UserControl`'dür:

```
Row 0: MenüBarView         → 34 px   (MenuBarView.xaml)
Row 1: TopluIslemView      → 52 px   (TopluIslemView.xaml)
Row 2: AramaFiltreView     → 60 px   (AramaFiltreView.xaml)
Row 3: AnaIcerik           → *       (Grid: 2 sütun + GridSplitter)
Row 4: AltDurumAlani       → 195 px  (Grid: 3 sütun)
Row 5: StatusBarView       → 30 px   (StatusBarView.xaml)
```

- `GridSplitter` sütun genişlikleri: sol panel **min 220, max 500, varsayılan 320**.
- Alt durum alanı yüzdeleri: **%18 / %42 / %40**, `GridSplitter` yok (sabit oran).
- Pencere yeniden boyutlandığında **hiçbir panel taşmaz**, minimum boyutta dahi scrollbar ile erişilebilir.

### 4.1 MenüBarView (Row 0)

- Sol: 📦 ikon + **"Scraper Yöneticisi"** başlığı (13 px SemiBold, `MetinAna`).
- Menüler: **Dosya · Düzenle · Görünüm · Modüller**.
- Sağ: minimum/orta/kapat butonları (koyu tema, 34 px yüksekliğe uygun).
- Menü stili: hover `#172B42`, seçili `#2585E8` alt çizgi, klavye erişimi (`_D` gibi accelerator).

**Menü içerikleri:**

| Menü | Öğeler |
|------|--------|
| Dosya | Scraper Ekle · Tümünü Seç · Tümünü Çalıştır · Seçilenleri Çalıştır · **—** · Ana Klasörü Aç · Log Klasörünü Aç · **—** · Ayarlar · **—** · Çıkış |
| Düzenle | Scraper Oluştur · Scraper Kontrol |
| Görünüm | Sekmeleri Aç · Sekmeleri Kapat · **—** · Kolonları Sıfırla |
| Modüller | 7z Sıkıştır · **—** · (Yakında: Toplu Export) |

### 4.2 TopluIslemView (Row 1)

Soldan sağa:

1. `☐ Tümünü Seç` CheckBox — tablodaki seçimlerle **iki yönlü senkron**.
2. **`▶ Seçilenleri Çalıştır`** — yeşil (`#00A875`), belirgin ama büyük değil (yükseklik 32 px).
3. Sağ hizalı sayaç: `Toplam: 24  ·  Seçili: 3` (`MetinIkincil`).

Davranış: hiçbir scraper seçili değilken buton **disabled** ve tooltip "Önce scraper seçin".

### 4.3 AramaFiltreView (Row 2)

Soldan sağa tek satır:

| Bileşen | Genişlik | Davranış |
|---------|----------|----------|
| Arama kutusu | `*` (min 280) | Placeholder: **"Scraper adı, kategori veya dosya yolu ara…"**; debounce 250 ms |
| Kategori ComboBox | 180 | "Tüm Kategoriler" + gruplar |
| Durum ComboBox | 150 | Tümü · Beklemede · Çalışıyor · Tamamlandı · Hata · Durduruldu |
| Env ComboBox | 150 | Tümü + benzersiz env listesi |
| `✕ Filtreleri Temizle` | 130 | Tüm filtreleri sıfırlar |

Filtreler **birlikte (AND)** çalışır; sonuç **anında** tabloya yansır.

### 4.4 Sol Kategori Ağacı (`KategoriAgaciView`)

- Kök satır: 📁 **Tüm Kategoriler** (yanında toplam sayı).
- `TreeView` hiyerarşi: `Kategori → AltKategori → Scraper adları`.
- Sayı etiketleri: `E-Ticaret (5)` biçiminde.
- Genişletme oku, girinti, **ince hiyerarşi çizgisi** (1 px `Kenarlik`).
- Seçili öğe: **arka plan `#2585E8`**, metin beyaz.
- Kategori tıklanınca sağ tablo **filtrelenir**.
- **Sekmeleri Aç:** tüm düğümler `IsExpanded=true`.
- **Sekmeleri Kapat:** yalnızca kök kategoriler; alt kategoriler `IsExpanded=false`.
- Ağaç her zaman bağımsız `UserControl` olarak ana içerik Grid'inin sol sütununda.

### 4.5 Sağ Scraper Tablosu (`ScraperTableView`)

`DataGrid` + `CollectionViewSource` gruplandırma. **Kolonlar:**

| # | Kolon | Genişlik | Not |
|---|-------|----------|-----|
| 1 | ☐ (checkbox) | 34 | Header'da tümünü seç |
| 2 | İkon | 30 | 🐍 glyph |
| 3 | Scraper Adı | 200 | |
| 4 | Kategori | 130 | |
| 5 | Dosya Yolu | `*` | Kısaltılmış + tooltip tam yol |
| 6 | Env (Python) | 120 | Örn `venv\py311` |
| 7 | Dosya Sayısı | 90 | Sağ hizalı |
| 8 | Durum | 110 | Renkli capsule etiket |
| 9 | İlerleme | 150 | Yüzde + `ProgressBar` aynı hücrede |
| 10 | Son Çalışma | 130 | `dd.MM.yyyy HH:mm` veya `-` |

- Satır yüksekliği **36 px**, satır arası çizgi 1 px `#24415F`.
- Grup başlığı: 📁 Kategori adı (N) — arka plan `#172B42`, sticky.
- Kolon sıralama aktif (bazı özel kolonlar hariç: checkbox, ikon, ilerleme).
- Çoklu seçim (`Extended`), Ctrl/Shift destekli.
- Seçim değişince **Çalışma Detayı paneli** güncellenir.

**Durum kapsülü renkleri:**

- Beklemede → arka `#1A2A3F`, metin `#91A7C1`
- Çalışıyor → arka `#00A87520`, metin `#00A875`, sol kenarda 2 px yeşil şerit
- Tamamlandı → metin `#4CD9A0`
- Hata → arka `#C7354520`, metin `#C73545`
- Durduruldu → arka `#E5A13B20`, metin `#E5A13B`

**Örnek veri (seed):** Toplam **24 scraper**, gruplar:

| Kategori | Alt kategoriler | Adet |
|----------|-----------------|------|
| E-Ticaret (8) | Amazon (3), Trendyol (3), Hepsiburada (2) | 8 |
| Haber (6) | Haber Siteleri (4), Bloglar (2) | 6 |
| Sosyal Medya (6) | Twitter (2), Instagram (2), YouTube (2) | 6 |
| Diğer (4) | Forumlar (2), Dizinler (2) | 4 |
| **Toplam** | | **24** |

Dağılım kuralı: ~10 Beklemede · 3 Çalışıyor (%24, %68, %41) · 9 Tamamlandı (%100) · 1 Hata (%62) · 1 Durduruldu (%35). Son çalışma tarihleri son 7 güne dağılmış.

### 4.6 Alt Durum Alanı (Row 4)

Üç panel yan yana, her biri `UserControl`, aralarında 1 px `Kenarlik` ayırıcı:

#### GenelDurumView (18%)

- Başlık "Genel Durum"
- 4 satır: ikon + etiket + sayı
  - 🗂 Toplam: **24**
  - ▶ Çalışan: **3**
  - ⏸ Beklemede: **10**
  - ⚠ Hata: **1**
- Sayılar mock veriyle **canlı senkron** (filtre uygulanınca değişmesin; toplam sabit).

#### CalismaDetayView (42%)

- Seçili scraper: ad, tam dosya yolu, env, kategori, son çalışma.
- Büyük `ProgressBar` + yüzde metni.
- "İşlem Açıklaması" alanı: mock (`Dosyalar taranıyor…`, `Ayrıştırma yapılıyor…`, vb.).
- Seçim yoksa: **"Detayları görmek için bir scraper seçin."** (metin ortalı, `MetinIkincil`).

#### LogView (40%)

- Başlık "Log"
- `RichTextBox` veya `ItemsControl`+`ScrollViewer`; **monospace** (`Cascadia Mono, Consolas`).
- Format: `[HH:mm:ss] [SEVİYE] mesaj`
- Renkler: INFO `#91A7C1`, WARN `#E5A13B`, ERROR `#C73545`, OK `#00A875`.
- Auto-scroll (yeni satırda).
- Başlangıçta **6–8 örnek satır** (gerçek işlem logu taklidi yapma, "örnek" ibaresi görünsün).
- Sağ üstte `🗑 Temizle` butonu.

### 4.7 StatusBarView (Row 5)

Sol: 🐍 **Python 3.11.7** · ⚙ **.NET 8.0.x**
Sağ: 📁 `C:\Scrapers` · 🧪 `venv\py311` · 💾 `C:\Exports` · ⚙ (Ayarlar ikonu → aynı komut)

Uzun yollar **orta kısımdan `…` ile kısaltılır**, tooltip'te tam yol.

---

## 5. Ayarlar penceresi (`Views/SettingsWindow.xaml`)

Ayrı `Window`, modal, 620×620.

**Alanlar (her biri etiket + açıklama + textbox + Gözat):**

| Alan | Varsayılan | Açıklama satırı |
|------|------------|-----------------|
| Scraper ana klasörü | `C:\Scrapers` | Tüm scraper'ların kök dizini |
| Python/Env klasörü | `C:\Scrapers\venv\py311` | Varsayılan Python ortamı |
| Scraper kalıbı | `*_scraper.py` | Dosya eşleşme deseni |
| Harici klasörler | (boş) | `;` ile ayrılmış ek yollar |
| Harici dosyalar | (boş) | `;` ile ayrılmış ek dosyalar |
| Paralel çalışma | `5` | Aynı anda çalışacak scraper sayısı (1–32) |
| Export yolu | `C:\Exports` | Çıktıların yazılacağı dizin |
| Log klasörü | `C:\Scrapers\logs` | Log dosyalarının konumu |

- Paralel alan **`NumericUpDown` benzeri**: `TextBox` + doğrulama (`int`, 1–32).
- Alt: **`Kaydet`** (yeşil) · **`İptal`** (gri).
- Kaydet → `SettingsService.Save()` → JSON → toast `"Ayarlar kaydedildi"` (log paneline de INFO olarak düşer).
- Var olmayan klasör → **kırmızı doğrulama metni** ama **kayıt engellenmez** (kullanıcı uyarılır).
- Uygulama açılışında `SettingsService.Load()`; dosya yoksa varsayılanlarla oluştur.

---

## 6. Menü komutları — davranış matrisi

| Komut | İlk sürümde davranış |
|-------|----------------------|
| Scraper Ekle | `AddScraperWindow` açılır: dosya/klasör seçici + kategori ComboBox + Ekle/İptal. Ekle → tabloya mock satır eklenir |
| Tümünü Seç | Filtrelenmiş tüm satırları seçer, sayaç güncellenir |
| Tümünü Çalıştır | `MessageBox`: "Gerçek çalıştırma bir sonraki sürümde etkinleştirilecek. Şu an simülasyon çalışır." → ardından **simülasyon** (opsiyonel, §9.5) |
| Seçilenleri Çalıştır | Aynı mesaj + seçili sayısını gösterir |
| Ana Klasörü Aç | `Process.Start("explorer.exe", path)` — yol yoksa `MessageBox` hata |
| Log Klasörünü Aç | Aynı; yol yoksa oluşturmayı teklif eder |
| Ayarlar | `SettingsWindow` |
| Scraper Oluştur | `CreateScraperWindow`: ad, kategori, env, dosya adı, şablon (Basic/Requests/Playwright) radio, Önizleme, Oluştur (dosya oluşturmaz, sadece form doğrulaması) |
| Scraper Kontrol | `CheckScraperWindow`: checkbox listesi (Sözdizimi, Import, Env, Kalıp), `Kontrol Et` → sonuç tablosu (mock) |
| Sekmeleri Aç / Kapat | §4.4 |
| 7z Sıkıştır | `SevenZipWindow`: kaynak, hedef, arşiv adı, seviye (0–9), `Başlat`/`İptal`, ilerleme. Başlat → "py7zr entegrasyonu bir sonraki sürümde" mesajı |
| Kolonları Sıfırla | `DataGrid` kolon genişliklerini varsayılana döndürür |

---

## 7. Veri modelleri (`Models/`)

```csharp
ScraperItem
  Guid Id
  string Name
  string Category
  string SubCategory
  string FullPath
  string ShortPath          // hesaplanmış
  string EnvName            // "venv\py311"
  string EnvFullPath
  int    FileCount
  ScraperStatus Status      // enum
  int    Progress           // 0-100
  string CurrentStep        // "Dosyalar taranıyor…"
  DateTime? LastRun
  bool   IsSelected

ScraperStatus { Beklemede, Calisiyor, Tamamlandi, Hata, Durduruldu }

AppSettings
  string ScraperRoot
  string EnvRoot
  string ScraperPattern
  string ExternalFolders
  string ExternalFiles
  int    ParallelLimit
  string ExportPath
  string LogFolder
```

`ShortPath` hesaplaması: >60 karakter ise `C:\…\son\iki\klasör\dosya.py`. Tüm `INotifyPropertyChanged` `CommunityToolkit.Mvvm` `[ObservableProperty]` ile.

---

## 8. Servis katmanı (`Services/`)

Her servis **arayüz + implementasyon** olarak yazılacak; implementasyonlar ilk sürümde mock veri döndürür veya `MessageBox`/log bilgilendirmesi yapar.

```csharp
IScraperDiscoveryService
  Task<IReadOnlyList<ScraperItem>> DiscoverAsync(AppSettings s, CancellationToken ct);

IScraperExecutionService
  Task RunAsync(ScraperItem item, CancellationToken ct);   // mock: 2 sn gecikme + simülasyon
  void Cancel(ScraperItem item);

IPythonEnvironmentService
  IReadOnlyList<string> ListEnvironments(string envRoot);
  string ResolvePythonExe(string envName);

ISettingsService
  AppSettings Load();
  void Save(AppSettings s);

ILogService
  void Info(string msg); void Warn(string msg); void Error(string msg);
  event EventHandler<LogEntry> EntryAdded;

IExportService
  Task ExportAsync(IEnumerable<ScraperItem> items, string targetPath, CancellationToken ct);

IArchiveService
  Task CompressAsync(string source, string target, int level, IProgress<int> p, CancellationToken ct);
```

**`ScraperExecutionService` ilk sürüm uyarlaması:**

- `RunAsync` → item.Status = Calisiyor, `IProgress<int>` ile 0→100 arası **deterministik** (rastgele değil) adımlarla 8 sn'de tamamlanır. İptal → Status = Durduruldu.
- Gerçek Python çağrısı için **yorum satırında değil**, `#region Future: Python Execution` bloğunda `ProcessStartInfo` iskeleti verilsin (derlenmeyecek şekilde `#if false` ile sarılı veya `NotImplementedException` fırlatmayacak şekilde `//` yorum bloğunda **tam kod**).

---

## 9. ViewModel katmanı (`ViewModels/`)

- `MainViewModel` — tüm koleksiyonlar, filtrelenmiş `ICollectionView`, seçim yönetimi, toplu komutlar.
- `SettingsViewModel` — ayarlar yükle/kaydet, doğrulama.
- `AddScraperViewModel`, `CreateScraperViewModel`, `CheckScraperViewModel`, `SevenZipViewModel`.
- `GenelDurumViewModel`, `CalismaDetayViewModel`, `LogViewModel`, `StatusBarViewModel` (bunlar `MainViewModel` içinde property olarak tutulur, ayrı örnek gerekmez ama ayrı sınıf).

`[RelayCommand]` ve `[ObservableProperty]` kullan (CommunityToolkit.Mvvm).

---

## 10. Proje yapısı — dosya listesi (bu dosyaların **tamamını** üret)

```
ScraperYonetici.sln
ScraperYonetici/
├── ScraperYonetici.csproj
├── App.xaml  /  App.xaml.cs                (DI container burada)
├── MainWindow.xaml  /  .xaml.cs
├── Views/
│   ├── MenuBarView.xaml  /  .xaml.cs
│   ├── TopluIslemView.xaml  /  .xaml.cs
│   ├── AramaFiltreView.xaml  /  .xaml.cs
│   ├── KategoriAgaciView.xaml  /  .xaml.cs
│   ├── ScraperTableView.xaml  /  .xaml.cs
│   ├── GenelDurumView.xaml  /  .xaml.cs
│   ├── CalismaDetayView.xaml  /  .xaml.cs
│   ├── LogView.xaml  /  .xaml.cs
│   ├── StatusBarView.xaml  /  .xaml.cs
│   ├── SettingsWindow.xaml  /  .xaml.cs
│   ├── AddScraperWindow.xaml  /  .xaml.cs
│   ├── CreateScraperWindow.xaml  /  .xaml.cs
│   ├── CheckScraperWindow.xaml  /  .xaml.cs
│   └── SevenZipWindow.xaml  /  .xaml.cs
├── ViewModels/                              (10 sınıf)
├── Models/                                  (ScraperItem, ScraperStatus, AppSettings, LogEntry)
├── Services/                                (7 arayüz + 7 implementasyon)
├── Commands/                                (RelayCommand zaten toolkit; ekstra varsa)
├── Converters/                              (StatusToBrush, PathShortener, NullToVisibility, ProgressToText)
├── Resources/
│   └── mock-scrapers.json
├── Themes/
│   ├── Colors.xaml
│   ├── Typography.xaml
│   ├── Controls.xaml     (Button, TextBox, ComboBox, DataGrid, TreeView, CheckBox)
│   └── DataGrid.xaml
└── Configuration/
    └── appsettings.example.json
```

---

## 11. Derleme ve çalışma doğrulaması

Projeyi ürettikten sonra **kendi kendine şu adımları doğrula ve raporla**:

1. `dotnet restore` — başarılı mı?
2. `dotnet build -c Release` — **0 hata**, uyarı sayısı?
3. `dotnet run` — pencere açılıyor mu?
4. Filtreler mock veriyle gerçekten süzüyor mu?
5. Kategori tıklaması tabloyu güncelliyor mu?
6. Tümünü Seç → sayaç + checkbox senkron mu?
7. Ayarlar kaydedilip yeniden açılışta yükleniyor mu?
8. Min 1200×700'de tüm paneller görünür mü (scroll ile)?
9. Sekmeleri Aç/Kapat ağacı doğru değiştiriyor mu?
10. 7z ve Scraper Ekle/Oluştur/Kontrol pencereleri açılıyor mu?

---

## 12. Tamamlanma ölçütleri (kontrol tablosu teslim edilecek)

| # | Ölçüt | Durum |
|---|-------|:-----:|
| 1 | Tüm dosyalar oluşturuldu (yukarıdaki ağaç eksiksiz) | |
| 2 | XAML ve C# tam içerikli (kesme yok) | |
| 3 | `dotnet build` 0 hata | |
| 4 | Uygulama açılışta mock veri ile dolu | |
| 5 | 1920×1080 görünüm bozulmuyor | |
| 6 | 1200×700 minimumda kullanılabilir | |
| 7 | Arama + 3 filtre birlikte çalışıyor | |
| 8 | Kategori seçimi tabloyu filtreliyor | |
| 9 | Tümünü Seç / çoklu seçim senkron | |
| 10 | Ayarlar JSON'a yazılıp geri yükleniyor | |
| 11 | 5 ana bölüm + 3 alt panel doğru konumda | |
| 12 | Menüler ve tüm dialog pencereleri açılıyor | |
| 13 | Durum/İlerleme kapsülleri doğru renkte | |
| 14 | Tooltip tam yolları gösteriyor | |
| 15 | StatusBar Python + .NET + yolları gösteriyor | |

---

## 13. Son not

Bu promptun amacı **çalışan bir WPF uygulaması üretmek**tir. "Şöyle olabilir", "benzer şekilde devam edilir", "..." gibi ifadeler kullanma. Eksik ürettiğin her dosya teslimatı geçersiz sayar. Cevabının **sonunda §12 kontrol tablosunu doldur** ve **bilinen sınırlamalar**ı listele.

---

## 14. Yapılan iyileştirmeler (gerekçeli)

| # | İyileştirme | Neden |
|---|-------------|-------|
| 1 | **§0 Rol + teslim zorunlulukları** | Modelin "tam dosya" üretmesini garantiler. |
| 2 | **Kesme/`...`/`TODO` yasağı** | En sık kalite kaybı; açıkça yasaklandı. |
| 3 | **Sürüm sabitleme** (`net8.0-windows`, CT.Mvvm 8.x) | "veya güncel sürüm" belirsizliği kaldırıldı. |
| 4 | **Yasak teknoloji listesi** | Dağınık kısıtlar tek yerde. |
| 5 | **Renk paleti `DynamicResource` zorunlu** | Tema tutarlılığı; hard-coded hex yasağı. |
| 6 | **Her panel ayrı `UserControl`** | "Devasa MainWindow" riskini ortadan kaldırır. |
| 7 | **Dosya ağacı tam listelendi** | Modelin dosya atlamasını engeller. |
| 8 | **Davranış matrisi (§6)** | Her menü öğesinin ilk sürüm davranışı kesinleşti. |
| 9 | **Mock veri dağılımı sayısallaştırıldı** | Tutarlılık denetlenebilir hale geldi. |
| 10 | **Servis imzaları** verildi | Model uydurmaz, gerçek imza yazar. |
| 11 | **`#region Future`** kuralı | Gelecekteki Python iskeleti bugünden görünür. |
| 12 | **`ShortPath` algoritması** tanımlandı | "Uzun yollar kısaltılsın" belirsizdi. |