# PROJE: Scraper Yöneticisi — Windows Masaüstü Uygulaması

## 1. Görev ve hedef

C# ile geliştirilen, Python tabanlı scraper dosyalarını merkezi olarak yönetmek için kullanılacak profesyonel bir Windows masaüstü uygulaması oluştur.

Uygulamanın adı **Scraper Yöneticisi** olsun.

Herhangi bir referans görseli bulunmuyor. Bu nedenle aşağıda belirtilen yerleşimi, boyutları, renkleri ve bileşenleri esas alarak arayüzü kendin oluştur. Tasarım kararlarını bu teknik tanıma göre ver; farklı bir tasarım konseptine geçme.

İlk aşamada arayüz, örnek veriler ve temel UI etkileşimleri geliştirilecek. Gerçek scraper çalıştırma ve sıkıştırma işlevleri sonraki aşamalarda eklenebilecek şekilde mimari hazırlanacak.

## 2. Teknoloji

- C#
- WPF
- .NET 8 veya desteklenen daha güncel bir .NET sürümü
- MVVM mimarisi
- XAML tabanlı arayüz
- JSON tabanlı kullanıcı ayarları
- Python scraper'ları ayrı işlemler olarak çalıştırmaya uygun servis mimarisi

Scraper dosyaları Python ile yazılmıştır. Bunları C#'a dönüştürme. C# yalnızca yönetim arayüzünü ve kontrol mekanizmasını sağlayacaktır.

Projeyi Visual Studio ile açılabilir ve derlenebilir şekilde oluştur.

## 3. Genel görsel tasarım

1920×1080 çözünürlükte iyi görünen, yeniden boyutlandırılabilir bir masaüstü penceresi oluştur.

Minimum pencere boyutu yaklaşık 1200×700 olsun.

Tasarım karakteri:

- Koyu lacivert ve mavi tonları.
- Kompakt ve bilgi yoğun masaüstü arayüzü.
- İnce mavi sınırlar.
- Küçük, okunaklı yazılar.
- Kareye yakın köşeler, çok hafif yuvarlatma.
- Yeşil çalıştırma butonları.
- Yeşil çalışma göstergeleri.
- Kırmızı hata göstergeleri.
- Sarı veya turuncu uyarılar.
- Gri-mavi bekleme durumları.
- Basit ve tutarlı ikonlar.

Önerilen renk paleti:

- Ana pencere: #081321
- Panel: #0C1929
- İkincil panel: #102137
- Tablo başlığı: #172B42
- Kenarlık: #24415F
- Ana metin: #DCE7F5
- İkincil metin: #91A7C1
- Vurgu mavisi: #2585E8
- Çalıştırma yeşili: #00A875
- Hata kırmızısı: #C73545
- Uyarı turuncusu: #E5A13B

Yazı tipi Segoe UI olsun. Normal metin boyutu yaklaşık 12–13 px, tablo başlıkları yaklaşık 12 px olsun.

Aşırı büyük başlıklar, büyük kartlar, gereksiz boşluklar, parlak gradientler, cam efekti veya web sitesi görünümü kullanma. Bu uygulama bir Windows masaüstü kontrol paneli gibi görünmelidir.

## 4. Ana pencerenin kesin yerleşimi

Ana pencereyi dikey olarak beş ana bölüme ayır:

1. Üst menü çubuğu.
2. Toplu işlem araç çubuğu.
3. Arama ve filtre çubuğu.
4. Ana içerik alanı.
5. Alt durum panelleri ve en alt durum çubuğu.

Yerleşim için WPF Grid ve GridSplitter kullan. Ana pencere yeniden boyutlandırıldığında içerikler taşmamalı ve paneller üst üste binmemelidir.

### Bölüm 1: Üst menü çubuğu

Pencerenin en üstünde yaklaşık 34 px yüksekliğinde bir menü çubuğu oluştur.

Sol tarafta uygulama ikonu ve “Scraper Yöneticisi” başlığı yer alsın.

Menü öğeleri sırasıyla:

- Dosya
- Düzenle
- Görünüm
- Modüller

Windows pencere kontrol düğmeleri sağ üstte bulunsun.

**Dosya menüsü:**

- Scraper Ekle
- Tümünü Seç
- Tümünü Çalıştır
- Seçilenleri Çalıştır
- Ana Klasörü Aç
- Log Klasörünü Aç
- Ayarlar

**Düzenle menüsü:**

- Scraper Oluştur
- Scraper Kontrol

**Görünüm menüsü:**

- Sekmeleri Aç
- Sekmeleri Kapat

**Modüller menüsü:**

- 7z Sıkıştır

Menüler Windows masaüstü uygulaması tarzında açılsın. Hover, seçili öğe ve klavye erişimi durumları bulunsun.

