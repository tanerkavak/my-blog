# Görev: `.git` yapısında checkpoint sistemi + yerel oturum arşivi kur (v2)

## Rol
Git iç yapısına (plumbing komutları, index, ref'ler, nesne deposu) hâkim bir
geliştirme ortamı mühendisisin. Proje dosyalarının anlık görüntülerini
(checkpoint) almak ve geri yüklemek için, kodlama agent'larının kullandığı
`.git` checkpoint düzeninin aynısını kur. Her checkpoint'e bağlı yerel
arşivi de kur: konsol ekran görüntüleri, oturum geçmişi ve komut çıktısı
yedekleri. Bunların hepsini tek bir `checkpoint` komutuyla yönet.

## Bağlam
- Platform: Windows 10/11, Git for Windows ≥ 2.40 (Git Bash / MINGW64),
  Windows PowerShell 5.1 (ekran görüntüsü için, Windows ile gelir).
- Sistem git config'inde `core.autocrlf=true` olabilir. Projede
  `.gitattributes`, LFS ya da filtreler bulunabilir. Checkpoint bunların
  hiçbirinden etkilenmez.
- Dosya adlarında Türkçe karakter olabilir (ör. `Veri kaynağı.txt`).
  Klasörde okunamayan Excel kilit dosyaları (`~$*.xlsx`) bulunabilir.
- `<PROJE_KÖKÜ>` = checkpoint'i alınan klasör (`ROOT`).

## Referans yapı (birebir taklit edilecek)
Agent aracının proje `.git` deposunda gözlenen düzen ve v2'deki karşılığı:

| Referans (agent aracı) | v2 karşılığı |
|---|---|
| `.git/refs/nextcode/checkpoints/<chat-uuid>/<mesaj-no>` | `<GIT_DIR>/refs/agent/checkpoints/<oturum-uuid>/<mesaj-no>` |
| Mesaj no sıfır dolgusuz (`1`, `6`, `14`) | Aynı: `1`, `2`, `15` |
| Commit'in parent'ı yok; her checkpoint bağımsız bir kök commit | Aynı |
| Yazar/işleyen: `cloudcode <checkpoint@cloudcode>` | `agent <checkpoint@agent>` |
| Mesaj: `cloudcode checkpoint: chat <uuid>, before message <n>` | `agent checkpoint: chat <uuid>, before message <n>` |
| Ağaç değişmediyse yeni ref eski commit'i gösterir; yeni commit oluşmaz | Aynı |
| `.git/cloudcode-exclude` (snapshot dışı kalıplar) | `<GIT_DIR>/agent-exclude` |
| Bu ref'ler için reflog yok; `HEAD`, branch, index'e dokunulmaz | Aynı |
| `.nextcode/checkpoints.git/` (projede `.git` yoksa bağımsız depo) | `.agent/checkpoints.git/` |
| `.nextcode/tool-results/` (araç çıktıları) | `.agent/tool-results/` |
| `.nextcode/recycle/` (geri yükleme yedekleri) | `.agent/recycle/` |
| — | `.agent/screenshots/` (konsol ekran görüntüleri) |
| — | `.agent/history/` (oturum ve olay geçmişi) |

## v1 → v2 farkları
| Konu | v1 | v2 |
|---|---|---|
| Depo | Her zaman ayrı bare `.agent/checkpoint.git` | Projede `.git` varsa onun içinde, `refs/agent/` ad alanında. Yoksa bare `.agent/checkpoints.git` |
| Ref | `refs/checkpoints/<oturum>/<sıra:06d>` + `refs/heads/main` | `refs/agent/checkpoints/<oturum-uuid>/<mesaj-no>`; `main` yok |
| Commit | `Checkpoint-Id` trailer'lı, parent tanımsız | Parent'sız kök commit, referans biçiminde ilk satır |
| Değişiklik yokken | Hiçbir şey yapılmaz | Ref yine yazılır, önceki commit'i gösterir |
| Pin | `refs/tags/<ad>` | `refs/agent/pins/<ad>` (projenin tag'lerini kirletmez) |
| Ayarlar | Depo `config` dosyasında | `.agent/config` (her iki modda aynı yer) |
| Satır sonu koruması | `info/attributes` + `autocrlf=false` | `hash-object --no-filters` + `cat-file`; proje ayarlarından bağımsız |
| Yerel arşiv | Yok | `screenshots/`, `history/`, `tool-results/` |

## İlkeler
1. **Git düzeni:** Checkpoint'ler referans yapıdaki ref, commit ve mesaj
   biçimini birebir izler.
2. **Proje deposuna saygı:** Proje modunda `.git` içinde yalnızca
   `refs/agent/**`, `agent-exclude` ve `objects/` (yeni nesneler) değişir.
   `HEAD`, index, branch'ler, tag'ler, stash, `config`, `hooks/` ve reflog'lar
   olduğu gibi kalır. Projenin `git status` çıktısı `save` ile değişmez.
3. **Bayt bayt aynılık:** Dosyalar `git hash-object -w --no-filters` ile
   saklanır ve `git cat-file blob` ile geri yazılır. `autocrlf`, `eol`,
   `.gitattributes`, LFS ve smudge/clean filtreleri devre dışı kalır.
4. **Veri kaybı yok:** `restore` öncesinde `pre-restore` checkpoint'i alınır.
   Üzerine yazılacak ya da silinecek dosyalar önce `recycle/` klasörüne
   kopyalanır ya da taşınır.
5. **İzolasyon:** Git yalnızca `GIT_DIR` / `GIT_WORK_TREE` /
   `GIT_INDEX_FILE` (geçici dosya) ortam değişkenleri ve `-c` geçersiz
   kılmalarıyla çağrılır. Global, sistem ve proje git config'ine yazılmaz.
6. **Plumbing:** Snapshot'lar `hash-object` + `update-index --index-info` +
   `write-tree` + `commit-tree` + `update-ref` ile alınır. Hook ve kullanıcı
   ayarı devreye girmez.
7. **Boş commit yok, ref her zaman var:** Her mesajın bir geri dönüş noktası
   olur, ama aynı ağaç için ikinci commit oluşturulmaz.
8. **Arşiv snapshot dışıdır:** `screenshots/`, `history/` ve `tool-results/`
   checkpoint'e girmez ve `restore` onlara dokunmaz. Geri yükleme kanıtı
   silmez.
9. **Geçmiş yalnızca ekleme ile büyür:** `history/*.jsonl` dosyalarına
   satır eklenir. Var olan satırlar değiştirilmez (`prune` dahil).

## Mod seçimi (`init` sırasında bir kez)
- **project:** `<ROOT>/.git` bir **klasör** ise `GIT_DIR=<ROOT>/.git` olur.
- **standalone:** `.git` yoksa ya da bir **dosya** ise (worktree/submodule),
  `GIT_DIR=<ROOT>/.agent/checkpoints.git` bare deposu kullanılır.
- Mod, `.agent/config` dosyasına `checkpoint.mode` olarak yazılır ve
  kendiliğinden değişmez. Standalone moddayken sonradan `.git` oluşursa
  `init` uyarı verir ama modu değiştirmez.

## Hiyerarşi

### project modu
```
<PROJE_KÖKÜ>/
├── .git/                                  # projenin deposu — yalnızca şunlar eklenir:
│   ├── agent-exclude                      # snapshot dışı kalıplar
│   ├── objects/                           # checkpoint blob/tree/commit nesneleri
│   └── refs/agent/
│       ├── checkpoints/
│       │   └── <oturum-uuid>/
│       │       ├── 1                      # before message 1
│       │       ├── 2
│       │       └── ...
│       ├── pins/<ad>                      # sabitlenmiş checkpoint'ler
│       └── pre-restore/<YYYYMMDD-HHMMSS>  # restore öncesi otomatik checkpoint
└── .agent/
    ├── config                             # ayarlar (git-config biçimi)
    ├── current-session                    # etkin oturum uuid'si (tek satır)
    ├── bin/
    │   ├── checkpoint.sh                  # CLI (Bash)
    │   ├── checkpoint.cmd                 # Windows sarmalayıcı → Git Bash
    │   └── screenshot.ps1                 # ekran görüntüsü (PowerShell 5.1)
    ├── history/
    │   ├── sessions.jsonl                 # oturum listesi
    │   └── <oturum-uuid>.jsonl            # o oturumun olay günlüğü
    ├── screenshots/
    │   └── <oturum-uuid>/
    │       └── <mesaj-no>-<HHMMSS>-<etiket>.png
    ├── tool-results/
    │   └── <oturum-uuid>/
    │       └── <mesaj-no>/
    │           ├── 001-<komut>.log        # `run` ile yakalanan konsol çıktısı
    │           └── 002-<dosya-adı>        # `attach` ile yedeklenen çıktı dosyası
    └── recycle/
        └── <YYYYMMDD-HHMMSS>/<orijinal/yol>
```

### standalone modu
`.agent/` aynıdır. Fark, `.git/` yerine aşağıdaki bare deponun bulunmasıdır:
```
.agent/checkpoints.git/
├── HEAD                 # ref: refs/heads/main (kullanılmaz, bare depo gereği)
├── config
├── description          # "Checkpoint deposu — <PROJE_ADI>"
├── agent-exclude
├── hooks/               # boş — örnek hook'lar silinir
├── objects/{info,pack}/
└── refs/agent/{checkpoints,pins,pre-restore}/
```
Listede olmayan dosya ya da klasör oluşturma. Geçici index ve geçici
dosyalar `mktemp` ile `$TMPDIR` altında oluşturulur ve `trap` ile silinir.

## Dosya içerikleri

### `.agent/config`
```ini
[checkpoint]
	mode = project
	maxFileSize = 50m
	retentionDays = 30
	maxCheckpoints = 500
	recycleRetentionDays = 14
[artifacts]
	screenshotMode = active
	retentionDays = 30
	maxAttachSize = 100m
```
Betik ayarları koda sabit yazmaz. Değerleri
`git config -f "$AGENT_HOME/config" --get <bölüm>.<anahtar>` ile okur;
boyutlar için `--type=int` kullanır (`50m` → bayt). Anahtar yoksa yukarıdaki
değeri varsayılan alır.

### `<GIT_DIR>/agent-exclude`
```
**/.agent/checkpoints.git/
**/.agent/tool-results/
**/.agent/recycle/
**/.agent/screenshots/
**/.agent/history/
**/.agent/bin/
**/.agent/current-session
**/.agent/*.lock
.git/
node_modules/
.venv/
venv/
__pycache__/
.pytest_cache/
.mypy_cache/
.gradle/
~$*
*.tmp
Thumbs.db
desktop.ini
```

### standalone `config`
```ini
[core]
	repositoryformatversion = 0
	filemode = false
	bare = true
	symlinks = false
	ignorecase = true
	autocrlf = false
	safecrlf = false
	quotepath = false
	longpaths = true
	precomposeunicode = true
	logAllRefUpdates = false
[gc]
	auto = 0
```
project modunda projenin `config` dosyasına hiçbir şey eklenmez.

## Commit biçimi
```
agent checkpoint: chat <oturum-uuid>, before message <n>

<isteğe bağlı not>

Session: <oturum-uuid>
Message: <n>
Kind: before-message | manual | pre-restore
Created-At: <ISO 8601, ofsetli>
```
- İlk satır referansla birebir aynıdır. `pre-restore` için ilk satır:
  `agent checkpoint: chat <uuid>, before restore to <hedef>`.
- Yazar ve işleyen bilgisi config'e değil ortam değişkenlerine verilir:
  `GIT_AUTHOR_NAME=agent`, `GIT_AUTHOR_EMAIL=checkpoint@agent` (COMMITTER
  için de aynısı).
- `commit-tree` parent'sız çağrılır.
- **Tekilleştirme:** Yeni ağaç, aynı oturumun son checkpoint'inin ağacıyla
  aynıysa yeni ref o commit'e yazılır ve yeni commit oluşturulmaz.
- Checkpoint listesi için ayrı dosya tutulmaz. Tek kaynak ref'ler ve
  commit mesajlarıdır. `history/` bir günlüktür, kaynak değildir.

## `bin/checkpoint.sh`
Bash, `set -euo pipefail`. Betik yolları kendi konumundan hesaplar:
`AGENT_HOME=<betik>/..` ve `ROOT=AGENT_HOME/..`. `GIT_DIR` değeri
`checkpoint.mode` ayarına göre belirlenir. Bütün git çağrıları tek bir
sarmalayıcıdan geçer:
```bash
export GIT_DIR GIT_WORK_TREE="$ROOT"
g() { git -c core.autocrlf=false -c core.safecrlf=false -c core.eol=lf \
          -c core.quotepath=false -c core.longpaths=true -c core.fsmonitor=false \
          -c gc.auto=0 "$@"; }
# index gerektiren her adımda: GIT_INDEX_FILE="$(mktemp)" g ...
```
Dosya yolları her yerde `-z` (NUL ayraçlı) işlenir. `history/` ve
`tool-results/` içindeki yollar `ROOT`'a göreli ve `/` ayraçlıdır.

### Oturum ve mesaj numarası çözümü
- **Oturum:** Sırasıyla `--session <id>`, `AGENT_SESSION_ID` ortam değişkeni
  ve `.agent/current-session` dosyasına bakılır. Hiçbiri yoksa `save`
  yeni oturum açar. Kısaltılmış kimlik kabul edilir (en az 8 karakter ve
  tek eşleşme olmalı).
- **Mesaj no:** Sırasıyla `--message <n>` ve `AGENT_MESSAGE_NO` kullanılır.
  Hiçbiri yoksa `save` için oturumdaki en büyük no + 1 alınır.
  `shot`/`run`/`attach` için oturumun son checkpoint'inin numarası alınır;
  böylece arşiv, içinde bulunulan mesaja bağlanır.
- **UUID:** v4 biçiminde `/dev/urandom` + `od` ile üretilir. Ek bağımlılık
  kullanılmaz.

### Komutlar
| Komut | Davranış |
|---|---|
| `init` | İdempotent kurulum. Modu belirler, eksik klasör ve dosyaları tamamlar. Var olan ref'leri, arşivi ve ayarları silmez ya da değiştirmez. |
| `session new [--title "<başlık>"]` | Yeni uuid üretir, `current-session` dosyasına yazar, `sessions.jsonl` dosyasına satır ekler ve uuid'yi yazdırır. |
| `session current` / `session list` | Etkin oturumu ya da tüm oturumları (checkpoint sayısıyla) gösterir. |
| `save ["<not>"] [--session] [--message] [--shot]` | Aşağıdaki **Snapshot** adımlarını uygular. Ardından `refs/agent/checkpoints/<uuid>/<n>` ref'ini yazar ve `<uuid-kısa>/<n> <sha-kısa> (new\|reused)` satırını yazdırır. `--shot` verilirse ardından `shot` çalışır. `history`'ye `checkpoint` olayı ekler. |
| `list [--session] [--limit N] [--all]` | `for-each-ref refs/agent/checkpoints` ile oturum, mesaj no, zaman, commit, yeni/tekrar, not, pin durumu, ekran görüntüsü sayısı ve çıktı sayısını listeler. Varsayılan olarak etkin oturumu gösterir; `--all` tüm oturumları gösterir. |
| `status` | Oturumun son checkpoint'inden bu yana eklenen, değişen ve silinen dosyaları gösterir (geçici snapshot ağacı + `diff-tree`). |
| `diff <hedef> [<hedef2>]` | İki checkpoint'i karşılaştırır. Tek hedef verilirse çalışma alanıyla karşılaştırır. `--no-textconv`, filtresiz. |
| `show <hedef> <yol>` | Dosyanın o checkpoint'teki ham baytlarını stdout'a yazar (`cat-file blob`). |
| `restore <hedef> [<yol>...]` | Aşağıdaki **Restore** adımlarını uygular. |
| `pin <hedef> <ad>` / `unpin <ad>` | `refs/agent/pins/<ad>` ekler ya da kaldırır. |
| `shot [--label <etiket>] [--mode active\|screen] [--delay <sn>]` | `screenshot.ps1` ile PNG kaydeder. Yolu yazdırır ve `screenshot` olayı ekler. |
| `attach-shot <dosya> [--label]` | Var olan bir görüntüyü `screenshots/` altına kopyalar. |
| `run [--label] -- <komut> [arg...]` | Komutu çalıştırır. stdout ve stderr'i hem konsola hem `tool-results/.../NNN-<komut>.log` dosyasına yazar. Komutun çıkış kodunu döndürür ve `output` olayı ekler. |
| `attach <dosya> [--label]` | Bir çıktı dosyasını (ör. Excel çıktısı) bayt bayt `tool-results/.../NNN-<ad>` olarak kopyalar ve `attach` olayı ekler. `artifacts.maxAttachSize` sınırını aşan dosya reddedilir. |
| `history [--session] [--message N] [--event <tür>] [--limit N] [--json]` | Olay günlüğünü tablo olarak gösterir. `--json` ham JSONL satırlarını basar. |
| `prune [--dry-run]` | Aşağıdaki **Prune** adımlarını uygular. |
| `verify` | Aşağıdaki **Verify** adımlarını uygular. |

`<hedef>` şunlardan biri olabilir: `<uuid>/<n>` (uuid kısaltılabilir), `<n>`
(etkin oturum), `pin:<ad>`, `pre:<YYYYMMDD-HHMMSS>` ya da commit sha.

### Snapshot (`save`, `status`, `pre-restore` ortak)
1. Dosyalar listelenir:
   `ls-files -z --others --exclude-standard --exclude-from="$GIT_DIR/agent-exclude"`.
   project modunda buna `ls-files -z --cached` eklenir. Bu liste projenin
   index'inden salt okunur alınır, `agent-exclude` kalıplarıyla süzülür ve
   diskte olmayanlar atlanır. Tekrarlar ayıklanır.
2. `checkpoint.maxFileSize` sınırını aşan dosyalar ve adında satır sonu
   olan dosyalar uyarıyla atlanır. Okunamayan dosyalar (kilitli) uyarıyla
   atlanır ve işlem durmaz.
3. Blob'lar `g hash-object -w --no-filters --stdin-paths` ile yazılır.
4. Boş geçici index'e `update-index -z --index-info` ile
   `100644 <sha>\t<yol>` girdileri eklenir. Ardından `write-tree` çalışır.
5. Tekilleştirme kuralı uygulanır, gerekirse `commit-tree` çalışır, sonra
   `update-ref` (reflog'suz, `--no-deref`).

### Restore
1. Kilit alınır. Snapshot alınır ve `refs/agent/pre-restore/<zaman>`
   olarak kaydedilir.
2. `diff-tree -r -z --name-status <şimdiki> <hedef> [-- <yol>...]` ile
   değişecek dosyalar bulunur.
3. `M` (iki tarafta da var, içerik farklı) dosyalar
   `recycle/<zaman>/<yol>` konumuna **kopyalanır**. `D` (şimdi var, hedefte
   yok) dosyalar oraya **taşınır**. Kalıcı silme yapılmaz.
4. `M` ve `A` (hedefte var, şimdi yok) dosyalar
   `g cat-file blob <sha> > <yol>` ile yazılır. Gerekirse önce klasör
   oluşturulur. Filtre ve satır sonu dönüşümü uygulanmaz.
5. Snapshot kapsamı dışındaki dosyalara (yok sayılanlar, `.agent/` arşivi)
   dokunulmaz. project modunda `HEAD`, index ve branch'ler değişmez.
   Sonrasında projenin `git status` çıktısında değişiklik görünmesi
   normaldir.
6. Özet yazdırılır (yazılan, recycle'a giden, atlanan). `restore` olayı
   eklenir; olayda `target`, `pre_restore` ve `recycle` alanları bulunur.

### `bin/screenshot.ps1`
PowerShell 5.1. Parametreler: `-Out <yol> [-Mode active|screen] [-Delay <sn>]`.
- `Add-Type` ile `user32.dll` içindeki `SetProcessDPIAware`,
  `GetForegroundWindow` ve `GetWindowRect` yüklenir. DPI farkındalığı ilk iş
  olarak açılır; aksi halde ölçeklenmiş ekranda görüntü kırpık çıkar.
- `active` modunda ön plandaki pencere yakalanır. Komut konsoldan
  çalıştırıldığı için bu pencere konsolun kendisidir. `screen` modunda
  tüm sanal ekran (`SystemInformation.VirtualScreen`) yakalanır.
- `System.Drawing.Graphics.CopyFromScreen` ile PNG kaydedilir. Hata olursa
  çıkış kodu sıfırdan farklıdır.
- `checkpoint.sh` bu betiği şöyle çağırır:
  `powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -File "$(cygpath -w …/screenshot.ps1)" -Out "$(cygpath -w <yol>)"`.

### `run` çıktı dosyası
```
# cmd: <komut ve argümanlar, tırnaklı>
# cwd: <ROOT'a göreli dizin>
# session: <uuid>  message: <n>
# started: <ISO 8601>
<stdout + stderr, ham bayt, olduğu gibi>
# exit: <kod>  ended: <ISO 8601>  duration: <sn>s
```
- Çıkış kodu `PIPESTATUS[0]` ile alınır ve `run` aynı kodla çıkar.
- Dosya adındaki `<komut>`, komutun ilk kelimesinin temel adıdır. Yalnızca
  `[A-Za-z0-9._-]` karakterleri kalır ve en fazla 40 karakter olur.
- `NNN` numarası mesaj klasöründeki sıradır (001'den başlar). Kilit altında
  hesaplanır.

### `history/` biçimi
UTF-8, BOM yok, LF. Her satır tek bir JSON nesnesidir.

`sessions.jsonl`:
```json
{"session":"<uuid>","started":"<ISO>","mode":"project","title":"<başlık>"}
```
`<oturum-uuid>.jsonl` için olay örnekleri:
```json
{"ts":"<ISO>","session":"<uuid>","message":3,"event":"checkpoint","kind":"before-message","ref":"refs/agent/checkpoints/<uuid>/3","commit":"<sha>","tree":"<sha>","reused":false,"files":42,"skipped":["büyük.zip"],"note":"..."}
{"ts":"<ISO>","session":"<uuid>","message":3,"event":"screenshot","path":".agent/screenshots/<uuid>/3-101502-konsol.png","mode":"active","bytes":183422}
{"ts":"<ISO>","session":"<uuid>","message":3,"event":"output","path":".agent/tool-results/<uuid>/3/001-python.log","cmd":"python main.py","exit":0,"duration_s":12}
{"ts":"<ISO>","session":"<uuid>","message":3,"event":"attach","path":".agent/tool-results/<uuid>/3/002-rapor.xlsx","source":"cikti/rapor.xlsx","bytes":51200}
{"ts":"<ISO>","session":"<uuid>","message":4,"event":"restore","target":"<uuid>/2","pre_restore":"refs/agent/pre-restore/<zaman>","recycle":".agent/recycle/<zaman>","written":5,"recycled":2}
```
Diğer olay türleri `pin`, `unpin` ve `prune`'dur. JSON, jq kullanılmadan
üretilir. `json_escape` fonksiyonu `\` ve `"` karakterlerini, `\n` `\r` `\t`
kontrol karakterlerini ve kalan kontrol karakterlerini (`\u00XX`) kaçırır.
Türkçe karakterler olduğu gibi yazılır. Ekleme kilit altında `>>` ile
yapılır.

### Prune
- Silinmeye aday checkpoint'ler: `checkpoint.retentionDays` süresinden eski
  olanlar ve `checkpoint.maxCheckpoints` sınırını aşan en eski ref'ler.
  Şu checkpoint'ler hiçbir zaman silinmez: pin'lenmiş commit'i gösterenler
  ve her oturumun son checkpoint'i.
- Ref'ler `update-ref -d` ile silinir. `pre-restore` ref'leri
  `recycleRetentionDays` süresine tabidir.
- `artifacts.retentionDays` süresinden eski `screenshots/` ve
  `tool-results/` mesaj klasörleri silinir. Pin'lenmiş mesajlarınkiler
  korunur. `recycleRetentionDays` süresinden eski `recycle/` klasörleri
  silinir.
- **standalone:** `reflog expire --expire=now --all` ve
  `gc --prune=now` çalışır.
  **project:** `gc` çalıştırılmaz (projenin deposunu yeniden paketlemek
  kapsam dışıdır). Erişilemez nesneler projenin kendi `gc`'si ile temizlenir.
- Bir `prune` olayı eklenir. Eski history satırları silinmez.
- `--dry-run` hiçbir şeyi değiştirmeden silinecekleri listeler.

### Verify
- standalone modunda `fsck --full --strict` çalışır. project modunda
  `rev-list --objects refs/agent | cat-file --batch-check` ile tüm
  checkpoint nesnelerinin varlığı denetlenir ve projenin geri kalanı
  denetlenmez.
- Her checkpoint ref'inin parent'sız commit olduğu ve ilk satırının
  biçime uyduğu doğrulanır.
- `history/` içinde adı geçen her `path` dosyasının var olduğu
  (prune edilmişse `prune` olayıyla açıklandığı) doğrulanır.

### Kilit ve çıkış kodları
- `save`, `restore`, `prune`, `run`/`attach` (numara alma anı),
  `session new` ve history ekleme sırasında
  `mkdir "$AGENT_HOME/checkpoint.lock"` ile kilit alınır. Kilit `trap` ile
  her çıkışta kaldırılır. Kilit 10 saniye içinde alınamazsa çıkış kodu 2'dir.
  `run`, komut çalışırken kilidi tutmaz.
- Çıkış kodları: `0` başarılı · `1` kullanım hatası · `2` kilit alınamadı ·
  `3` git hatası · `4` ekran görüntüsü hatası. `run` ise sarılan komutun
  kodunu döndürür.

### `bin/checkpoint.cmd`
Argümanları Git Bash ile `checkpoint.sh`'e iletir ve çıkış kodunu döndürür.
`bash.exe`, sırasıyla `where git` çıktısındaki Git kurulumunun `bin\`
klasöründe ve `%ProgramFiles%\Git\bin\` klasöründe aranır. Bulunamazsa
anlaşılır bir hata mesajı verir.

## Uygulama adımları
1. `<PROJE_KÖKÜ>\.agent\` zaten varsa **dur ve sor**; üzerine yazma.
   İçinde v1 kurulumu (`.agent/checkpoint.git`) varsa bunu ayrıca belirt.
   Kullanıcı onaylarsa v1 ref'leri
   `g fetch <v1-yolu> 'refs/checkpoints/*:refs/agent/import-v1/*'` ile
   aktarılır ve v1 klasörü silinmez.
2. Modu belirle (project / standalone).
3. standalone modunda:
   `git init --bare --initial-branch=main "<ROOT>/.agent/checkpoints.git"`.
   Ardından `hooks/*.sample` dosyalarını sil, `config` ve `description`
   dosyalarını yaz.
4. `<GIT_DIR>/agent-exclude`, `.agent/config` ve `.agent/bin/*` dosyalarını
   yaz (UTF-8, BOM yok, LF; `.cmd` ve `.ps1` için CRLF). Klasörleri oluştur.
5. Sırayla `bin/checkpoint.sh init`, `session new --title "Kurulum"` ve
   `save "İlk checkpoint" --shot` komutlarını çalıştır.

## Doğrulama (geçici test klasörlerinde, iki mod için ayrı ayrı)
1. **project — dokunulmazlık:** `save` ve `restore` öncesi ve sonrası
   şunlar aynıdır: `.git/HEAD`, `.git/index` ve `.git/config` dosyalarının
   `sha256sum` değeri, `git status --porcelain`,
   `git for-each-ref refs/heads refs/tags` ve `git stash list`.
2. Ref `refs/agent/checkpoints/<uuid>/<n>` biçimindedir ve `n` sıfır
   dolgusuzdur. Commit'in parent'ı yoktur. Yazar
   `agent <checkpoint@agent>` olur. İlk satır biçime uyar.
3. Değişiklik yokken `save` yeni ref yazar. `rev-parse` sonucu önceki
   ref'le aynıdır ve nesne sayısı (`count-objects -v`) artmaz.
4. Test deposunda `core.autocrlf=true` ve `.gitattributes` içinde
   `* text=auto eol=lf` ayarlıyken CRLF dosyası kaydedilip geri
   yüklendiğinde `sha256sum` aynı kalır.
5. Türkçe adlı bir dosya kayıt, `show` ve geri yüklemeden bozulmadan geçer.
6. `~$test.xlsx`, `node_modules/`, `.gitignore`'a takılan dosya ve
   `.agent/` arşivi snapshot'a girmez. project modunda izlenen (tracked)
   dosya girer.
7. Sınırı aşan büyük dosya uyarıyla atlanır.
8. `restore`: silinen dosya geri gelir, fazla dosya `recycle/` klasörüne
   taşınır, değişen dosyanın eski hali `recycle/` klasörüne kopyalanır,
   `pre-restore` ref'i oluşur ve `screenshots/`, `history/` ile
   `tool-results/` değişmez.
9. `shot`: oluşan PNG sıfır bayttan büyüktür, ilk 4 baytı `89 50 4E 47`
   olur ve `screenshot` olayı yazılır.
10. `run -- bash -c 'echo out; echo err >&2; exit 7'` çıkış kodu 7 verir.
    Log dosyasında `out`, `err`, başlık ve `# exit: 7` bulunur.
11. `attach`: kopya bayt bayt aynıdır (`cmp`).
12. `history`: tırnak, satır sonu ve Türkçe karakter içeren bir not
    kaydedilir. Her satır
    `powershell -c "Get-Content -Encoding UTF8 … | % { $_ | ConvertFrom-Json }"`
    ile hatasız ayrışır.
13. Paralel iki `save` çağrısında depo bozulmaz ve mesaj numaraları
    çakışmaz.
14. `prune --dry-run` pin'lenmiş checkpoint'i ve oturumun son
    checkpoint'ini listelemez. project modunda `prune` sonrası
    `.git/objects/pack/` değişmez.
15. `init` ikinci kez çalıştırıldığında hiçbir şeyi değiştirmez.
16. `verify` hatasız tamamlanır.

## Kısıtlar
- Proje dosyalarını yalnızca `restore` değiştirir; onun da yedeği alınır.
- Global, sistem ve proje git config'ine yazma. Geçersiz kılmalar yalnızca
  `-c` ve ortam değişkenleriyle yapılır.
- Proje `.git` deposunda **İlke 2**'deki listenin dışında hiçbir şeye
  dokunma.
- Git for Windows ve Windows ile gelen PowerShell 5.1 dışında bağımlılık
  ekleme (jq, Python ve benzerleri kullanılmaz).
- Listede olmayan dosya oluşturma.
- Not: `refs/agent/**` normal `push` ve `clone` ile taşınmaz, ancak
  `git push --mirror` ile uzak depoya gider. Raporda bunu belirt.

## Çıktı
Kısaca şunları raporla: seçilen mod, oluşturulan hiyerarşi (`find .agent`
ve `find <GIT_DIR>/refs/agent` çıktısı, `objects/` hariç), iki mod için
doğrulama sonuçları (geçti/kaldı) ve tasarımdan sapmalar.
