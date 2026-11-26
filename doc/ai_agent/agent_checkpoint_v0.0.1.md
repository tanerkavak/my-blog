# AI Bağımsız Checkpoint Sistemi — Kurulum ve Geliştirme Promptu

Aşağıdaki promptu, projede yerel bir checkpoint ve geri alma sistemi kurmasını
istediğin herhangi bir AI kodlama asistanına verebilirsin. Sistem `.nextcode`
yaklaşımındaki **proje içinde ayrı durum klasörü, oturum bazlı kayıtlar ve
paylaşılan içerik nesneleri** fikrini örnek alır; ancak Git veya başka bir
sürüm kontrol sistemi kullanmaz.

Bu dosya çalıştırılabilir bir betik değil, ayrıntılı bir üretim promptudur.
Köşeli parantezli alanları kullanmadan önce doldur.

---

# 0. Rol

Kıdemli bir yazılım mimarı, dosya sistemi güvenliği, veri bütünlüğü ve test
otomasyonu uzmanı olarak çalış. Amacın; kullanıcının bir projede dosyaların
anlık durumlarını kaydetmesini, geçmişi listelemesini, farkları görmesini ve
seçtiği noktaya güvenle geri dönmesini sağlayan **AI aracından ve Git'ten
bağımsız** bir checkpoint sistemi kurmaktır.

Sistem komut satırından insan tarafından kullanılabilmeli; farklı AI
asistanları da aynı komutları veya kararlı bir yerel API'yi çağırabilmelidir.
Hiçbir AI servisine, bulut hesabına, uzak sunucuya veya internet bağlantısına
ihtiyaç duymamalıdır.

# 1. Parametreler

| Parametre | Varsayılan | Açıklama |
|---|---|---|
| `[PROJE_KOKU]` | `<tam proje yolu>` | Korunacak çalışma dizini |
| `[DURUM_KLASORU]` | `[PROJE_KOKU]/.agent/.checkpoint` | Sistemin bütün yerel verileri |
| `[UYGULAMA_DILI]` | `<projenin mevcut dili>` | Zorunlu değilse yeni dil ekleme |
| `[CLI_ADI]` | `aict` | Kullanıcı ve AI'ların çağıracağı komut |
| `[CALISMA_MODU]` | `inceleme / tasarim / uygulama` | Varsayılan: `inceleme` |
| `[TEST_KOKU]` | `<geçici/scratch dizini>` | Sentetik test projeleri |
| `[DESTEKLENEN_OSLER]` | `<Windows / Linux / macOS>` | Doğrulanacak platformlar |

Parametre eksikse tahminle doldurma. Mevcut proje dili uygunsa onu kullan;
yeni bir çalışma zamanı veya üçüncü taraf bağımlılık eklemeden önce gerekçeyi
belirt. Mümkünse yalnız standart kütüphaneyle çalış.

# 2. Temel ürün tanımı

Kurulacak sistem şu kullanım senaryosunu karşılamalıdır:

1. Kullanıcı projeye sistemi bir kez kurar.
2. Her önemli değişiklikten önce veya sonra `aict checkpoint` çalıştırır.
3. Sistem proje dosyalarının o anki durumunu yerel olarak kaydeder.
4. Kullanıcı `aict list`, `aict show`, `aict diff` ve `aict restore` ile geçmişi
   inceler ve istediği noktaya döner.
5. Geri alma işlemi geçmişi silmez; mevcut durumu koruyan yeni bir güvenlik
   checkpoint'i ve geri yüklemenin sonucunu anlatan yeni bir kayıt üretir.
6. Farklı AI araçları aynı checkpoint geçmişini kullanabilir; hiçbir araca özgü
   dosya adı, ref ad alanı, eklenti veya oturum protokolü zorunlu değildir.

Checkpoint bir **yedekleme hizmeti değildir**. Aynı diskteki yerel çalışma
geçmişini tutar; disk arızasına, silinmeye veya cihaz kaybına karşı ayrı haricî
yedek gerekir.