### Bölüm 2: Toplu işlem araç çubuğu

Menünün hemen altında yaklaşık 48–54 px yüksekliğinde bir araç çubuğu oluştur.

Sol tarafta:

- Tümünü Seç checkbox'ı.
- Belirgin yeşil “▶ Seçilenleri Çalıştır” butonu.

Bu araç çubuğu ile tablodaki seçimler senkronize çalışmalıdır.

Gereksiz büyük butonlar kullanma.

### Bölüm 3: Arama ve filtre çubuğu

Toplu işlem araç çubuğunun altında yaklaşık 58–64 px yüksekliğinde bir satır oluştur.

Soldan sağa:

1. Geniş arama kutusu.
2. Kategori açılır listesi.
3. Durum açılır listesi.
4. Env açılır listesi.
5. Filtreleri Temizle butonu.

Arama kutusunun placeholder metni:

“Scraper adı, kategori veya dosya yolu ara…”

Arama ve filtreler örnek verilerle gerçekten çalışsın. Filtreler birbirleriyle birlikte kullanılabilsin.

## 5. Ana içerik alanı

Ana içerik alanını yatay olarak ikiye böl.

- Sol kategori paneli: yaklaşık 320 px.
- Sağ scraper tablosu: kalan alanın tamamı.

Sol panel kullanıcı tarafından GridSplitter ile yeniden boyutlandırılabilsin.

### 5.1. Sol kategori paneli

Üstte klasör ikonu ile “Tüm Kategoriler” satırı bulunsun.

Altında ağaç yapısında kategoriler yer alsın.

Örnek yapı:

E-Ticaret
- Amazon
- Trendyol
- Hepsiburada

Haber
- Haber Siteleri
- Bloglar

Sosyal Medya
- Twitter
- Instagram
- YouTube

Diğer
- Forumlar
- Dizinler

Kategori adlarının yanında ilgili gruptaki scraper sayısı gösterilsin.

Örnek:

- E-Ticaret (5)
- Amazon (2)
- Haber (4)
- Sosyal Medya (3)
- Diğer (2)

Ağaç öğelerinde küçük klasör ikonları, genişletme okları, girintiler ve ince hiyerarşi çizgileri kullan.

Seçili kategori mavi bir arka planla vurgulansın.

Bir kategoriye tıklanınca sağ tablodaki scraper listesi filtrelensin.

**Sekmeleri Aç:** Alt kategorileri ve scraper dosyalarını ağaçta genişlet.

**Sekmeleri Kapat:** Alt kategorileri gizle, yalnızca ana kategorileri göster.

Kategori ağacı ana içerik alanında bağımsız bir panel olmalıdır.

### 5.2. Sağ scraper tablosu

Bu bölüm ekranın en geniş kısmını kaplamalıdır.

WPF DataGrid veya eşdeğer, gruplandırma ve seçim desteği bulunan bir bileşen kullan.

Tablo başlıkları:

1. Checkbox
2. İkon
3. Scraper Adı
4. Kategori
5. Dosya Yolu
6. Env (Python)
7. Dosya Sayısı
8. Durum
9. İlerleme
10. Son Çalışma

Tablo satırları kompakt olsun. Yaklaşık 35–38 px satır yüksekliği kullan.

Tablo başlıkları koyu mavi, gövde koyu lacivert olsun. Satırlar arasında ince mavi çizgiler kullan.

Scraper'ları kategori grupları altında göster. Grup başlığında klasör ikonu, kategori adı ve toplam scraper sayısı yer alsın.

Örnek:

E-Ticaret (5)
- Amazon Ürün Scraper
- Trendyol Fiyat Scraper
- Hepsiburada Ürün Scraper

Haber (4)
- Haber Siteleri Scraper
- Blog Scraper

Sosyal Medya (3)
- Twitter Veri Scraper
- Instagram User Scraper
- YouTube Kanal Scraper

Diğer (2)
- Forum Scraper
- Dizin Scraper

Örnekler temsili veridir. Toplam sayı ve grup sayıları, kullanılan örnek veri kümesiyle tutarlı olsun.

#### Dosya yolu

Dosya yolları Windows biçiminde olsun.

Örnek:

`C:\Scrapers\E-Ticaret\Amazon\amazon_scraper.py`

Uzun yollar tabloda kısaltılarak gösterilsin. Fareyle üzerine gelindiğinde tam yol tooltip ile görüntülensin.

#### Python ortamı

Örnek:

`venv\py311`

Her scraper için atanmış Python ortamı gösterilsin. İlk sürümde örnek veriler kullanılabilir.

#### Dosya sayısı

Scraper'ın bulunduğu klasördeki toplam dosya sayısını ifade etsin. Bu değer scraper sayısı değildir.

