# AI Bağımsız Checkpoint Sistemi v3 (v0.0.3) — Yerel CLI Agent'lar İçin Kurulum ve Geliştirme Promptu

Aşağıdaki promptu, projede yerel bir checkpoint ve geri alma sistemi kurmasını
istediğin herhangi bir AI kodlama asistanına verebilirsin. Sistem **proje
içinde ayrı durum klasörü, oturum bazlı kayıtlar ve paylaşılan içerik
nesneleri** fikrine dayanır; ancak Git veya başka bir sürüm kontrol sistemi
kullanmaz.

v2'den gelen odak: sistemin yalnız insanlar tarafından değil, **yerel CLI agent'lar
(Claude Code, Codex CLI, Gemini CLI, Aider, OpenCode vb.) tarafından otomatik,
etkileşimsiz ve güvenli** biçimde kullanılabilmesidir. Agent'ın her dosya
değişikliğinden önce durum kaydedilir, her agent turu geri alınabilir ve agent
kendi başına yıkıcı işlem yapamaz.

Ek olarak sistem, agent'larla yapılan **sohbetleri de yerel olarak
`.agent/.checkpoint/storage/` altında yedekler** ve her sohbet turunu o turda
alınan checkpoint'lere bağlar. Böylece "bu dosya değişikliğini hangi konuşma
üretti?" sorusu yerel olarak cevaplanabilir (Bölüm 7B).

Bu dosya çalıştırılabilir bir betik değil, ayrıntılı bir üretim promptudur.
Köşeli parantezli alanları kullanmadan önce doldur.

## v0.0.3 değişiklikleri (performans denetimi sonrası)

v0.0.2'nin sıcak yolu (tarama + stat cache + SHA-256 + nesne deposu + tam
manifest) yalnız standart kütüphaneyle Python 3.14 üzerinde prototiplenip
sentetik projelerde ölçüldü (Windows 11, i5-13500H, 16 GB, NTFS, Defender
açık). Ölçülen değerler Bölüm 7C'dedir. Bulgular ve yapılan değişiklikler:

1. **Soğuk ilk checkpoint hook bütçesine sığmıyor.** 10.000 dosyada 3–194 sn,
   50.000 dosyada ~18 dk ölçüldü. `fail-closed` ile birleşince agent hiç
   düzenleme yapamaz hâle gelebiliyordu. → Taban checkpoint `init`'e taşındı,
   soğuk durumda hook davranışı ve kaldığı yerden devam eden tarama
   tanımlandı (5.4, 7, 7A.4).
2. **Her checkpoint tam manifest yazınca disk hızla doluyor.** Dosya başına
   ~210 bayt: 10.000 dosyada checkpoint başına 2,1 MB, 50.000 dosyada 10,6 MB.
   → Manifest, klasör bazlı içerik adresli ağaç nesnelerine bölündü; değişmeyen
   klasörler checkpoint'ler arasında paylaşılıyor (5.2, 5.5).
3. **Stat cache her hook'ta baştan okunup yazılıyor.** 50.000 dosyada okuma
   ~58 ms, yazma ~120 ms (8,4 MB). → Değişiklik yoksa yazılmıyor, parçalı
   biçim tanımlandı (5.4).
4. **"Değişmedi" kontrolü önceki manifesti okuyor.** 50.000 dosyada ~90 ms.
   → Son kök özeti `sessions.json` içindeki küçük `head` kaydından okunuyor (7).
5. **Nesne başına `fsync` maliyeti yüksek.** Windows'ta ilk checkpoint süresini
   ~2 katına çıkardı. → Dayanıklılık politikası (`durability`) eklendi (5.3).
6. **Antivirüs taraması soğuk süreyi ~6 kat değiştiriyor.** Aynı 1.000
   dosyada 20 sn ile 3,4 sn arası ölçüldü. → `doctor` bunu raporluyor ve
   dışlama ayarına kendisi dokunmuyor (7C).
7. Test senaryoları 46–52 ve yeni kabul ölçütleri eklendi.

---

# 0. Rol

Kıdemli bir yazılım mimarı, dosya sistemi güvenliği, veri bütünlüğü, agent
entegrasyonu ve test otomasyonu uzmanı olarak çalış. Amacın; kullanıcının ve
yerel AI agent'larının bir projede dosyaların anlık durumlarını kaydetmesini,
geçmişi listelemesini, farkları görmesini ve seçtiği noktaya güvenle geri
dönmesini sağlayan **AI aracından ve Git'ten bağımsız** bir checkpoint sistemi
kurmaktır.

Sistem komut satırından insan tarafından kullanılabilmeli; farklı AI agent'ları
da aynı komutları, kararlı JSON çıktısını ve hook adaptörlerini kullanabilmelidir.
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
| `[HEDEF_AGENTLAR]` | `<Claude Code / Codex CLI / Gemini CLI / Aider / ...>` | Adaptör yazılacak agent'lar |
| `[HOOK_HATA_POLITIKASI]` | `fail-closed` | Checkpoint alınamazsa agent'ın düzenlemesi engellensin mi |
| `[HOOK_SURE_BUTCESI_MS]` | `1500` | Hook başına izin verilen en uzun checkpoint süresi |
| `[SOHBET_ARSIVI]` | `açık` | Agent sohbetlerinin `storage/` altına yedeklenmesi |
| `[SOHBET_MASKELEME]` | `mask` | Sohbetlerdeki gizli bilgi kalıplarının maskelenmesi (`mask` / `none`) |

Parametre eksikse tahminle doldurma. Mevcut proje dili uygunsa onu kullan;
yeni bir çalışma zamanı veya üçüncü taraf bağımlılık eklemeden önce gerekçeyi
belirt. Mümkünse yalnız standart kütüphaneyle çalış. Hook'lar her araç
çağrısında çalışacağı için başlangıç süresi düşük bir çalışma zamanı tercih et.

# 2. Temel ürün tanımı

Kurulacak sistem şu kullanım senaryolarını karşılamalıdır:

1. Kullanıcı projeye sistemi bir kez kurar (`aict init`) ve isterse kullandığı
   agent için adaptörü etkinleştirir (`aict agent install <agent>`).
2. İnsan her önemli değişiklikten önce veya sonra `aict checkpoint` çalıştırır.
3. Agent adaptörü, agent dosya değiştiren bir araç çağırmadan **önce** otomatik
   `pre-edit` checkpoint'i, agent turu bittiğinde `post-turn` checkpoint'i alır.
4. Sistem proje dosyalarının o anki durumunu yerel olarak kaydeder.
5. Kullanıcı `aict list`, `aict show`, `aict diff`, `aict restore` ve
   `aict undo` ile geçmişi inceler ve istediği noktaya döner.
6. Geri alma işlemi geçmişi silmez; mevcut durumu koruyan yeni bir güvenlik
   checkpoint'i ve geri yüklemenin sonucunu anlatan yeni bir kayıt üretir.
7. Farklı AI araçları aynı checkpoint geçmişini kullanabilir; hiçbir araca özgü
   dosya adı, ref ad alanı, eklenti veya oturum protokolü zorunlu değildir.
   Agent'a özgü kısımlar yalnız ince adaptör katmanında yaşar.
8. Aynı projede aynı anda birden fazla agent çalışıyorsa her değişikliğin hangi
   oturuma/agent'a ait olduğu checkpoint'lerden izlenebilir.
9. Agent sohbetleri her tur sonunda, oturum kapanırken ve agent bağlamı
   sıkıştırmadan/temizlemeden önce `storage/` altına yedeklenir.
   `aict chat list/show/search/export` ile okunur; `aict chat for <ref>`
   bir checkpoint'i üreten konuşmayı gösterir.

Checkpoint bir **yedekleme hizmeti değildir**. Aynı diskteki yerel çalışma
geçmişini tutar; disk arızasına, silinmeye veya cihaz kaybına karşı ayrı haricî
yedek gerekir.

# 3. Kesin sınırlar

1. Git komutu çağırma, Git kütüphanesi kullanma, `.git` klasörü oluşturma veya
   projenin mevcut Git yapılandırmasına dokunma.
2. Git nesne biçimini, pack/index/ref yapısını, commit modelini veya Git
   komutlarını taklit eden gizli bir bağımlılık kurma.
3. Checkpoint deposu proje içindeyse taramanın dışında tut. Sistemin kendi
   nesnelerini, önbelleğini veya loglarını yeniden checkpoint'leme.
4. Ağ erişimi, uzak depo, kullanıcı hesabı, bulut eşitlemesi ve telemetri ekleme.
5. Kullanıcı onayı olmadan gerçek projede geri yükleme, temizlik veya geçmiş
   silme işlemi yapma.
6. Kullanıcı değişikliklerini geri yükleme sırasında sessizce ezme. Önce mevcut
   durumu koru ve çakışmaları göster.
7. Gerçek checkpoint geçmişinde bozma, prune veya kurtarma testi çalıştırma.
   Bütün tehlikeli testler sentetik kopyalarda yürütülmeli.
8. Yeni bağımlılıkları otomatik kurma. Eksik bağımlılığı ve kurulum komutunu
   bildir; kullanıcının ortamını değiştirme.
9. Test sonucu, checkpoint sayısı, dosya sayısı veya platform desteği uydurma.
10. Proje kapsamı dışında refactor yapma; istenmeyen doküman veya örnek proje
    üretme.
11. Şifreleme, tam yedek veya çok kullanıcılı güvenlik garantisi verme.
12. **Agent'ın kendi başına yıkıcı işlem yapmasına izin verme.** Agent
    bağlamında (`AICT_ACTOR=agent` veya TTY yok) `restore`, `undo`, `clean
    --apply` ve `pin --remove` insan onayı olmadan uygulanmaz; yalnız dry-run
    önizlemesi döner. `--yes` agent bağlamında bu kuralı aşamaz.
13. Agent yapılandırma dosyalarını (ör. `.claude/settings.json`,
    `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`) kullanıcı onayı olmadan değiştirme.
    Adaptör kurulumu değişecek satırları önce göstermeli ve mevcut içeriği
    korumalıdır.
14. Agent'ların hook belgelerini ezberden varsayma. Hedef agent'ın güncel hook
    / eklenti mekanizmasını kurulu sürümün belgelerinden doğrula; doğrulanamayan
    adaptörü `doğrulanmadı` olarak işaretle.
15. Agent'ın kendi sohbet/transcript dosyalarını **değiştirme, taşıma veya
    silme**; yalnız okuyarak kopyala. Sohbet içeriği yalnız `storage/` altında
    bulunur; checkpoint manifestlerine, `operations.jsonl`'e veya hook
    çıktısına sohbet metni yazılmaz.
16. Sohbet arşivini proje dışına kopyalama, paylaşma veya başka bir agent'ın
    bağlamına kendiliğinden yükleme. Okuma yalnız açık `aict chat` komutuyla
    olur.

# 4. Tasarım ilkeleri

Aşağıdaki genel ilkeleri uygula, fakat Git'e özgü dosya biçimlerini alma:

- Proje kökünde ayrı ve görünür bir durum klasörü bulunması
- İşlerin oturum kimliğiyle ilişkilendirilebilmesi
- Aynı içeriğin farklı checkpoint'lerde tekrar saklanmaması
- Her checkpoint'in sıralı ve bağımsız okunabilir bir kayda sahip olması
- Geçmişin proje kodundan ve normal sürüm kontrolünden ayrılması

Bunların yerine kendi dosya formatını, JSON manifestlerini, SHA-256 içerik
adresli nesneleri ve atomik dosya işlemlerini kullan. Git ref/index/nesne
biçimleri bu sistemin standardı değildir.

# 5. Hedef klasör ve dosya yapısı

Sistem kurulduğunda `[DURUM_KLASORU]` altında aşağıdaki yapıyı oluştur:

```text
.agent/.checkpoint/
├── config.json                 # Şema ve kullanıcı yapılandırması
├── sessions.json               # Oturum kayıtları, son sıra ve head (root_tree) bilgisi (türetilebilir)
├── checkpoints/
│   └── <session-id>/
│       └── <sequence>.json     # Küçük, bağımsız okunabilir checkpoint manifesti (kök ağaca bağlanır)
├── objects/
│   └── <hash[:2]>/
│       └── <hash>              # Dosya içeriği veya klasör ağaç nesnesi; adı SHA-256 özetidir
├── cache/
│   ├── stat-cache/             # Parçalı: <üst-klasör-özeti>.json → yol → (boyut, mtime_ns, ctime_ns, file-id, sha256)
│   └── scan-progress.json      # Yarım kalan soğuk taramanın ilerlemesi (yalnız hızlandırıcı)
├── pins.json                   # Sabitlenmiş checkpoint kimlikleri ve etiketler
├── backups/
│   └── <operation-id>/         # Başarısız işlemde dönüş için geçici güvenlik verisi
├── locks/
│   └── <kilit-adı>.json        # Sahip, PID, oturum, agent ve zaman bilgisi
├── tmp/
│   └── <operation-id>/         # Henüz yayınlanmamış geçici yazımlar
├── logs/
│   └── operations.jsonl        # İçerik sızdırmayan işlem günlüğü
└── storage/                    # Sohbet arşivi (Bölüm 7B)
    ├── index.json              # Sohbet oturumları özeti (türetilebilir)
    ├── objects/
    │   └── <hash[:2]>/<hash>   # Transcript parçaları; adı SHA-256 özetidir
    └── chats/
        └── <agent>/
            └── <agent-session-id>/
                ├── session.json        # Oturum metadata'sı ve parça listesi
                ├── snapshots/
                │   └── <sequence>.json # Tur/olay bazlı arşiv kaydı
                └── normalized.jsonl    # Agent'tan bağımsız okunur kopya (türetilebilir)
```

Bu yapı bir başlangıç standardıdır. Projenin mevcut kuralları farklı adlandırma
gerektiriyorsa kullanıcıya bildir; işlevleri sessizce çıkarma.

Doğruluk kaynağı yalnız `checkpoints/` ve `objects/` klasörleridir.
`sessions.json`, `cache/` ve `pins.json` bozulursa veya silinirse sistem
çalışmaya devam etmeli (sohbet arşivi için doğruluk kaynağı
`storage/chats/**/session.json`, `snapshots/` ve `storage/objects/`'tir;
`index.json` ve `normalized.jsonl` yeniden üretilebilir): oturum/sıra bilgisi manifestlerden, önbellek tam
yeniden hash'lemeyle yeniden oluşturulur. `pins.json` kaybı sabitlemeleri
kaldırdığı için `clean` bu durumda durur ve kullanıcıya sorar.

`init`, durum klasörünün projede sürüm kontrolüne girmemesi için kullanıcıya
uygun ignore satırını **önerir**; ignore dosyasını kendisi değiştirmez.

## 5.1 `config.json`

En az şu alanları sürümlü biçimde tut:

```json
{
  "schema_version": 3,
  "project_root": ".",
  "object_hash": "sha256",
  "exclude": [
    ".agent/.checkpoint/**",
    "node_modules/**", ".venv/**", "venv/**", "__pycache__/**",
    "dist/**", "build/**", "target/**", ".next/**", ".cache/**"
  ],
  "sensitive": [".env", ".env.*", "**/*.pem", "**/*.key", "**/id_rsa*", "**/*.pfx"],
  "sensitive_policy": "metadata-only",
  "follow_symlinks": false,
  "max_file_bytes": 52428800,
  "large_file_policy": "metadata-only",
  "line_endings": "preserve",
  "durability": {
    "manual": "strict",
    "auto": "balanced"
  },
  "retention": {
    "max_checkpoints_per_session": null,
    "max_age_days": null,
    "max_total_bytes": null,
    "keep_auto_checkpoints_days": 14
  },
  "agent": {
    "hook_failure_policy": "fail-closed",
    "hook_time_budget_ms": 1500,
    "coalesce_window_ms": 2000,
    "pre_edit_tools": ["Edit", "Write", "MultiEdit", "NotebookEdit", "Bash"],
    "allow_agent_destructive": false
  },
  "chat_archive": {
    "enabled": true,
    "storage_dir": ".agent/.checkpoint/storage",
    "agents": ["claude-code", "codex", "gemini-cli", "aider"],
    "events": ["turn-end", "session-end", "pre-compact"],
    "redaction": "mask",
    "redact_patterns": ["<yerleşik kalıp kümesi>"],
    "keep_normalized": true,
    "max_transcript_bytes": 209715200,
    "failure_policy": "fail-open",
    "retention": {
      "max_age_days": null,
      "max_total_bytes": null
    }
  }
}
```

- `project_root` taşınabilirliği korumak için göreli tutulur.
- `null` sınır yok demektir; sınırsız saklamanın disk riskini belgeleyicide yaz.
- Dışlama kalıpları açık ve platformdan bağımsız `/` ayraçlı göreli yol kullanır.
- Mevcut proje ignore dosyaları okunabilir ancak hiçbirinin biçimine bağımlı
  olma; sistemin kendi `exclude` kuralları belirleyicidir.
- Varsayılan dışlama listesi yalnız öneridir; `init` bunu kullanıcıya gösterir.
  Projede bulunmayan kalıplar zararsızdır.
- `sensitive`: Bu yollar varsayılan olarak **içerik saklanmadan** yalnız
  metadata ve hash ile kaydedilir (`sensitive_policy`: `metadata-only` /
  `store` / `skip`). Agent'ların sık checkpoint alması gizli dosyaların düz metin
  kopyalarının çoğalması demektir; kullanıcı bilinçli olarak `store` seçmedikçe
  içerik saklama. `metadata-only` dosya geri yüklenemez; `restore` bunu açıkça
  raporlar.
- `large_file_policy`: `max_file_bytes` üstü dosyalar için `metadata-only`,
  `store` veya `error`. Agent hook'ları büyük dosyalar yüzünden süre bütçesini
  aşmamalıdır.
- `line_endings: "preserve"`: CRLF/LF dönüştürmesi yapılmaz; bayt düzeyinde
  saklanır ve geri yüklenir.
- `durability`: Hangi checkpoint türünde ne kadar `fsync` yapılacağı (Bölüm
  5.3). `manual` insan komutları içindir, `auto` hook kaynaklı checkpoint'ler
  içindir.
- `agent.*` alanları Bölüm 7A'da açıklanır.
- `chat_archive.*` alanları Bölüm 7B'de açıklanır. `init`, arşivin açık
  olduğunu ve sohbetlerde gizli bilgi bulunabileceğini **bir kez açıkça
  bildirir ve onay ister**; onay verilmezse `enabled: false` yazılır.
  `storage_dir` durum klasörünün içinde kalmalıdır; dışarıyı gösteren yol
  reddedilir.

Şema sürümü 1 veya 2 olan bir kurulum bulunursa `aict migrate --dry-run` ile neyin
değişeceğini göster; eski manifestler (v2 tam `files` listeli manifestler dahil) yerinde değiştirilmez, okunabilir kalır.

## 5.2 Checkpoint manifesti

Her checkpoint tek başına okunabilir bir JSON belgesi olmalıdır:

```json
{
  "schema_version": 3,
  "checkpoint_id": "<benzersiz-id>",
  "session_id": "<oturum-id>",
  "sequence": 1,
  "created_at": "<UTC ISO-8601>",
  "parent_id": null,
  "trigger": "pre-edit",
  "message": "<kullanıcı veya agent notu>",
  "actor": {
    "kind": "agent",
    "agent": "claude-code",
    "agent_version": "<varsa>",
    "agent_session_id": "<agent'ın kendi oturum kimliği>",
    "turn_id": "<varsa tur/prompt kimliği>",
    "tool": "Edit",
    "tool_call_id": "<varsa>",
    "target_paths": ["src/ornek.py"],
    "host": "<hostname>",
    "pid": 12345
  },
  "chat_ref": {
    "agent": "claude-code",
    "agent_session_id": "<agent oturum kimliği>",
    "snapshot": 7,
    "turn_index": 12
  },
  "root_tree": "<kök klasör ağaç nesnesinin SHA-256 özeti>",
  "root_fingerprint": "<root_tree ile aynı değer; geriye uyumluluk için>",
  "changed": [
    { "path": "src/ornek.py", "change": "modified" }
  ],
  "skipped": [
    { "path": "logs/app.sock", "reason": "unsupported-type" }
  ],
  "summary": {
    "file_count": 1,
    "directory_count": 1,
    "total_bytes": 1234,
    "created": 0,
    "modified": 0,
    "deleted": 0,
    "changed_paths_sample": ["src/ornek.py"]
  }
}
```

`trigger` değerleri sabit bir kümedir:
`manual`, `pre-edit`, `post-edit`, `post-turn`, `session-start`, `pre-restore`,
`restore-result`, `pre-clean`, `migrate`.

`storage` değerleri: `object` (içerik nesnede), `metadata-only` (hassas veya
büyük dosya; içerik yok), `empty-dir`.

Kurallar:

- Yollar UTF-8, göreli ve `/` ayraçlı kanonik biçimde saklanır.
- Dosya listesi manifestte değil, Bölüm 5.5'teki **ağaç nesnelerinde**
  durur. Manifest yalnız `root_tree`'yi gösterir. Manifest, ebeveyn
  checkpoint olmadan, yalnız nesne deposuyla tam okunabilir; bu "bağımsız
  okunabilirlik" kuralını korur. `aict show` ağacı açarak tam dosya listesini
  gösterir.
- Aynı ağaç aynı `root_tree` değerini üretir. `actor`, `message` ve zaman
  alanları ağaç özetine dahil edilmez.
- `changed` yalnız ebeveyne göre değişen yolların özetidir ve hızlı `list` /
  `log` içindir. Doğruluk kaynağı ağaçtır; `changed` en fazla 1.000 yol tutar,
  fazlası `changed_truncated: true` ile işaretlenir.
- Dosya içeriği manifeste gömülmez; `sha256` ile nesneye bağlanır.
- Boş dosyalar ve destekleniyorsa boş klasörler açıkça temsil edilir.
- Dosya silme, önceki manifestin kapsamıyla karşılaştırılarak anlaşılır;
  geçmişteki dosya kaydı silinmez.