# 3. Kesin sınırlar

1. Git komutu çağırma, Git kütüphanesi kullanma, `.git` klasörü oluşturma veya
   projenin mevcut Git yapılandırmasına dokunma.
2. Git nesne biçimini, pack/index/ref yapısını, commit modelini veya Git
   komutlarını taklit eden gizli bir bağımlılık kurma.
3. `.nextcode` klasörünü değiştirme. Onu yalnız fikir edinmek için salt okunur
   incele; gerçek üretim verilerini testte kullanma.
4. Checkpoint deposu proje içindeyse taramanın dışında tut. Sistemin kendi
   nesnelerini veya loglarını yeniden checkpoint'leme.
5. Ağ erişimi, uzak depo, kullanıcı hesabı, bulut eşitlemesi ve telemetri ekleme.
6. Kullanıcı onayı olmadan gerçek projede geri yükleme, temizlik veya geçmiş
   silme işlemi yapma.
7. Kullanıcı değişikliklerini geri yükleme sırasında sessizce ezme. Önce mevcut
   durumu koru ve çakışmaları göster.
8. Gerçek checkpoint geçmişinde bozma, prune veya kurtarma testi çalıştırma.
   Bütün tehlikeli testler sentetik kopyalarda yürütülmeli.
9. Yeni bağımlılıkları otomatik kurma. Eksik bağımlılığı ve kurulum komutunu
   bildir; kullanıcının ortamını değiştirme.
10. Test sonucu, checkpoint sayısı, dosya sayısı veya platform desteği uydurma.
11. Proje kapsamı dışında refactor yapma; istenmeyen doküman veya örnek proje
    üretme.
12. Şifreleme, tam yedek veya çok kullanıcılı güvenlik garantisi verme.

# 4. `.nextcode` yaklaşımından alınacak fikirler

Aşağıdaki genel fikirleri al, fakat Git'e özgü dosya biçimlerini alma:

- Proje kökünde ayrı ve görünür bir durum klasörü bulunması
- İşlerin oturum kimliğiyle ilişkilendirilebilmesi
- Aynı içeriğin farklı checkpoint'lerde tekrar saklanmaması
- Her checkpoint'in sıralı ve bağımsız okunabilir bir kayda sahip olması
- Geçmişin proje kodundan ve normal sürüm kontrolünden ayrılması

Bunların yerine kendi dosya formatını, JSON manifestlerini, SHA-256 içerik
adresli nesneleri ve atomik dosya işlemlerini kullan. `.nextcode` içindeki
gerçek Git ref/index/nesne biçimleri yeni sistemin standardı değildir.

# 5. Hedef klasör ve dosya yapısı

Sistem kurulduğunda `[DURUM_KLASORU]` altında aşağıdaki yapıyı oluştur:

```text
.agent/.checkpoint/
├── config.json                 # Şema ve kullanıcı yapılandırması
├── sessions.json               # Oturum kayıtları ve son sıra bilgileri
├── checkpoints/
│   └── <session-id>/
│       └── <sequence>.json     # Tam, bağımsız okunabilir checkpoint manifesti
├── objects/
│   └── <hash[:2]>/
│       └── <hash>              # Dosya içeriği; adı SHA-256 özetidir
├── backups/
│   └── <operation-id>/         # Başarısız işlemde dönüş için geçici güvenlik verisi
├── locks/
│   └── <kilit-adı>.json        # Sahip, PID, oturum ve zaman bilgisi
├── tmp/
│   └── <operation-id>/         # Henüz yayınlanmamış geçici yazımlar
└── logs/
    └── operations.jsonl        # İçerik sızdırmayan işlem günlüğü
```

Bu yapı bir başlangıç standardıdır. Projenin mevcut kuralları farklı adlandırma
gerektiriyorsa kullanıcıya bildir; işlevleri sessizce çıkarma. `sessions.json`
tek doğruluk kaynağı değildir: bozulursa manifestlerden oturum ve sıra bilgisi
yeniden oluşturulabilmelidir.