Örnek sayılar:

- Amazon: 12
- Trendyol: 8
- Hepsiburada: 10
- Haber Siteleri: 15
- Blog: 7
- Twitter: 9
- Instagram: 11
- YouTube: 6
- Forum: 5
- Dizin: 3

#### Durum

Durumlar:

- Beklemede
- Çalışıyor
- Tamamlandı
- Hata
- Durduruldu

Durumlar küçük kapsül biçimli etiketlerle gösterilsin.

Beklemede gri-mavi, Çalışıyor yeşil, Hata kırmızı, Durduruldu turuncu olsun.

#### İlerleme

Yüzde ve yatay progress bar aynı hücrede bulunsun.

Örnek:

- Beklemede: %0
- Çalışıyor: %24
- Çalışıyor: %68
- Tamamlandı: %100
- Hata: son bilinen değer

İlk sürümde bu veriler temsili olsun. Rastgele ve sürekli değişen ilerleme animasyonları üretme.

#### Son çalışma

Tarih ve saat gösterilsin. Henüz çalıştırılmamış scraper için `-` kullan.

#### Tablo etkileşimleri

- Tekli ve çoklu seçim.
- Tümünü seç.
- Seçimi kaldır.
- Kategoriye göre filtreleme.
- Metinle arama.
- Duruma göre filtreleme.
- Env filtresi.
- Sütun sıralama.
- Seçili scraper detaylarını alt panele yansıtma.

Tablodaki checkbox'lar ve üstteki Tümünü Seç kontrolü birbiriyle tutarlı çalışsın.

## 6. Ayarlar penceresi

Dosya > Ayarlar ile ayrı bir pencere aç.

Aşağıdaki alanları ekle:

- Scraper ana klasörü.
- Python/Env klasörü.
- Scraper kalıbı: varsayılan `*_scraper.py`.
- Harici klasör ve dosyalar.
- Paralel çalışma limiti: varsayılan 5.
- Export yolu.
- Log klasörü.

Klasör ve dosya yolları için Gözat butonları ekle.

Paralel çalışma limiti sayısal alan olsun.

Alt kısımda:

- Kaydet
- İptal

butonları bulunsun.

Ayarları JSON dosyasına kaydet. Uygulama yeniden açıldığında yükle.

İlk açılışta varsayılan değerler kullan. Var olmayan klasörler için hata vermek yerine anlaşılır bir doğrulama uyarısı göster.

Ayarlar ekranında her alan için kısa ve anlaşılır açıklama bulunabilir.

## 7. Alt durum alanı

Ana tablonun altında, ana pencerenin genişliğini kaplayan yaklaşık 180–210 px yüksekliğinde üç panelli bir bölüm oluştur.

Paneller yatay olarak yan yana yerleşsin:

- Genel Durum: %18 genişlik.
- Çalışma Detayı: %42 genişlik.
- Log: %40 genişlik.

Pencere boyutuna göre oranlar esneyebilsin.

### 7.1. Genel Durum paneli

Başlık: “Genel Durum”

Şunları göster:

- Toplam Scraper
- Çalışan
- Beklemede
- Hata

Her satırda küçük bir ikon, açıklama ve sayı yer alsın.

Örnek veriler birbiriyle tutarlı olsun.

### 7.2. Çalışma Detayı paneli

Başlık: “Çalışma Detayı”

Seçili scraper için şu bilgileri göster:

- Scraper adı.
- Genel ilerleme çubuğu.
- İlerleme yüzdesi.
- İşlem açıklaması.
- Dosya adı.
- Python ortamı.
- Kategori.

Seçili scraper değiştiğinde detay paneli güncellensin.

Seçili scraper yoksa “Detayları görmek için bir scraper seçin” mesajı göster.

### 7.3. Log paneli

Başlık: “Log”

Koyu arka planlı, monospace yazı tipi kullanan, kaydırılabilir bir log alanı oluştur.

Örnek:

`[10:37:12] Scraper seçildi.`
`[10:37:15] Hazırlık aşaması.`
`[10:37:28] Örnek işlem günlüğü.`

Log satırlarını zaman damgası ve seviye bilgisiyle göster.

Bilgi, uyarı ve hata satırları farklı renklerle ayırt edilsin.

İlk aşamada loglar örnek veri olarak gösterilebilir. Gerçek işlem yapılmadığı halde gerçek işlem logu üretme.

## 8. En alt durum çubuğu

Pencerenin en altında yaklaşık 30 px yüksekliğinde ince bir durum çubuğu bulunmalı.

Sol tarafta:

- Python ikonu ve Python sürümü.
- C#/.NET sürümü.

Sağ tarafta:

- Ana klasör.
- Aktif Env.
- Export yolu.
- Ayarlar ikonu.

Uzun yollar kısaltılmış biçimde gösterilsin. Tam yol tooltip ile görüntülensin.

Durum çubuğu ana pencere boyunca yatay uzansın.

## 9. Menü komutları ve modüller

### Scraper Ekle

Klasör veya Python dosyası seçmeye uygun bir pencere hazırla.

### Scraper Oluştur

Yeni scraper oluşturmak için ayrı bir dialog veya sayfa hazırla. İlk sürümde form alanları ve temel yerleşim yeterlidir.

### Scraper Kontrol

Scraper dosyalarını doğrulamak için ayrı bir arayüz hazırla. İlk sürümde kontrol seçenekleri gösterilebilir.

### Ana Klasörü Aç ve Log Klasörünü Aç

Ayarlar içinde tanımlı klasörleri açmaya uygun komutlar oluştur. Klasör bulunmuyorsa kullanıcıya hata mesajı göster.

### Tümünü Çalıştır ve Seçilenleri Çalıştır

Komutların UI bağlantısını ve servis arayüzünü oluştur. Gerçek Python çalıştırma işlevi henüz geliştirilmediyse kullanıcıya özelliğin henüz etkinleştirilmediğini bildir.

### 7z Sıkıştır

Ayrı bir pencere oluştur. Şu alanlar bulunsun:

- Kaynak klasör/dosya.
- Hedef arşiv yolu.
- Arşiv adı.
- Sıkıştırma seviyesi.
- İlerleme çubuğu.
- Başlat ve İptal.

Gelecekte Python tarafındaki `py7zr` kütüphanesiyle entegre edilebilecek şekilde tasarla. İlk sürümde gerçek sıkıştırma işlemi zorunlu değildir.

## 10. Python entegrasyonuna hazırlık

Gelecekte gerçek scraper çalıştırma için şu servisleri ayrı sınıflarda tasarla:

- `ScraperDiscoveryService`
- `ScraperExecutionService`
- `PythonEnvironmentService`
- `SettingsService`
- `LogService`
- `ExportService`
- `ArchiveService`

Gerçek çalıştırma aşamasında aşağıdakiler desteklenebilmeli:

- Her scraper için doğru Python yürütülebilir dosyasını seçmek.
- Scraper'ın kendi çalışma dizinini kullanmak.
- Standart çıktı ve hata çıktısını yakalamak.
- İlerleme bilgisini UI'ye iletmek.
- İşlemi iptal etmek.
- Çıkış kodunu kontrol etmek.
- En fazla ayarlardaki sayı kadar scraper'ı eşzamanlı çalıştırmak.
- Uzun işlemler sırasında arayüzün donmasını önlemek.

Bu servisleri ilk aşamada gerçek scraper'ları başlatmaya zorlamadan, ileride uygulanabilir arayüzler olarak tasarla.

## 11. Proje yapısı

Kodları mantıklı dosyalara ayır. Önerilen yapı:

`ScraperYonetici/`
- `App.xaml`
- `MainWindow.xaml`
- `Views/`
- `ViewModels/`
- `Models/`
- `Services/`
- `Commands/`
- `Converters/`
- `Resources/`
- `Themes/`
- `Configuration/`

Ana pencerenin XAML kodunu tek bir devasa dosyada toplama. Kategori paneli, scraper tablosu, durum panelleri ve ayarlar penceresini ayrı bileşenlere ayır.

## 12. Tamamlanma ölçütleri

Projeyi tamamlanmış saymadan önce:

1. Tüm dosyaları oluştur.
2. XAML ve C# kodlarını tamamla.
3. Eksik namespace ve sınıfları düzelt.
4. Uygulamayı derle.
5. Derleme hatalarını gider.
6. Ana pencereyi çalıştır.
7. 1920×1080 çözünürlükte ekran görüntüsü al.
8. Minimum pencere boyutunu test et.
9. Arama ve filtrelerin çalıştığını doğrula.
10. Kategori seçiminin tabloyu güncellediğini doğrula.
11. Tümünü Seç ve çoklu seçimi test et.
12. Ayarların kaydedilip tekrar yüklendiğini test et.
13. Menülerin ve alt panellerin doğru konumlandığını kontrol et.

İlk aşamada öncelik, eksiksiz ve tutarlı bir masaüstü arayüzü ile temel etkileşimlerdir. Gerçek scraper çalıştırma ve py7zr entegrasyonunu sonraki aşamalara bırak.

**Sonuç:** Görsel tasarımını bu metindeki teknik tariften kendin oluştur. Ek referans görseli bekleme, yalnızca taslak anlatmakla yetinme ve mümkünse doğrudan derlenebilir proje dosyalarını üret.