- `parent_id` yalnız ilişki bilgisidir; manifest okumak için ebeveyn zorunlu
  olmamalıdır. `parent_id` aynı oturumdaki önceki checkpoint'tir; projenin
  global olarak son checkpoint'i başka oturuma aitse bu ayrıca
  `previous_global_id` alanında tutulabilir.
- `actor` alanında **prompt metni, model çıktısı, araç argümanlarının içeriği,
  token veya ortam değişkeni değerleri tutulmaz.** Yalnız kimlikler, araç adı
  ve hedef yollar saklanır. Sohbete bağlantı yalnız `chat_ref` kimlikleriyle
  kurulur; `chat_ref` isteğe bağlıdır ve sohbet arşivi kapalıysa yazılmaz.
  `chat_ref` fingerprint'e dahil edilmez.
- Bilinmeyen ileri şema sürümü salt okunur raporlanır; eski uygulamayla
  üzerine yazılmaz.
- Yol ve metadata'nın da hassas olabileceği kullanıcıya belirtilir.

## 5.3 Nesne deposu

- Nesne adı içeriğin SHA-256 özetidir; Git nesne biçimi kullanılmaz.
- Nesne önce `tmp/<operation-id>/` altına yazılır, flush/close tamamlanır,
  boyut ve hash doğrulanır, sonra atomik olarak hedef ada taşınır. İşlem
  başına tek bir `tmp/<operation-id>/` klasörü açılır (nesne başına klasör
  açılmaz) ve işlem sonunda boşsa silinir.
- Kopyalama sırasında hash, kaynaktan okunurken hesaplanır. Dosya bir kez
  okunur; hash için ayrı bir okuma yapılmaz.
- **Dayanıklılık (`durability`):**
  - `strict`: Her nesne ve manifest `fsync` edilir, ardından hedef klasör
    `fsync` edilir (destekleyen platformlarda).
  - `balanced`: Nesneler `fsync` edilmeden yayınlanır. Manifest yayınlanmadan
    **önce** bu checkpoint'te yeni yazılan nesneler toplu olarak `fsync`
    edilir (hepsi yazıldıktan sonra tek geçişte), ardından manifest `fsync`
    edilir. Böylece çökme sonrası manifest, diske inmemiş bir nesneyi asla
    göstermez.
  - Ölçüm: Windows/NTFS'te nesne başına `fsync`, soğuk checkpoint süresini
    ~2 katına çıkarıyor (Bölüm 7C). Hangi politikanın seçileceği ölçümle
    belirlenir; `balanced` hiçbir koşulda manifestten önce gelen nesne
    `fsync`'ini atlamaz.
- Aynı hash'e sahip geçerli nesne varsa yeniden yazılmaz.
- Sıfır baytlık içerik de geçerli nesnedir.
- Nesneler varsayılan olarak değişmez kabul edilir; mevcut nesnenin üzerine
  yazılmaz.
- Nesne okunduğunda hash uyuşmazsa işlem durur; bozuk içerik geri yüklenmez.
- Farklı oturumlar ve farklı agent'lar aynı nesneleri güvenle paylaşabilir;
  nesne sahipliği tek oturuma bağlı değildir.
- İki süreç aynı nesneyi aynı anda yayınlamaya çalışırsa hedefin zaten var
  olması hata değil başarıdır (hash doğrulandıktan sonra).

## 5.4 Durum önbelleği (stat cache)

Agent'lar dakikada onlarca checkpoint isteyebilir; her seferinde bütün projeyi
yeniden hash'lemek kabul edilemez.

- `cache/stat-cache/` her yol için `(size, mtime_ns, ctime_ns, inode veya
  Windows file-id)` → `sha256` eşlemesi tutar.
- Önbellek **parçalıdır** (ör. birinci seviye klasöre göre). Yalnız içinde
  değişiklik olan parçalar yeniden yazılır. Hiçbir giriş değişmediyse
  önbelleğe hiç yazılmaz. Tek dosyalık JSON önbellek 50.000 dosyada 8,4 MB'a
  ulaştı ve her hook'ta ~180 ms okuma+yazma maliyeti getirdi (Bölüm 7C).
  Dil standart kütüphanesinde gömülü bir veritabanı varsa (ör. Python
  `sqlite3`) parçalı JSON yerine o da kullanılabilir. Gerekçe raporda
  belirtilir.
- **Kaldığı yerden devam eden soğuk tarama:** İlk tarama veya önbelleği
  silinmiş tarama uzun sürer (50.000 dosyada dakikalar). Tarama sırasında
  önbellek parçaları ve `scan-progress.json` belirli aralıklarla (ör. her
  2.000 dosyada veya 1 saniyede) atomik olarak kaydedilir. Süre bütçesi
  dolduğunda veya işlem kesildiğinde yapılan iş kaybolmaz: bir sonraki
  deneme yayınlanmış nesneleri ve önbelleği yeniden kullanır. Yarım tarama
  **hiçbir zaman** checkpoint olarak yayınlanmaz.
- Bu dört değer aynıysa hash yeniden hesaplanmaz; biri farklıysa dosya yeniden
  okunur.
- mtime çözünürlüğü kaba olan dosya sistemlerinde, son `N` saniye içinde
  değişmiş dosyalar ("racy" dosyalar) önbelleğe güvenilmeden yeniden hash'lenir.
- Önbellek hiçbir zaman doğruluk kaynağı değildir. `aict checkpoint --rehash`
  ve `aict verify --worktree` önbelleği yok sayar.
- Önbellek atomik yazılır; bozuksa sessizce silinir ve tam tarama yapılır,
  bu durum loglanır.

## 5.5 Ağaç nesneleri

Her checkpoint için bütün dosya listesini yeniden yazmak ölçekte kabul
edilemez. Ölçülen değer dosya başına ~210 bayt: 50.000 dosyada checkpoint
başına 10,6 MB eder. Bu yüzden dosya listesi klasör bazlı ağaç nesnelerine
bölünür:

```json
{
  "schema": "aict.tree/1",
  "entries": [
    { "name": "ornek.py", "type": "file", "sha256": "<içerik>", "size": 1234,
      "mode": 420, "mtime_ns": 0, "storage": "object" },
    { "name": "alt", "type": "dir", "tree": "<alt ağaç özeti>" }
  ]
}
```

- Ağaç nesnesi kanonik JSON'dur (UTF-8, sıralı anahtarlar, `name`e göre
  bayt sıralı girdiler, boşluksuz). Adı, bu baytların SHA-256 özetidir ve
  dosya içerikleriyle aynı `objects/` deposunda saklanır.
- Bir klasörde değişiklik yoksa onun ağaç nesnesi (ve bütün alt ağacı)
  değişmez ve yeniden yazılmaz. Tek dosyalık bir düzenleme yalnız o dosyadan
  köke giden yol üzerindeki ağaçları yeniden yazar (klasör derinliği kadar
  küçük nesne).
- Boş klasör, girdisi olmayan ağaçtır. `metadata-only` ve `skipped` bilgisi
  girdinin kendisinde durur.
- Bu yapı, içerik adresli Merkle ağacı fikrinin genel bir uygulamasıdır.
  Biçimi kendi JSON şemasıdır; Git tree/commit nesne biçimi kullanılmaz
  (Bölüm 3.2).
- `verify` ağacı kökten yaprağa dolaşır. Eksik veya hash'i tutmayan ağaç
  nesnesi, eksik içerik nesnesiyle aynı şekilde bütünlük hatasıdır (kod `4`).
- `clean` erişilebilirlik hesabına ağaç nesnelerini de dahil eder.

# 6. Komut satırı sözleşmesi

Komut adlarını ve davranışlarını kararlı tut. Bütün komutlar projenin herhangi
bir alt dizininden çalışabilmeli veya açık `--root <yol>` parametresi almalıdır.

```text
aict init [--json]
aict checkpoint [-m "not"] [--session <id>] [--trigger <tür>]
                [--allow-empty] [--rehash] [--quiet] [--json]
aict list [--session <id>] [--agent <ad>] [--trigger <tür>] [--limit N] [--json]
aict log [--limit N] [--json]                 # Tüm oturumların zaman çizelgesi
aict status [--json]
aict show <checkpoint-id|ref> [--json]
aict diff <ref> [ref] [--path <göreli-yol>] [--stat] [--name-only]
          [--max-lines N] [--json]
aict restore <ref> [--path <göreli-yol>]... [--dry-run] [--yes] [--json]
aict undo [--session <id>] [--steps N] [--dry-run] [--yes] [--json]
aict pin <ref> [--label "ad"] | aict pin --remove <ref>
aict verify [ref] [--worktree] [--json]
aict clean --dry-run [--chats] [--json]
aict clean --apply --yes [--chats]
aict sessions [--json]
aict doctor [--fix-stale] [--json]            # Kilit, tmp, önbellek, şema sağlığı
aict migrate --dry-run | --apply --yes
aict agent install <agent> [--dry-run]        # Adaptör kurulumu (önizlemeli)
aict agent uninstall <agent> [--dry-run]
aict agent hook <olay>                         # Adaptörlerin çağırdığı giriş noktası
aict schema [--json]                           # JSON çıktı şemalarını yazdırır

aict chat list [--agent <ad>] [--limit N] [--json]
aict chat show <chat-ref> [--turn N] [--raw] [--json]
aict chat search "<metin>" [--agent <ad>] [--limit N] [--json]
aict chat for <checkpoint-ref> [--json]         # Checkpoint'i üreten konuşma turu
aict chat export <chat-ref> --format md|jsonl|raw --out <yol>
aict chat import --agent <ad> --from <transcript-yolu> [--dry-run]
aict chat verify [<chat-ref>] [--json]
aict chat reindex                               # index.json ve normalized.jsonl'i yeniden üretir
```

`<chat-ref>` biçimleri: `<agent>:<agent-session-id>`, tekil kısa kimlik,
`@chat-last` (son arşivlenen oturum) ve `<agent>:<agent-session-id>@<snapshot>`.