## 5.1 `config.json`

En az şu alanları sürümlü biçimde tut:

```json
{
  "schema_version": 1,
  "project_root": ".",
  "object_hash": "sha256",
  "exclude": [".agent/.checkpoint/**"],
  "follow_symlinks": false,
  "max_file_bytes": null,
  "retention": {
    "max_checkpoints_per_session": null,
    "max_age_days": null,
    "max_total_bytes": null
  }
}
```

- `project_root` taşınabilirliği korumak için göreli tutulur.
- `null` sınır yok demektir; sınırsız saklamanın disk riskini belgeleyicide yaz.
- Dışlama kalıpları açık ve platformdan bağımsız `/` ayraçlı göreli yol kullanır.
- Mevcut proje ignore dosyaları okunabilir ancak hiçbirinin biçimine bağımlı
  olma; sistemin kendi `exclude` kuralları belirleyicidir.

## 5.2 Checkpoint manifesti

Her checkpoint tek başına okunabilir bir JSON belgesi olmalıdır:

```json
{
  "schema_version": 1,
  "checkpoint_id": "<benzersiz-id>",
  "session_id": "<oturum-id>",
  "sequence": 1,
  "created_at": "<UTC ISO-8601>",
  "parent_id": null,
  "trigger": "manual",
  "message": "<kullanıcı notu>",
  "root_fingerprint": "<kanonik dosya listesinin SHA-256 özeti>",
  "files": [
    {
      "path": "src/ornek.py",
      "type": "file",
      "sha256": "<içerik-özeti>",
      "size": 1234,
      "mode": 420,
      "mtime_ns": 0
    }
  ],
  "summary": {
    "file_count": 1,
    "directory_count": 1,
    "total_bytes": 1234,
    "created": 0,
    "modified": 0,
    "deleted": 0
  }
}
```

Kurallar:

- Yollar UTF-8, göreli ve `/` ayraçlı kanonik biçimde saklanır.
- Manifest dosya listesi yola göre kanonik sıralanır; aynı ağaç aynı
  `root_fingerprint` değerini üretir.
- Dosya içeriği manifeste gömülmez; `sha256` ile nesneye bağlanır.
- Boş dosyalar ve destekleniyorsa boş klasörler açıkça temsil edilir.
- Dosya silme, önceki manifestin kapsamıyla karşılaştırılarak anlaşılır;
  geçmişteki dosya kaydı silinmez.
- `parent_id` yalnız ilişki bilgisidir; manifest okumak için ebeveyn zorunlu
  olmamalıdır.
- Bilinmeyen ileri şema sürümü salt okunur raporlanır; eski uygulamayla
  üzerine yazılmaz.
- Manifestte parola, token veya dosya içeriği tutulmaz. Yol ve metadata'nın da
  hassas olabileceği kullanıcıya belirtilir.

## 5.3 Nesne deposu

- Nesne adı içeriğin SHA-256 özetidir; Git nesne biçimi kullanılmaz.
- Nesne önce `tmp/<operation-id>/` altına yazılır, flush/close tamamlanır,
  boyut ve hash doğrulanır, sonra atomik olarak hedef ada taşınır.
- Aynı hash'e sahip geçerli nesne varsa yeniden yazılmaz.
- Sıfır baytlık içerik de geçerli nesnedir.
- Nesneler varsayılan olarak değişmez kabul edilir; mevcut nesnenin üzerine
  yazılmaz.
- Nesne okunduğunda hash uyuşmazsa işlem durur; bozuk içerik geri yüklenmez.
- Farklı oturumlar aynı nesneleri güvenle paylaşabilir; nesne sahipliği tek
  oturuma bağlı değildir.

# 6. Komut satırı sözleşmesi

Komut adlarını ve davranışlarını kararlı tut. Bütün komutlar projenin herhangi
bir alt dizininden çalışabilmeli veya açık `--root <yol>` parametresi almalıdır.

```text
aict init
aict checkpoint [-m "not"] [--session <id>]
aict list [--session <id>] [--limit N] [--json]
aict status [--json]
aict show <checkpoint-id> [--json]
aict diff <checkpoint-id> [checkpoint-id] [--path <göreli-yol>]
aict restore <checkpoint-id> [--path <göreli-yol>] [--dry-run] [--yes]
aict verify [checkpoint-id] [--json]
aict clean --dry-run [--json]
aict clean --apply --yes
aict sessions
```

Her komut için:

- `init`: Yapıyı oluşturur; mevcut geçerli kurulumu bozmaz. Farklı şema veya
  bozuk yapılandırma varsa üzerine yazmaz.
- `checkpoint`: Tam ağaç manifesti üretir; değişmeyen nesneleri yeniden yazmaz.
  İçerik değişmediyse varsayılan olarak yeni checkpoint üretmez ve mevcut
  checkpoint kimliğini bildirir. Bilinçli boş checkpoint gerekiyorsa ayrı
  `--allow-empty` seçeneği sun.
- `list`: Zaman/sıra düzeninde checkpoint özetlerini gösterir.
- `status`: Son checkpoint'e göre eklenen, değişen ve silinen yolları hesaplar;
  hiçbir dosyayı değiştirmez.
- `show`: Manifest metadata'sını ve dosya listesini gösterir.
- `diff`: İki checkpoint veya checkpoint ile çalışma ağacını karşılaştırır.
  Metin/ikili ayrımı yapar; ikili dosyaları metin gibi yazdırmaz.
- `restore`: Varsayılan olarak dry-run önizlemesi ve onay ister. Tek dosya veya
  tüm proje geri yüklemesini destekler. `--yes` yalnız onayı atlar; güvenlik
  checkpoint'ini ve bütünlük doğrulamasını atlamaz.
- `verify`: Manifest JSON'unu, yol güvenliğini, nesne varlığını, boyutunu ve
  hash'ini denetler.
- `clean`: Önce adayları ve kazanılacak alanı dry-run ile gösterir. `--apply`
  olmadan hiçbir şey silmez; `--yes` olmadan uygulamaz.
- `sessions`: Oturumları, son sırayı ve son checkpoint'i listeler.

Başarı `0`; kullanıcı hatası, bozuk checkpoint, güvenlik ihlali veya başarısız
geri yükleme sıfırdan farklı ve tutarlı çıkış kodu üretir. Makine okunur
`--json` çıktısında log metinleri JSON akışına karışmaz.

# 7. Checkpoint oluşturma algoritması

1. Proje ve durum köklerini kanonikleştir; durum klasörünün proje içinde mi
   dışında mı olduğunu belirle.
2. Yapılandırmayı doğrula. Kapsamı ve dışlama kurallarını uygula.
3. Proje dosyalarını deterministik sırada tara; `.agent/.checkpoint` klasörünü
   kesin olarak atla.
4. Her yol için tür, kanonik göreli yol, boyut ve desteklenen metadata'yı topla.
5. Dosyayı okurken başlangıç/bitiş metadata'sını karşılaştır. İşlem sırasında
   değiştiyse sınırlı sayıda yeniden oku; hâlâ değişiyorsa tutarsız anlık
   görüntü üretme ve açık hata ver.
6. İçeriğin SHA-256 özetini akış hâlinde hesapla; büyük dosyaları gereksiz
   yere belleğe alma.
7. Yeni nesneleri geçici alana yaz, doğrula ve atomik yayınla.
8. Tam manifesti geçici dosyaya yaz ve JSON/şema doğrulaması yap.
9. Oturum sırasını kilit altında ayır. Aynı oturumda sıra çakışmasını önle.
10. Manifesti hedef ada atomik taşı; ardından oturum özetini güncelle.
11. Manifest yayınlanmadan checkpoint başarılı sayılmaz. Hata olursa geçici
    dosyaları temizle; daha önce yayınlanmış checkpoint'lere dokunma.