`<ref>` biçimleri: tam `checkpoint_id`, tekil eşleşen kısa kimlik, pin etiketi,
`@last` (projedeki son checkpoint), `@last~N`, `<session-id>:<sequence>` ve
`@session` (geçerli oturumun son checkpoint'i). Belirsiz eşleşme hata verir ve
adayları listeler.

Her komut için:

- `init`: Yapıyı oluşturur; mevcut geçerli kurulumu bozmaz. Farklı şema veya
  bozuk yapılandırma varsa üzerine yazmaz. Önerilen dışlama ve hassas dosya
  listesini gösterir. Onaydan sonra **taban checkpoint'i** (`trigger:
  session-start`, oturum `init`) hook süre bütçesi olmadan alır. Dosya
  sayısını ve ilerlemeyi stderr'e yazar, Ctrl+C ile kesilirse kaldığı yerden
  devam eder (5.4). Bu adım atlanırsa ilk hook soğuk tarama yapmak zorunda
  kalır (7A.4).
- `checkpoint`: Tam ağacı ağaç nesneleriyle temsil eder (5.5). Önbellek
  sayesinde yalnız değişen dosyaları hash'ler, yalnız değişen klasörlerin ağaç
  nesnelerini yazar ve değişmeyen nesneleri yeniden yazmaz. İçerik değişmediyse
  varsayılan olarak yeni checkpoint üretmez ve mevcut checkpoint kimliğini
  `unchanged: true` ile bildirir. Bilinçli boş checkpoint için `--allow-empty`.
- `list`: Zaman/sıra düzeninde checkpoint özetlerini gösterir; agent, tetikleyici
  ve değişen dosya sayısını içerir.
- `log`: Bütün oturumları tek zaman çizelgesinde birleştirir; birden fazla
  agent'ın aynı projede çalıştığı durumlarda kimin neyi değiştirdiğini gösterir.
- `status`: Son checkpoint'e göre eklenen, değişen ve silinen yolları hesaplar;
  hiçbir dosyayı değiştirmez. Son checkpoint başka bir oturuma aitse bunu belirtir.
- `show`: Manifest metadata'sını, `actor` bilgisini ve dosya listesini gösterir.
- `diff`: İki checkpoint veya checkpoint ile çalışma ağacını karşılaştırır.
  Metin/ikili ayrımı yapar; ikili dosyaları metin gibi yazdırmaz. Metin farkı
  birleşik (unified) biçimdedir. `--stat` ve `--max-lines` agent bağlamını
  şişirmemek için vardır; kesilen çıktı `truncated: true` ile işaretlenir.
- `restore`: Varsayılan olarak dry-run önizlemesi ve onay ister. Birden fazla
  `--path` destekler. `--yes` yalnız onayı atlar; güvenlik checkpoint'ini ve
  bütünlük doğrulamasını atlamaz. Agent bağlamında Bölüm 7A.5 geçerlidir.
- `undo`: Geçerli (veya verilen) oturumun son `pre-edit` checkpoint'ine ya da
  `--steps N` ile N tur geriye dönmenin kısayoludur. İçeride `restore` ile aynı
  güvenlik akışını kullanır. Hangi checkpoint'e döneceğini her zaman önce yazar.
- `pin`: Checkpoint'i sabitler ve isteğe bağlı etiket verir; sabit checkpoint
  otomatik temizlikte silinmez.
- `verify`: Manifest JSON'unu, yol güvenliğini, nesne varlığını, boyutunu ve
  hash'ini denetler. `--worktree` çalışma ağacını önbelleksiz hash'leyip en son
  checkpoint'le karşılaştırır.
- `clean`: Önce adayları ve kazanılacak alanı dry-run ile gösterir. `--apply`
  olmadan hiçbir şey silmez; `--yes` olmadan uygulamaz.
- `sessions`: Oturumları, agent'ı, son sırayı ve son checkpoint'i listeler.
- `doctor`: Bayat kilitleri, yarım `tmp/` klasörlerini, bozuk önbelleği, eksik
  `sessions.json`'u ve şema uyumsuzluğunu raporlar. `--fix-stale` yalnız
  sahibinin yaşamadığı kanıtlanan kilitleri ve yayınlanmamış tmp verisini siler.
- `migrate`: Şema yükseltmesi. Eski manifestleri yerinde değiştirmez.
- `agent install/uninstall`: Bölüm 7A.3'e bakın.
- `agent hook <olay>`: Agent'ın hook JSON'unu stdin'den okur, `actor` bilgisini
  çıkarır ve ilgili checkpoint'i alır. Agent'ın beklediği çıktı/çıkış kodu
  sözleşmesine uyar.
- `schema`: Bütün `--json` çıktılarının sürümlü şemasını yazdırır.
- `chat list/show/search`: Arşivi okur, hiçbir şey değiştirmez. `show`
  varsayılan olarak maskeli ve normalize edilmiş görünümü gösterir; `--raw`
  arşivlenen ham kaydı yazdırır. `search` sonuçları kısa bağlam parçasıyla
  ve `--limit` ile sınırlıdır.
- `chat for`: Checkpoint'in `chat_ref` alanından konuşmayı ve turu bulur;
  bağlantı yoksa bunu açıkça söyler, tahmin etmez.
- `chat export`: Yalnız verilen `--out` yoluna yazar; hedef varsa üzerine
  yazmadan önce onay ister. Agent bağlamında kod `7` döner.
- `chat import`: Arşiv açılmadan önceki veya hook'suz agent'ların
  transcript'lerini elle içe alır; kaynak dosyayı değiştirmez.
- `chat verify`: Parça nesnelerinin varlığını, hash'ini ve parça zincirinin
  bütünlüğünü denetler.

## 6.1 Çıkış kodları

Tutarlı ve belgelenmiş olmalıdır:

| Kod | Anlam |
|---|---|
| `0` | Başarılı (değişiklik yoksa da `0`, `unchanged: true`) |
| `1` | Beklenmeyen iç hata |
| `2` | Kullanım hatası (geçersiz argüman, belirsiz ref) |
| `3` | Bulunamadı (checkpoint, oturum, yol) |
| `4` | Bütünlük hatası (bozuk manifest, eksik/yanlış hash'li nesne) |
| `5` | Güvenlik ihlali (yol kaçışı, symlink dışarı yazma) |
| `6` | Çakışma (onaysız ezilecek kullanıcı değişikliği) |
| `7` | Onay gerekli (etkileşimsiz/agent bağlamında yıkıcı işlem istendi) |
| `8` | Kilit alınamadı / zaman aşımı |
| `9` | Süre bütçesi aşıldı (hook) |
| `10` | Kısmi başarısızlık (geri yükleme kısmen tamamlanamadı; rapor eklidir) |

## 6.2 Makine okunur çıktı

- `--json` çıktısı tek bir JSON belgesidir; stdout'a yalnız bu yazılır.
  İlerleme ve uyarılar stderr'e gider.
- Her JSON çıktısı `{"schema": "aict.<komut>/v2", "ok": true|false, ...}`
  zarfıyla başlar. Hata durumunda `error: {code, exit_code, message, hint}`
  bulunur. `code` sabit bir dizedir (`CONFLICT`, `CONFIRMATION_REQUIRED`,
  `INTEGRITY`, ...); `message` insan içindir ve değişebilir.
- Agent'lar için kısa çıktı esastır: varsayılan insan çıktısı da gereksiz
  satır üretmez; `--quiet` yalnız checkpoint kimliğini yazar.
- `NO_COLOR` ve TTY olmayan ortamda renk/ilerleme çubuğu kullanılmaz.

## 6.3 Ortam değişkenleri

| Değişken | Anlam |
|---|---|
| `AICT_ROOT` | `--root` yerine |
| `AICT_SESSION` | Varsayılan oturum kimliği |
| `AICT_ACTOR` | `human` / `agent`; agent bağlamını açıkça bildirir |
| `AICT_AGENT` | Agent adı (`claude-code`, `codex`, `gemini-cli`, `aider`, ...) |
| `AICT_NONINTERACTIVE` | `1` ise hiçbir zaman soru sorulmaz; onay gerekiyorsa kod `7` |

Oturum kimliği önceliği: `--session` > `AICT_SESSION` > hook JSON'undaki agent
oturum kimliği > süreç ağacından türetilen kararlı kimlik > yeni kimlik.

# 7. Checkpoint oluşturma algoritması

1. Proje ve durum köklerini kanonikleştir; durum klasörünün proje içinde mi
   dışında mı olduğunu belirle.
2. Yapılandırmayı doğrula. Kapsamı, dışlama ve hassas dosya kurallarını uygula.
3. Proje dosyalarını deterministik sırada tara; `.agent/.checkpoint` klasörünü
   kesin olarak atla. Dışlanan klasörlere hiç inme (performans).
4. Her yol için tür, kanonik göreli yol, boyut ve desteklenen metadata'yı topla.
5. Önbellek eşleşiyorsa hash'i önbellekten al; eşleşmiyorsa dosyayı oku.
6. Dosyayı okurken başlangıç/bitiş metadata'sını karşılaştır. İşlem sırasında
   değiştiyse sınırlı sayıda yeniden oku; hâlâ değişiyorsa tutarsız anlık
   görüntü üretme ve açık hata ver. Windows'ta başka süreç tarafından kilitli
   dosya için kısa, sınırlı yeniden deneme yap; sonra açık hata ver.
7. İçeriğin SHA-256 özetini akış hâlinde hesapla; büyük dosyaları gereksiz
   yere belleğe alma. Yeni içerik için hash'i kopyalama sırasında hesapla
   (tek okuma).
8. Yeni nesneleri geçici alana yaz, doğrula ve atomik yayınla.
9. Klasör ağaç nesnelerini aşağıdan yukarı üret (5.5). Değişmeyen klasörün
   önceki ağaç özetini yeniden kullan.
10. **Değişmedi kontrolü:** Yeni `root_tree`'yi `sessions.json` içindeki
    oturum/proje `head` kaydıyla karşılaştır; önceki manifesti dosyadan
    okuma. Head kaydı yoksa veya bozuksa manifestten yeniden kur. Aynıysa
    `unchanged: true` dön; manifest ve önbellek yazma.
11. Küçük manifesti geçici dosyaya yaz ve JSON/şema doğrulaması yap.
12. Oturum sırasını kilit altında ayır. Aynı oturumda sıra çakışmasını önle.
13. `durability` politikasına göre `fsync` yap (5.3). Manifesti hedef ada
    atomik taşı, ardından `head` kaydını ve yalnız değişen önbellek
    parçalarını güncelle.
14. Manifest yayınlanmadan checkpoint başarılı sayılmaz. Hata olursa geçici
    dosyaları temizle; daha önce yayınlanmış checkpoint'lere dokunma.
    Yayınlanmış nesneler ve önbellek ilerlemesi korunur; sonraki deneme
    bunları yeniden kullanır.

Sıra kimliği yalnız oturum içinde monoton olur. Farklı oturumlar aynı sayıyı
kullanabilir; gerçek benzersiz kimlik `checkpoint_id` alanıdır. Kısa kimlikle
erişim yalnız tek eşleşme varsa kabul edilir. `checkpoint_id` zamana göre
sıralanabilir biçimde üretilmelidir (ör. ULID benzeri; ek bağımlılık olmadan).

# 7A. Yerel CLI agent entegrasyonu

## 7A.1 Katmanlar

```text
[Agent (Claude Code / Codex / Gemini CLI / Aider / ...)]
        │  hook olayı (stdin JSON) veya talimat dosyası
        ▼
[Adaptör]  aict agent hook <olay>   ← agent'a özgü tek ince katman
        │  normalize edilmiş actor + trigger
        ▼
[Çekirdek] aict checkpoint / restore / ...   ← agent'tan tamamen bağımsız
```

Çekirdek hiçbir agent adını, dosya biçimini veya hook şemasını bilmez.
Agent'a özgü bütün bilgi adaptörde normalize edilir. Yeni bir agent eklemek
çekirdeği değiştirmemelidir.

## 7A.2 Olaylar ve tetikleyiciler

| Normalize olay | Ne zaman | Trigger | Varsayılan davranış |
|---|---|---|---|
| `session-start` | Agent oturumu açılınca | `session-start` | Taban checkpoint |
| `pre-tool` | Dosya değiştirebilecek araç çağrısından önce | `pre-edit` | Checkpoint; başarısızsa politika |
| `post-tool` | Araç çağrısından sonra | `post-edit` | İsteğe bağlı (varsayılan kapalı) |
| `turn-end` | Agent yanıtını bitirince | `post-turn` | Checkpoint |
| `session-end` | Oturum kapanınca | `post-turn` | Değişiklik varsa checkpoint + sohbet arşivi |
| `pre-compact` | Agent bağlamı sıkıştırmadan/temizlemeden önce | — | Yalnız sohbet arşivi |

`turn-end` olayı checkpoint'ten sonra sohbet arşivini de tetikler (Bölüm 7B).

- `pre_edit_tools` listesi hangi araçların `pre-tool` checkpoint'i
  tetikleyeceğini belirler. Kabuk komutu çalıştıran araçlar (ör. `Bash`) dosya
  değiştirip değiştirmeyeceği bilinemediği için varsayılan olarak dahildir.
- **Birleştirme (coalescing):** Aynı oturumda `coalesce_window_ms` içinde
  gelen ardışık `pre-tool` olaylarında ağaç değişmediyse yeni checkpoint
  üretilmez; mevcut kimlik döner. Böylece bir turda 30 düzenleme 30 checkpoint
  üretmez, ama her gerçek değişiklikten önceki durum yine korunur.
- Hedef yollar (`target_paths`) yalnız ipucudur; manifest yine tam ağacı
  kapsar. İpucu, önbellekte o yolların önce yeniden hash'lenmesi için kullanılır.

## 7A.3 Adaptör kurulumu

`aict agent install <agent>`:

1. Hedef agent'ın kurulu sürümünü ve hook/eklenti desteğini tespit eder.
   Destek doğrulanamıyorsa kurmaz, talimat dosyası yöntemini önerir.
2. Değişecek yapılandırma dosyasını ve eklenecek satırları **dry-run** olarak
   gösterir; mevcut ayarları ve başka hook'ları korur, birleştirir.
3. Kullanıcı onayıyla yazar; önceki dosyanın kopyasını `backups/` altına alır.
4. `uninstall` yalnız kendi eklediği girdileri kaldırır.

Örnek (Claude Code; şemayı kurulu sürüm belgelerinden doğrula):

```json
{
  "hooks": {
    "SessionStart": [{ "hooks": [{ "type": "command", "command": "aict agent hook session-start --agent claude-code" }] }],
    "PreToolUse": [{
      "matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash",
      "hooks": [{ "type": "command", "command": "aict agent hook pre-tool --agent claude-code", "timeout": 10 }]
    }],
    "Stop": [{ "hooks": [{ "type": "command", "command": "aict agent hook turn-end --agent claude-code" }] }],
    "PreCompact": [{ "hooks": [{ "type": "command", "command": "aict agent hook pre-compact --agent claude-code" }] }],
    "SessionEnd": [{ "hooks": [{ "type": "command", "command": "aict agent hook session-end --agent claude-code" }] }]
  }
}
```

Hook desteği olmayan agent'lar için iki yedek yol sun:

- **Talimat dosyası:** `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` benzeri dosyaya
  eklenecek kısa bir blok öner (kullanıcı onayıyla): "Dosya değiştirmeden önce
  `aict checkpoint --trigger pre-edit --quiet` çalıştır; geri yükleme yapma,
  yalnız `aict restore --dry-run` çıktısını kullanıcıya göster."
- **Sarmalayıcı:** `aict run -- <agent komutu>` agent'ı başlatmadan önce
  `session-start`, çıkınca `session-end` checkpoint'i alır ve `AICT_*`
  değişkenlerini alt sürece aktarır. Agent'ın kendisini değiştirmez.

## 7A.4 Hook hata ve süre politikası

- `fail-closed` (varsayılan): `pre-tool` checkpoint'i alınamazsa veya süre
  bütçesi aşılırsa adaptör agent'ın beklediği "engelle" sinyalini döner ve
  kısa, eyleme dönük bir sebep yazar. Kullanıcı verisi korunmadan düzenleme
  yapılmaz.
- `fail-open`: Checkpoint alınamazsa uyarı yazılır, araç çağrısı devam eder,
  olay `operations.jsonl`'e `CHECKPOINT_SKIPPED` olarak düşer.
- Hook hiçbir koşulda agent'ı askıda bırakmaz: kilit beklemesi ve tarama
  `hook_time_budget_ms` ile sınırlıdır.
- **Soğuk başlangıç (taban checkpoint yok veya önbellek boş):** Soğuk tarama
  bütçeye sığmaz (10.000 dosyada saniyeler ile dakikalar arası ölçüldü).
  `fail-closed` burada agent'ı süresiz kilitleyebilir. Bu yüzden:
  - `session-start` hook'u taban checkpoint yoksa soğuk taramayı başlatır ve
    bütçe bitince ilerlemeyi kaydedip çıkar (5.4). Bu olay agent'ı engellemez.
  - Soğuk durumdaki `pre-tool` hook'u, `fail-closed` politikasında düzenlemeyi
    engeller. Yine de ilerlemeyi kaydeder, böylece sonraki denemeler hızlanır.
    Tek satırlık mesajı eyleme dönüktür: `aict: taban checkpoint yok;
    terminalde "aict init" veya "aict checkpoint" çalıştırın (N/M dosya
    hazır)`.
  - Kod `9` (`BUDGET_EXCEEDED`) ve `cold: true`, `progress: {done, total}`
    JSON alanları döner.
  - Projenin belirli bir boyutun üstünde olması (Bölüm 7C eşikleri) bunun
    dışındadır. Önbellek sıcakken bile bütçe aşılıyorsa `doctor` ve `init`
    bunu ölçülmüş süreyle bildirir ve dışlama listesini genişletmeyi önerir.
- Hook çıktısı agent bağlamına girer; tek satır ve kısa olmalı. Başarılı
  `pre-tool` hook'u varsayılan olarak hiçbir şey yazmaz.

## 7A.5 Agent bağlamında yıkıcı işlemler

Agent bağlamı: `AICT_ACTOR=agent`, `aict agent hook` üzerinden çağrı veya TTY
olmayan stdin ile `AICT_NONINTERACTIVE=1`.

- `restore`, `undo`, `clean --apply`, `pin --remove`, `migrate --apply`
  agent bağlamında **yalnız dry-run** sonucu döner ve kod `7`
  (`CONFIRMATION_REQUIRED`) ile biter. Çıktı, insanın çalıştırması gereken tam
  komutu içerir.
- `allow_agent_destructive: true` yalnız kullanıcının açıkça yapılandırmasıyla
  açılabilir; o durumda bile güvenlik checkpoint'i, bütünlük doğrulaması ve
  çakışma koruması atlanmaz ve her işlem `actor` ile loglanır.
- Okuma komutları (`list`, `log`, `status`, `show`, `diff`, `verify`,
  `sessions`, `doctor` raporu) agent için her zaman serbesttir; agent'ın kendi
  değişikliğini incelemesi teşvik edilir.

## 7A.6 Birden fazla agent ve oturum

- Her agent oturumu kendi `session_id`'sine sahiptir; manifest yazımı oturum
  kilidiyle, `restore`/`clean` ise proje genelinde **yazma kilidiyle** korunur.
- Bir oturumun `undo`'su başka bir oturumun sonradan yaptığı değişiklikleri
  geri alacaksa bu, çakışma olarak gösterilir ve hangi oturumun/agent'ın hangi
  dosyayı değiştirdiği listelenir. Onaysız ezilmez.
- `status` ve `log`, son checkpoint'ten sonra değişen dosyaları hangi oturumun
  son dokunduğuna göre etiketleyebilir (mümkünse; tahmin edilemiyorsa
  `unknown`).

# 7B. Sohbet arşivi (`storage/`)

## 7B.1 Amaç ve kapsam

- Agent'larla yapılan sohbetler `.agent/.checkpoint/storage/` altında yerel
  olarak yedeklenir. Amaç; agent kendi kayıtlarını sildiğinde, bağlamı
  sıkıştırdığında veya `/clear` benzeri işlemle temizlendiğinde konuşmanın
  kaybolmaması ve her dosya değişikliğinin hangi konuşmadan geldiğinin
  izlenebilmesidir.
- Arşiv, agent'ın **kendi ürettiği transcript/oturum dosyasının okunarak
  kopyalanmasıyla** oluşur. Sistem agent'ın ekranını, terminal akışını veya
  ağ trafiğini yakalamaz; agent'ın kaydetmediği bir şeyi arşivleyemez.
- Arşiv proje dosyası değildir: proje taramasına girmez, `restore`/`undo` ile
  geri yüklenmez veya silinmez, agent'ın kendi kayıt klasörüne asla geri
  yazılmaz.
- Sohbet arşivi de bir yedekleme hizmeti değildir; aynı diskte durur.

## 7B.2 Transcript kaynağının bulunması

Öncelik sırası:

1. Hook girdisi transcript yolunu veriyorsa (ör. Claude Code hook JSON'undaki
   transcript yolu alanı) o yol kullanılır.
2. Adaptör, agent'ın kurulu sürümüne göre bilinen oturum klasörünü ve oturum
   kimliğini eşleştirir. Bu konumlar sürüme göre değişebileceği için sabit
   kodlanmaz; adaptör bunları kurulu sürümden **doğrular**, doğrulayamazsa
   arşivlemez ve `CHAT_SOURCE_UNVERIFIED` loglar.
3. Hook'suz agent'lar için `aict chat import` veya `aict run --` sarmalayıcısı
   oturum sonunda kullanıcının belirttiği kaynağı içe alır.

Kaynak yolu güvenlik kontrolünden geçer: yalnız normal dosya okunur, symlink
izlenmez, `max_transcript_bytes` üstü kaynak açık uyarıyla atlanır.

## 7B.3 Okuma tutarlılığı

- Agent transcript'e yazmaya devam ediyor olabilir. Dosya yalnız okunur,
  kilitlenmez ve kaynağa hiçbir zaman yazılmaz.
- Satır bazlı (JSONL) kaynaklarda yalnız **son tam satıra kadar** okunur;
  yarım son satır bir sonraki arşivde alınır.
- Okuma başı/sonu metadata'sı karşılaştırılır; dosya küçüldüyse veya önceki
  önek değiştiyse (agent dosyayı yeniden yazdıysa) artımlı mod bırakılıp tam
  kopya alınır ve bu durum snapshot'ta `rewritten: true` ile işaretlenir.

## 7B.4 Artımlı ve içerik adresli saklama

Transcript'ler her turda büyür; her turda tam kopya saklamak diski hızla
doldurur. Bu yüzden:

- `session.json` her oturum için sıralı **parça listesi** tutar:
  `{index, byte_start, byte_end, sha256, redacted, prefix_sha256}`.
- Yeni arşivde, kaynağın daha önce arşivlenen öneki `prefix_sha256` ile
  doğrulanır. Önek aynıysa yalnız yeni bayt aralığı yeni parça olarak saklanır.
- Parçalar `storage/objects/` altında SHA-256 adıyla, Bölüm 5.3'teki atomik
  yazım kurallarıyla saklanır. Bu depo proje nesne deposundan ayrıdır; böylece
  saklama ve temizlik politikaları bağımsız yürür.
- Ham kayıt, parçaların sırayla birleştirilmesiyle yeniden oluşturulur
  (`aict chat export --format raw`).

## 7B.5 Snapshot kaydı ve checkpoint bağlantısı

Her arşiv olayı `snapshots/<sequence>.json` üretir:

```json
{
  "schema_version": 1,
  "agent": "claude-code",
  "agent_version": "<varsa>",
  "agent_session_id": "<oturum>",
  "sequence": 7,
  "created_at": "<UTC ISO-8601>",
  "event": "turn-end",
  "source_path_hint": "<kaynak yolun kullanıcı klasörüne göre kısaltılmış hâli>",
  "parts_upto": 7,
  "turn_count": 12,
  "bytes_total": 482113,
  "redaction": { "mode": "mask", "masked_count": 3, "rules_version": 1 },
  "rewritten": false,
  "checkpoint_ids": ["<bu turda alınan checkpoint kimlikleri>"]
}
```

- Aynı turda alınan `pre-edit`/`post-turn` checkpoint'lerinin `chat_ref` alanı
  bu snapshot'ı gösterir; snapshot da `checkpoint_ids` ile geri bağlanır.
  İki yönlü bağ bozulursa `chat verify` raporlar.
- Kaynak değişmediyse yeni snapshot üretilmez (checkpoint'teki gibi
  `unchanged: true`).

## 7B.6 Maskeleme (redaction)

- Varsayılan `redaction: "mask"`. Parça saklanmadan **önce** bilinen gizli
  bilgi kalıpları `«REDACTED:<tür>»` ile değiştirilir: API anahtarı
  biçimleri, `Bearer` token'ları, bulut erişim anahtarları, özel anahtar
  blokları (`-----BEGIN ... PRIVATE KEY-----`), bağlantı dizelerindeki
  parolalar ve `sensitive` dosyalardan okunmuş `ANAHTAR=değer` satırları.
- Maskelenmiş arşiv kaynakla bayt bayt aynı değildir; bu snapshot'ta
  `masked_count` ile belirtilir ve `export --format raw` çıktısının başına
  not düşülür. Maskelenen değer hiçbir yerde (log dâhil) saklanmaz.
- Önek doğrulaması (7B.4) maskelenmiş içerik üzerinden değil, kaynağın
  maskelenmemiş öneki üzerinden yapılır; bu ara hash yalnız bellekte tutulur,
  geri dönüştürülemez biçimde (`prefix_sha256`) saklanır.
- `redaction: "none"` yalnız kullanıcının açık yapılandırmasıyla seçilir ve
  `init`/`doctor` bunu uyarı olarak gösterir.
- Maskeleme bir garanti değildir; kalıp dışı gizli bilgiler arşive girebilir.
  Bu sınır kullanıcıya açıkça söylenir.

## 7B.7 Normalize görünüm

- `keep_normalized: true` ise her oturum için agent'tan bağımsız
  `normalized.jsonl` üretilir: `{turn, role, timestamp, text, tool_calls:
  [{name, target_paths}], checkpoint_ids}`.
- Araç çağrılarının tam argümanları ve büyük araç çıktıları normalize görünüme
  alınmaz; yalnız ad ve hedef yollar tutulur (ham kayıtta mevcuttur).
- Normalize görünüm türetilmiş veridir; bozulursa `chat reindex` ile ham
  parçalardan yeniden üretilir. Agent biçimi tanınmıyorsa normalize görünüm
  üretilmez, ham arşiv yine saklanır.

## 7B.8 Hata, gizlilik ve erişim

- `failure_policy: "fail-open"` (varsayılan): Sohbet arşivlenemezse agent
  engellenmez; olay `CHAT_ARCHIVE_SKIPPED` koduyla loglanır ve sonraki olayda
  eksik kısım tamamlanır. Sohbet arşivi hatası, proje checkpoint'ini asla
  başarısız kılmaz.
- Arşiv işi hook süre bütçesine dahildir; bütçe aşılacaksa arşiv bir sonraki
  olaya ertelenir.
- `storage/` dosyaları mümkün olan platformlarda yalnız geçerli kullanıcının
  okuyabileceği izinlerle oluşturulur (POSIX `0700`/`0600`; Windows'ta
  kullanıcıya özel ACL — uygulanamazsa raporlanır).
- `init` ve `doctor`, proje klasörü bulut eşitlemesi, paylaşılan klasör veya
  sürüm kontrolü altındaysa sohbetlerin oradan sızabileceğini uyarır ve uygun
  ignore satırını **önerir**.
- Agent bağlamında okuma komutları (`chat list/show/search/for`) serbesttir;
  `export`, arşiv silme ve `redaction` değiştirme insan onayı ister (kod `7`).

## 7B.9 Saklama

- Sohbet arşivi kendi `chat_archive.retention` politikasına sahiptir ve
  yalnız `aict clean --chats` ile temizlenir; varsayılan dry-run ve açık onay
  kuralları aynen geçerlidir.
- Silinecek oturum başka bir sabitlenmiş (`pin`) checkpoint'in `chat_ref`'i
  tarafından gösteriliyorsa korunur.
- Bir oturumun parçaları yalnız oturumun tamamı silinirken silinir; zincirin
  ortasından parça silinmez.

# 7C. Performans hedefleri ve referans ölçümler

## 7C.1 Referans ölçüm (v0.0.2 tasarımının prototipi)

Ortam: Windows 11 Pro, Intel i5-13500H, 16 GB RAM, NTFS SSD, Windows
Defender gerçek zamanlı koruma açık, Python 3.14 (yalnız stdlib). Sentetik
projede dosyaların medyan boyutu ~3 KB'tır (log-normal dağılım) ve ayrıca
dışlanan 5.000 dosyalık bir `node_modules` vardır. Değerler, süreç başlatma
dahil duvar saati süreleridir (5 tekrar).

| Senaryo | 1.000 dosya | 10.000 dosya | 50.000 dosya |
|---|---|---|---|
| Python başlatma (`json`, `hashlib`, `os`) | 34 ms | 34 ms | 34 ms |
| Soğuk ilk checkpoint | 3,4–20 sn* | 194 sn | 1.098 sn (~18 dk) |
| Sıcak, değişiklik yok | 98–138 ms | 180–207 ms | 620–657 ms |
| Sıcak, tek dosya düzenlendi | 138–162 ms | 226–247 ms | 728–776 ms |
| Tarama (`scandir`) | ~45 ms | ~55 ms | ~250 ms |
| Stat cache okuma + yazma (tek JSON) | ~27 ms | ~47 ms | ~178 ms |
| Önceki manifesti okuma | 3–15 ms | 19–39 ms | 89–107 ms |
| Checkpoint başına tam manifest | 0,2 MB | 2,1 MB | 10,6 MB |
| Stat cache boyutu | 0,17 MB | 1,7 MB | 8,4 MB |

\* Aynı 1.000 dosyalık proje: dosyalar yeni oluşturulmuşken (antivirüs
taraması sürüyorken) 20 sn, sonradan 3,4 sn ölçüldü. Nesne başına `fsync`
kapatıldığında aynı soğuk checkpoint 1,7 sn sürdü.

Sonuçlar:

- Sıcak yol 50.000 dosyaya kadar 1.500 ms bütçenin içinde kalıyor. Asıl
  maliyet, değişmeyen veri üzerinde yapılan tam yazma/okumalardır (manifest,
  önbellek). 5.4, 5.5 ve 7 numaralı adımlardaki değişiklikler bunları
  kaldırır. Tahmini kazanç 50.000 dosyada ~300 ms; uygulama bunu ölçerek
  raporlar.
- Soğuk yolun maliyetini dosya başına oluşturma, `fsync` ve antivirüs
  belirler; bayt hızı belirleyici değildir. Bu iş hook içinde yapılamaz.
- Disk: v0.0.2 tasarımıyla 50.000 dosyalık projede günde 100 otomatik
  checkpoint, yalnız manifestler için ~1 GB/gün eder. Ağaç nesneleriyle bu,
  değişen klasör sayısıyla orantılı hâle gelir.

## 7C.2 Hedefler (uygulama ölçüp raporlar, uydurmaz)

| Ölçüt | Hedef |
|---|---|
| Sıcak `pre-tool`, değişiklik yok, 10.000 dosya | ≤ 300 ms (p95) |
| Sıcak `pre-tool`, değişiklik yok, 50.000 dosya | ≤ 800 ms (p95) |
| Tek dosya düzenlemesinde yeni yazılan meta veri | ≤ (klasör derinliği + 1) nesne, ≤ 64 KB |
| Değişiklik yokken diske yazılan bayt | 0 (log satırı hariç) |
| Bellek (50.000 dosya, sıcak) | ≤ 200 MB RSS |
| Soğuk checkpoint | Bütçe yok; ilerleme gösterilir, kesilince devam eder |

- Hedef karşılanmıyorsa raporda ölçülen değer ve darboğaz aşaması
  (tarama / önbellek / hash / yazma) yazılır. Hedef sessizce gevşetilmez.
- 100.000 dosyanın üstündeki projelerde sıcak tarama bile bütçeyi
  zorlayabilir. Bu durumda `init` ölçülmüş süreyi gösterir ve dışlama
  önerir. Dosya sistemi izleyicisi (watcher) veya arka plan servisi
  eklenmesi kapsam dışıdır; ancak kullanıcı kararı olarak raporlanır.
- `doctor`, soğuk checkpoint ölçümü anormal derecede yavaşsa (ör. dosya başına
  > 5 ms) antivirüs gerçek zamanlı taramasının olası etkisini bildirir.
  Antivirüs veya dışlama ayarlarını **kendisi değiştirmez**.

# 8. Geri yükleme algoritması

Geri yükleme sistemin en hassas işlemidir:

1. Hedef checkpoint'in ve kullanacağı bütün nesnelerin bütünlüğünü doğrula.
   `metadata-only` kayıtlı dosyaları geri yüklenemez olarak işaretle.
2. Agent bağlamı ve onay politikasını değerlendir (Bölüm 7A.5).
3. Proje yazma kilidini al.
4. Mevcut çalışma ağacının **otomatik güvenlik checkpoint'ini**
   (`trigger: pre-restore`) oluştur.
5. Hedef ile mevcut ağacı karşılaştır; oluşturulacak, değiştirilecek,
   korunacak, silinecek ve geri yüklenemeyecek dosyaları dry-run önizlemesinde
   listele.
6. Hedef checkpoint'ten sonraki kullanıcı ve diğer oturum değişikliklerini
   tespit et ve açıkça işaretle. Onay yoksa çakışan dosyaları ezme.
7. Tam proje geri yüklemede hedefte olmayan dosyanın silinmesi yalnız ilgili
   kapsam ve onayla yapılır. Yol kısıtlı geri yüklemede başka hiçbir dosyaya
   dokunma.
8. Güvenlik checkpoint'i oluşturulamadıysa geri yüklemeyi başlatma.
9. Dosyaları aynı dosya sistemindeki geçici alana yaz, hash/boyut doğrula ve
   her dosyayı atomik olarak değiştir. Çok dosyalı işlemin tamamını donanım
   düzeyinde atomikmiş gibi gösterme. Bayt düzeyinde geri yükle (satır sonu
   dönüşümü yok); desteklenen izin bitlerini geri koy.
10. Windows'ta hedef dosya başka süreç tarafından kilitliyse sınırlı yeniden
    dene; hâlâ kilitliyse o yolu başarısız say, diğerlerine devam etme kararını
    kullanıcıya bırak (varsayılan: dur ve güvenlik checkpoint'ine dön).
11. İşlem ortasında hata olursa güvenlik kopyasından mümkün olan en güvenli
    dönüşü yap; tamamlanamayan yolları açıkça raporla (kod `10`).
12. Son ağacı hedef manifestle karşılaştır. Bilinçli korunan çakışmalar ve
    geri yüklenemez dosyalar dışında fark varsa işlemi başarılı sayma.
13. Geri yüklemeyi `trigger: restore-result` olan yeni bir checkpoint ve
    operasyon kaydı olarak belgele. Eski checkpoint'leri silme veya sıralarını
    değiştirme. Önbelleği geri yüklenen yollar için güncelle.

Geri alma işlemi yeni bir durum oluşturur; kullanıcı güvenlik checkpoint'ine
dönerek geri yüklemeyi de geri alabilir. Dry-run ve gerçek çıktı, güvenlik
checkpoint kimliğini ve "bunu geri almak için" komutunu içerir.

Geri yükleme sonrası agent'a dönen çıktı, agent'ın bellekteki dosya içeriğinin
artık geçersiz olduğunu belirtmelidir ("değişen dosyaları yeniden oku").

Geri yükleme sohbet arşivine (`storage/`) dokunmaz; konuşmalar geri alınmaz
veya silinmez. Geri yükleme kaydı, ilgili sohbet turuna `chat_ref` ile
bağlanabilir.

# 9. Yol ve platform güvenliği

- `..`, mutlak yol, sürücü değiştirme, UNC kaçışı ve kök dışına çıkan kanonik
  yolları reddet.
- Sembolik bağları varsayılan olarak izleme. Destekleneceklerse bağın kendisini
  ayrı tür olarak sakla ve hedefin proje dışına yazmasını engelle.
- Windows junction/reparse point ve POSIX symlink davranışını ayrı test et.
- Büyük/küçük harf duyarsız sistemlerde aynı hedefe düşen iki yolu sessizce
  ezme; çakışmayı bildir.
- Unicode normalizasyonundan doğan yol çakışmalarını tespit et (macOS NFD).
- Windows ayrılmış adları (`CON`, `NUL`, `COM1`...), sondaki nokta/boşluk ve
  uzun yol (`\\?\`) davranışını ele al.
- Desteklenmeyen socket, device, FIFO ve özel dosyaları atlayıp `skipped`
  listesinde sayısını açıkça raporla; normal dosya gibi okuma.
- Çalışma dizinine değil, hesaplanan proje köküne göre işlem yap. Agent'ın
  `cwd`'si alt klasör olabilir; kök yukarı doğru `.agent/.checkpoint` aranarak
  bulunur.
- Kilit dosyasında PID, oturum, agent, başlangıç zamanı ve hostname bulunsun;
  bayat kilit otomatik silinmeden önce sürecin gerçekten yaşamadığı (ve PID'in
  yeniden kullanılmadığı; süreç başlangıç zamanıyla) doğrulansın.

# 10. Saklama ve temizlik

- Kullanıcı `clean` istemedikçe checkpoint veya nesne silme.
- Saklama politikalarını önce simüle et: silinecek manifestler, korunanlar,
  artık hiçbir manifestin kullanmadığı nesneler ve kazanılacak bayt.
- Canlı herhangi bir manifestten erişilen nesne silinmez.
- Temizlik öncesi bütün manifestler taranır ve doğrulanır. Okunamayan manifest
  varsa otomatik temizlik durur.
- Sabitlenen (`aict pin`) checkpoint korunur; otomatik yaş/boyut politikasına
  kurban edilmez.
- Agent'lar çok sayıda otomatik checkpoint üretir. `keep_auto_checkpoints_days`
  süresinden eski `pre-edit`/`post-edit` checkpoint'leri inceltilebilir; ancak
  her oturumun ilk ve son checkpoint'i, her `post-turn`, her `pre-restore` ve
  `restore-result` korunur.
- Temizlik de geri dönüşü zor bir işlemdir; varsayılan dry-run ve açık onay
  gerektirir. Agent bağlamında uygulanamaz.
- Temizlik sonrası `verify` çalıştırılır; sonuç ve silinen aday sayıları
  raporlanır.
- `clean` varsayılan olarak sohbet arşivine dokunmaz; sohbetler yalnız
  `clean --chats` ile ve Bölüm 7B.9 kurallarıyla temizlenir. Checkpoint
  silindiğinde ona bağlı sohbet kendiliğinden silinmez.

# 11. Hata ve günlük davranışı

- Beklenmeyen hatayı sessizce yutma; hangi aşamada oluştuğunu ve kullanıcının
  verisinin korunup korunmadığını söyle.
- Günlüklerde dosya içeriği, prompt metni, sohbet içeriği, maskelenen değer,
  gizli token, ortam değişkeni değeri veya tam manifest dökümü tutma. Sohbet
  içeriğinin tek yeri `storage/`'dır.
- `operations.jsonl` kayıtları zaman, işlem, sonuç, checkpoint kimliği, süre
  (ms), `actor.kind`, `actor.agent`, oturum ve hata kodu içerebilir.
- Günlük boyutu sınırlandırılır ve döndürülür (rotate); günlük yazılamaması
  ana işlemi başarısız kılmaz ama stderr'de uyarılır.
- Bir nesne yazımı yarım kalırsa canlı nesneye dönüşmez.
- Bozuk oturum özeti ve önbellek, manifestlerden yeniden kurulabilir; bozuk
  manifest veya nesne ise onarılmış gibi gösterilmez.
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
8. Liste, log, durum, gösterim ve iki yönlü fark çıktıları
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

v2 ile eklenen agent senaryoları:

21. Önbellek: dosya içeriği değişip boyut/mtime aynı kaldığında (racy dosya)
    değişikliğin yakalanması; bozuk/silinmiş önbellekle doğru sonuç
22. Hook girişi: örnek agent hook JSON'u stdin'den verilerek `pre-tool`,
    `turn-end` ve `session-start` olaylarının doğru `actor` ve `trigger`
    üretmesi; tanınmayan/bozuk JSON'da güvenli hata
23. Birleştirme: aynı turda değişiklik olmadan ardışık `pre-tool` olaylarının
    tek checkpoint üretmesi; araya gerçek değişiklik girince yeni checkpoint
24. `fail-closed` ve `fail-open` politikalarının, kilit tutulurken ve süre
    bütçesi aşıldığında beklenen çıkış kodu/sinyali vermesi
25. Agent bağlamında `restore`, `undo`, `clean --apply` çağrısının hiçbir dosyayı
    değiştirmeden kod `7` ile dönmesi; `--yes` ile de aşılamaması
26. İki ayrı oturumun aynı projede dönüşümlü değişiklik yapması; `undo`'nun
    diğer oturumun değişikliğini çakışma olarak göstermesi
27. Hassas dosyaların (`.env` vb.) içeriğinin nesne deposunda bulunmadığının
    nesneler taranarak bağımsız kanıtlanması
28. CRLF/LF ve izin bitlerinin geri yüklemede bayt bayt korunması
29. Windows'ta başka süreç tarafından açık/kilitli dosya ile checkpoint ve
    geri yükleme davranışı
30. `--json` çıktılarının `aict schema` şemalarına uyması ve stdout'a JSON
    dışında hiçbir şey yazılmaması
31. `agent install --dry-run` yapılandırma dosyasını değiştirmemesi; gerçek
    kurulumun mevcut başka hook'ları koruması; `uninstall`'ın yalnız kendi
    girdisini kaldırması
32. Hook süresi: orta boy sentetik projede (ör. 10.000 dosya) önbellek sıcakken
    `pre-tool` checkpoint süresinin ölçülüp `[HOOK_SURE_BUTCESI_MS]` ile
    karşılaştırılması (ölçülen değer raporlanır, uydurulmaz)
33. v1 ve v2 şemalı sentetik kurulumlarda `migrate --dry-run`ın hiçbir şeyi
    değiştirmemesi ve eski manifestlerin okunabilir kalması

Sohbet arşivi senaryoları:

34. Sentetik agent transcript'i (JSONL) ile `turn-end` sonrası arşivlenme;
    `export --format raw` çıktısının (maskeleme kapalıyken) kaynakla bayt
    bayt aynı olması
35. Artımlı saklama: ardışık turlarda yalnız yeni bayt aralığının parça olarak
    eklenmesi; değişmeyen kaynakta yeni snapshot üretilmemesi
36. Yazılmakta olan transcript: yarım son satırın alınmaması, sonraki
    arşivde tamamlanması
37. Kaynağın küçülmesi/yeniden yazılması: tam kopyaya geçiş ve
    `rewritten: true`
38. Maskeleme: bilinen token/anahtar kalıplarının arşivde, normalize görünümde
    ve loglarda bulunmadığının arşiv dosyaları taranarak bağımsız kanıtlanması
39. `chat for <checkpoint>` ile doğru tura ulaşılması; bozuk iki yönlü bağın
    `chat verify` ile raporlanması
40. Agent'ın kaynak transcript dosyasının arşivleme öncesi ve sonrası hash'inin
    aynı kalması (kaynağa yazılmadığının kanıtı)
41. `restore`/`undo` sonrası `storage/` içeriğinin hiç değişmemesi
42. Arşiv hatasında (izin, disk dolu, bozuk kaynak) agent'ın engellenmemesi,
    proje checkpoint'inin başarılı kalması ve `CHAT_ARCHIVE_SKIPPED` loglanması
43. `clean --dry-run`'ın sohbetlere dokunmaması; `clean --chats` dry-run'ında
    pin'li checkpoint'e bağlı oturumun korunması
44. `storage/` dosya izinlerinin yalnız kullanıcıya açık olduğunun doğrulanması
    (desteklenen platformlarda; desteklenmeyende `doğrulanmadı`)
45. `storage_dir`'in durum klasörü dışını göstermesi hâlinde yapılandırmanın
    reddedilmesi

v0.0.3 performans senaryoları:

46. 1.000 / 10.000 / 50.000 dosyalık sentetik projelerde Bölüm 7C.1 tablosunun
    yeniden ölçülmesi. Sıcak p50/p95, soğuk süre ve aşama kırılımı raporlanır.
47. Tek dosya düzenlemesinden sonra yalnız kökten o dosyaya giden ağaç
    nesnelerinin yeni yazıldığının, `objects/` öncesi/sonrası listesi
    karşılaştırılarak bağımsız kanıtlanması
48. Değişiklik olmayan sıcak checkpoint'te durum klasörüne hiçbir dosyanın
    yazılmadığının (mtime ve boyut karşılaştırmasıyla) doğrulanması
49. Soğuk taramanın bütçe dolunca kesilmesi, ardından devam etmesi ve sonunda
    kesintisiz taramayla **aynı** `root_tree`'yi üretmesi. Yarım taramanın
    checkpoint olarak yayınlanmadığının doğrulanması.
50. Soğuk durumda `fail-closed` `pre-tool` hook'unun kod `9` ve eyleme dönük
    mesaj vermesi; `session-start`'ın agent'ı engellememesi
51. `balanced` dayanıklılıkta, manifest yayınlanmadan hemen önce süreç
    öldürüldüğünde (sentetik kesinti) manifestin yayınlanmadığının ve
    `verify`'ın temiz çıktığının doğrulanması
52. v2 tam manifestli sentetik kurulumun v3 ağaç biçimiyle okunabilmesi ve
    aynı ağaç için aynı dosya listesini vermesi

Test, yalnız uyguladığın kodun ürettiği değeri tekrar etmemeli. Geri yükleme
sonrası dosyaları beklenen bağımsız içerikle karşılaştır; manifestteki hash'i
tek başına yeterli kanıt sayma. Gerçek agent'larla uçtan uca test yapılacaksa
sentetik proje kopyasında ve kullanıcı onayıyla yap.

# 13. Çalışma sırası

1. Proje talimatlarını ve mevcut kod tabanını oku.
2. Mevcut dil, paket yöneticisi, başlatıcı ve test düzenini belirle.
3. `[HEDEF_AGENTLAR]` için kurulu sürümleri ve hook/eklenti belgelerini tespit
   et; desteklenen olayları, hook giriş/çıkış sözleşmesini ve transcript
   dosyalarının konumunu/biçimini not et. Gerçek transcript'leri yalnız biçim
   tespiti için salt okunur incele; testlerde sentetik transcript kullan.
4. Dosya formatı, CLI, hook politikası ve güvenlik modelinde belirsiz kalan
   kullanıcı kararlarını listele; kod ve dokümanlardan cevaplanamayanları sor.
5. Uygulama modu kapalıysa tasarımı ve bulguları raporlayarak dur.
6. Uygulama modu açıksa önce sentetik test fixture'ını kur.
7. Şu kontrollü fazlarla ilerle:
   - Faz 1: `init`, yapılandırma, tarama ve güvenli yol kontrolü
   - Faz 2: nesne deposu, ağaç nesneleri, manifest, parçalı durum önbelleği, kaldığı yerden devam eden tarama ve `checkpoint` (7C ölçümleriyle)
   - Faz 3: `list`, `log`, `status`, `show`, `diff`, `verify`, JSON şemaları
   - Faz 4: güvenlik checkpoint'li `restore` ve `undo`
   - Faz 5: oturum eşzamanlılığı, `pin`, `clean`, `doctor`
   - Faz 6: agent adaptörleri (`agent hook`, `agent install`), birleştirme,
     hata/süre politikası, agent bağlamı kısıtları
   - Faz 7: sohbet arşivi (`storage/`, artımlı parçalar, maskeleme,
     `chat_ref` bağlantısı, `aict chat *` komutları, `clean --chats`)
8. Her fazın testlerini çalıştır; hata varken sonraki faza geçme.
9. Son olarak gerçek projede yalnız zararsız `init`, `checkpoint`, `list`,
    `status` ve `verify` işlemlerini kullanıcı onayıyla dene. Adaptörü gerçek
    agent yapılandırmasına yalnız `--dry-run` çıktısı onaylandıktan sonra kur.
    Geri yükleme doğrulamasını sentetik kopyada tut.

# 14. Teslim raporu

Rapor şu başlıklarla ve kısa, doğrulanabilir bilgilerle olsun:

## Kurulan yapı
- Eklenen/değiştirilen dosyalar
- Kullanılan dil, çalışma zamanı ve bağımlılıklar
- Nihai `.agent/.checkpoint` klasör şeması

## Kullanım
- Kurulum ve ilk checkpoint komutu
- Listeleme, fark gösterme ve doğrulama
- Tek dosya ve tam proje geri yükleme, `undo`
- Güvenlik checkpoint'iyle geri yüklemeyi geri alma

## Agent entegrasyonu
- Kurulan adaptörler, kullanılan hook olayları ve yapılandırma değişiklikleri
- Hook hata politikası ve ölçülen hook süreleri
- Hook desteği olmayan agent'lar için önerilen yöntem
- `doğrulanmadı` olarak kalan agent/sürüm kombinasyonları

## Sohbet arşivi
- Hangi agent'ların sohbetleri hangi olaylarla arşivleniyor
- Transcript kaynağının nasıl bulunduğu ve doğrulandığı
- Maskeleme modu, kalıp kümesi ve bilinen sınırları
- `storage/` boyutu ve artımlı saklamanın ölçülen etkisi
- Örnek `aict chat list`, `chat for` ve `chat export` çıktıları

## Güvenlik davranışı
- Onay, dry-run, çakışma ve yol güvenliği
- Agent bağlamındaki yıkıcı işlem kısıtları
- Hassas ve büyük dosya politikası
- Eşzamanlılık, kilit ve yarım işlem davranışı
- Saklama ve temizlik politikası

## Doğrulama
- Çalıştırılan komutlar ve gerçek sonuçlar
- Test edilen platformlar ve senaryolar
- Doğrulanamayan veya uygulanamayan maddeler

## Sınırlar
- Yerel checkpoint ile haricî yedek arasındaki fark
- `metadata-only` dosyaların geri yüklenemeyeceği
- Kabuk komutlarının proje dışında yaptığı değişikliklerin (ör. paket kurulumu,
  veritabanı, ağ) checkpoint kapsamında olmadığı
- Desteklenmeyen dosya türleri ve platform kısıtları
- Kullanıcı kararı gereken noktalar

# 15. Kabul ölçütleri

- [ ] Sistem hiçbir yerde Git komutuna, Git kütüphanesine veya Git dosya
      formatına bağımlı değil.
- [ ] Farklı AI araçları aynı CLI ve dosya formatını kullanabiliyor; agent'a
      özgü kod yalnız adaptör katmanında.
- [ ] Proje taşındığında checkpoint geçmişi okunabiliyor.
- [ ] `.agent/.checkpoint` hiçbir manifeste girmiyor.
- [ ] Aynı içerik nesneleri checkpoint'ler arasında paylaşılıyor.
- [ ] Manifestler bağımsız okunuyor ve dosya listesi deterministik.
- [ ] Yarım yazılan manifest veya nesne canlı hâle gelmiyor.
- [ ] Önbellek yalnız hızlandırıcı; silinmesi veya bozulması sonucu değiştirmiyor.
- [ ] Agent'ın dosya değiştiren her araç çağrısından önce durum korunuyor
      (veya `fail-open` ile atlandığı loglanıyor).
- [ ] Ardışık değişikliksiz hook olayları gereksiz checkpoint üretmiyor.
- [ ] Hook'lar süre bütçesine uyuyor ve agent'ı askıda bırakmıyor.
- [ ] Taban checkpoint `init` ile hook dışında alınıyor. Soğuk tarama kesilse
      de ilerleme kaybolmuyor ve yarım tarama checkpoint olarak yayınlanmıyor.
- [ ] Değişiklik olmayan checkpoint durum klasörüne hiçbir şey yazmıyor.
- [ ] Tek dosya değişikliği yalnız değişen yol üzerindeki ağaç nesnelerini
      yazıyor; checkpoint başına meta veri dosya sayısıyla doğrusal büyümüyor.
- [ ] Bölüm 7C.2 hedefleri ölçüldü; karşılanmayanlar ölçülen değer ve
      darboğazla raporlandı.
- [ ] Agent bağlamında yıkıcı işlemler insan onayı olmadan uygulanmıyor.
- [ ] Manifest ve loglarda prompt, model çıktısı, token veya hassas dosya
      içeriği yok; hassas dosya içerikleri varsayılan olarak saklanmıyor.
- [ ] `--json` çıktıları sürümlü şemaya uyuyor; çıkış kodları tabloyla tutarlı.
- [ ] Geri yükleme öncesi güvenlik checkpoint'i ve değişiklik önizlemesi var.
- [ ] Kullanıcı ve diğer oturum değişiklikleri onaysız ezilmiyor veya silinmiyor.
- [ ] Geri yükleme geçmişi silmiyor; geri yüklemenin kendisi geri alınabiliyor.
- [ ] Bozuk/eksik nesne açık hata veriyor ve geri yüklenmiyor.
- [ ] Oturumlar arası manifest/sıra çakışması önleniyor.
- [ ] Temizlik varsayılan olarak dry-run; canlı ve sabitlenmiş checkpoint
      nesneleri korunuyor.
- [ ] Adaptör kurulumu önizlemeli; mevcut agent yapılandırması korunuyor.
- [ ] Agent sohbetleri tur sonu, oturum sonu ve bağlam sıkıştırma öncesinde
      `.agent/.checkpoint/storage/` altına yedekleniyor.
- [ ] Sohbet arşivi artımlı; değişmeyen transcript yeni kayıt üretmiyor.
- [ ] Agent'ın kaynak transcript dosyası hiçbir zaman değiştirilmiyor.
- [ ] Checkpoint ↔ sohbet turu bağlantısı iki yönlü ve doğrulanabilir.
- [ ] Gizli bilgi kalıpları varsayılan olarak maskeleniyor; sohbet içeriği
      manifest ve loglara sızmıyor.
- [ ] Sohbet arşivi hatası agent'ı veya proje checkpoint'ini bozmuyor.
- [ ] `restore`, `undo` ve varsayılan `clean` sohbet arşivine dokunmuyor.
- [ ] Tehlikeli testler yalnız sentetik fixture üzerinde çalıştırıldı.
- [ ] Kullanıcı komutları gerçekten çalıştırıldı ve çıktıları doğrulandı.
- [ ] Doğrulanamayan platform, agent veya davranış açıkça `doğrulanmadı` yazıldı.

---

Sonuç olarak hedef; ayrı durum klasörü ve paylaşılan içerik fikrine dayanan, kendi JSON manifestleri ve SHA-256 nesne deposu ile
çalışan, **Git gibi geri alma imkânı sunan fakat Git kullanmayan**, yerel CLI
agent'larının her düzenlemesini ve sohbetlerini otomatik ve hızlı biçimde
yerelde koruyan, ancak geri
alma ve silme kararını her zaman insana bırakan, AI aracından bağımsız bir
checkpoint sistemidir.