Sıra kimliği yalnız oturum içinde monoton olur. Farklı oturumlar aynı sayıyı
kullanabilir; gerçek benzersiz kimlik `checkpoint_id` alanıdır. Kısa kimlikle
erişim yalnız tek eşleşme varsa kabul edilir.

# 8. Geri yükleme algoritması

Geri yükleme sistemin en hassas işlemidir:

1. Hedef checkpoint'in ve kullanacağı bütün nesnelerin bütünlüğünü doğrula.
2. Mevcut çalışma ağacının **otomatik güvenlik checkpoint'ini** oluştur.
3. Hedef ile mevcut ağacı karşılaştır; oluşturulacak, değiştirilecek,
   korunacak ve silinecek dosyaları dry-run önizlemesinde listele.
4. Hedef checkpoint'ten sonraki kullanıcı değişikliklerini tespit et ve açıkça
   işaretle. Onay yoksa çakışan dosyaları ezme.
5. Tam proje geri yüklemede hedefte olmayan dosyanın silinmesi yalnız ilgili
   kapsam ve onayla yapılır. Tek dosya geri yüklemede başka hiçbir dosyaya
   dokunma.
6. Güvenlik checkpoint'i oluşturulamadıysa geri yüklemeyi başlatma.
7. Dosyaları aynı dosya sistemindeki geçici alana yaz, hash/boyut doğrula ve
   her dosyayı atomik olarak değiştir. Çok dosyalı işlemin tamamını donanım
   düzeyinde atomikmiş gibi gösterme.
8. İşlem ortasında hata olursa güvenlik kopyasından mümkün olan en güvenli
   dönüşü yap; tamamlanamayan yolları açıkça raporla.
9. Son ağacı hedef manifestle karşılaştır. Bilinçli korunan çakışmalar dışında
   fark varsa işlemi başarılı sayma.
10. Geri yüklemeyi yeni bir checkpoint/operasyon kaydı olarak belgele. Eski
    checkpoint'leri silme veya sıralarını değiştirme.

Geri alma işlemi yeni bir durum oluşturur; kullanıcı güvenlik checkpoint'ine
dönerek geri yüklemeyi de geri alabilir.

# 9. Yol ve platform güvenliği

- `..`, mutlak yol, sürücü değiştirme, UNC kaçışı ve kök dışına çıkan kanonik
  yolları reddet.
- Sembolik bağları varsayılan olarak izleme. Destekleneceklerse bağın kendisini
  ayrı tür olarak sakla ve hedefin proje dışına yazmasını engelle.
- Windows junction/reparse point ve POSIX symlink davranışını ayrı test et.
- Büyük/küçük harf duyarsız sistemlerde aynı hedefe düşen iki yolu sessizce
  ezme; çakışmayı bildir.
- Unicode normalizasyonundan doğan yol çakışmalarını tespit et.
- Desteklenmeyen socket, device, FIFO ve özel dosyaları atlayıp sayısını açıkça
  raporla; normal dosya gibi okuma.
- Çalışma dizinine değil, hesaplanan proje köküne göre işlem yap.
- Kilit dosyasında PID, oturum, başlangıç zamanı ve hostname bulunsun; bayat
  kilit otomatik silinmeden önce sürecin gerçekten yaşamadığı doğrulansın.

# 10. Saklama ve temizlik

- Kullanıcı `clean` istemedikçe checkpoint veya nesne silme.
- Saklama politikalarını önce simüle et: silinecek manifestler, korunanlar,
  artık hiçbir manifestin kullanmadığı nesneler ve kazanılacak bayt.
- Canlı herhangi bir manifestten erişilen nesne silinmez.
- Temizlik öncesi bütün manifestler taranır ve doğrulanır. Okunamayan manifest
  varsa otomatik temizlik durur.
- Kullanıcı tarafından sabitlenen checkpoint varsa `pinned: true` ile korunur;
  otomatik yaş/boyut politikasına kurban edilmez.
- Temizlik de geri dönüşü zor bir işlemdir; varsayılan dry-run ve açık onay
  gerektirir.
- Temizlik sonrası `verify` çalıştırılır; sonuç ve silinen aday sayıları
  raporlanır.

# 11. Hata ve günlük davranışı

- Beklenmeyen hatayı sessizce yutma; hangi aşamada oluştuğunu ve kullanıcının
  verisinin korunup korunmadığını söyle.
- Günlüklerde dosya içeriği, gizli token veya tam manifest dökümü tutma.
- `operations.jsonl` kayıtları zaman, işlem, sonuç, checkpoint kimliği ve hata
  kodu içerebilir.
- Bir nesne yazımı yarım kalırsa canlı nesneye dönüşmez.
- Bozuk oturum özeti, manifestlerden yeniden kurulabilir; bozuk manifest veya
  nesne ise onarılmış gibi gösterilmez.
- Checkpoint alınamayan proje için çıkış kodu başarılı olmaz.

# 12. Test stratejisi

Bütün testleri `[TEST_KOKU]` altındaki sentetik projelerde yürüt. En az şu
senaryoları bağımsız dosya/hash karşılaştırmalarıyla doğrula:

1. `init`, tekrar `init` ve boş proje
2. İlk checkpoint ve içerik değişmeden ikinci deneme
3. Dosya ekleme, değiştirme, silme ve yeniden adlandırma
4. Boş dosya, boş klasör, UTF-8 metin ve ikili dosya
5. Aynı içerikli iki dosyanın ve ardışık checkpoint'lerin nesne paylaşımı
6. Türkçe, Unicode, boşluklu ve uzun dosya yolları
7. `.agent/.checkpoint` ve dışlanan dosyaların manifeste girmemesi
8. Liste, durum, gösterim ve iki yönlü fark çıktıları
9. Tek dosya geri yükleme; diğer dosyaların değişmediğini kanıtlama
10. Tam proje geri yükleme ve silinen dosyanın geri gelmesi
11. Checkpoint sonrası kullanıcı değişikliğinde çakışma ve onaysız ezmeme
12. Geri yükleme öncesi güvenlik checkpoint'iyle geri yüklemeyi geri alma
13. Bozuk JSON, eksik nesne, yanlış hash ve yarım geçici dosya
14. Yol kaçışı, symlink/junction ve büyük/küçük harf çakışması
15. Aynı oturumda eşzamanlı sıra ayırma ve farklı oturumlarda nesne paylaşımı
16. Disk dolması, izin hatası, iptal ve kilitli işlem davranışı
17. Temizlik dry-run'ının hiçbir şey silmemesi; canlı nesnenin korunması
18. Proje klasörünün başka yere taşınmasından sonra geçmişin okunabilmesi
19. Desteklenen her işletim sisteminde kritik akışların çalışması
20. Büyük sentetik projede süre, bellek ve disk kullanımının ölçülmesi

Test, yalnız uyguladığın kodun ürettiği değeri tekrar etmemeli. Geri yükleme
sonrası dosyaları beklenen bağımsız içerikle karşılaştır; manifestteki hash'i
tek başına yeterli kanıt sayma.

# 13. Çalışma sırası

1. Proje talimatlarını ve mevcut kod tabanını oku.
2. `.nextcode` yapısını yalnız ilham almak için salt okunur incele; gerçek
   nesnelerini değiştirme ve yeni sisteme kopyalama.
3. Mevcut dil, paket yöneticisi, başlatıcı ve test düzenini belirle.
4. Dosya formatı, CLI ve güvenlik modelinde belirsiz kalan kullanıcı kararlarını
   listele; kod ve dokümanlardan cevaplanamayanları sor.
5. Uygulama modu kapalıysa tasarımı ve bulguları raporlayarak dur.
6. Uygulama modu açıksa önce sentetik test fixture'ını kur.
7. Şu kontrollü fazlarla ilerle:
   - Faz 1: `init`, yapılandırma, tarama ve güvenli yol kontrolü
   - Faz 2: nesne deposu, manifest ve `checkpoint`
   - Faz 3: `list`, `status`, `show`, `diff`, `verify`
   - Faz 4: güvenlik checkpoint'li `restore`
   - Faz 5: oturum eşzamanlılığı ve `clean`
8. Her fazın testlerini çalıştır; hata varken sonraki faza geçme.
9. Son olarak gerçek projede yalnız zararsız `init`, `checkpoint`, `list`,
   `status` ve `verify` işlemlerini kullanıcı onayıyla dene. Geri yükleme
   doğrulamasını sentetik kopyada tut.

# 14. Teslim raporu

Rapor şu başlıklarla ve kısa, doğrulanabilir bilgilerle olsun:

## Kurulan yapı
- Eklenen/değiştirilen dosyalar
- Kullanılan dil, çalışma zamanı ve bağımlılıklar
- Nihai `.agent/.checkpoint` klasör şeması

## Kullanım
- Kurulum ve ilk checkpoint komutu
- Listeleme, fark gösterme ve doğrulama
- Tek dosya ve tam proje geri yükleme
- Güvenlik checkpoint'iyle geri yüklemeyi geri alma

## Güvenlik davranışı
- Onay, dry-run, çakışma ve yol güvenliği
- Eşzamanlılık, kilit ve yarım işlem davranışı
- Saklama ve temizlik politikası

## Doğrulama
- Çalıştırılan komutlar ve gerçek sonuçlar
- Test edilen platformlar ve senaryolar
- Doğrulanamayan veya uygulanamayan maddeler

## Sınırlar
- Yerel checkpoint ile haricî yedek arasındaki fark
- Desteklenmeyen dosya türleri ve platform kısıtları
- Kullanıcı kararı gereken noktalar

# 15. Kabul ölçütleri

- [ ] Sistem hiçbir yerde Git komutuna, Git kütüphanesine veya Git dosya
      formatına bağımlı değil.
- [ ] Farklı AI araçları aynı CLI ve dosya formatını kullanabiliyor.
- [ ] Proje taşındığında checkpoint geçmişi okunabiliyor.
- [ ] `.agent/.checkpoint` hiçbir manifeste girmiyor.
- [ ] Aynı içerik nesneleri checkpoint'ler arasında paylaşılıyor.
- [ ] Manifestler bağımsız okunuyor ve dosya listesi deterministik.
- [ ] Yarım yazılan manifest veya nesne canlı hâle gelmiyor.
- [ ] Geri yükleme öncesi güvenlik checkpoint'i ve değişiklik önizlemesi var.
- [ ] Kullanıcı değişiklikleri onaysız ezilmiyor veya silinmiyor.
- [ ] Geri yükleme geçmişi silmiyor; geri yüklemenin kendisi geri alınabiliyor.
- [ ] Bozuk/eksik nesne açık hata veriyor ve geri yüklenmiyor.
- [ ] Oturumlar arası manifest/sıra çakışması önleniyor.
- [ ] Temizlik varsayılan olarak dry-run; canlı manifest nesneleri korunuyor.
- [ ] Tehlikeli testler yalnız sentetik fixture üzerinde çalıştırıldı.
- [ ] Kullanıcı komutları gerçekten çalıştırıldı ve çıktıları doğrulandı.
- [ ] Doğrulanamayan platform veya davranış açıkça `doğrulanmadı` yazıldı.

---

Sonuç olarak hedef; `.nextcode` yaklaşımındaki ayrı durum klasörü ve paylaşılan
içerik fikrini koruyan, ancak kendi JSON manifestleri ve SHA-256 nesne deposu
ile çalışan, **Git gibi geri alma imkânı sunan fakat Git kullanmayan**, yerel ve
AI aracından bağımsız bir checkpoint sistemidir.
