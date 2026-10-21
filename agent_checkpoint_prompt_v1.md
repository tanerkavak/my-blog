# Görev: `.agent/checkpoint.git` — checkpoint sistemi kur

## Rol
Git iç yapısına (plumbing komutları, index, ref'ler) hâkim bir geliştirme
ortamı mühendisisin. Proje dosyalarının anlık görüntülerini (checkpoint)
almak ve geri yüklemek için proje kökünde `.agent/checkpoint.git` adlı bir
checkpoint deposu ve bu depoyu kullanan `checkpoint` komutunu kur.
 
## Bağlam
- Platform: Windows 10/11, Git for Windows ≥ 2.40 (Git Bash / MINGW64).
- Hedef: `<PROJE_KÖKÜ>\.agent\checkpoint.git\`
- Dosya adlarında Türkçe karakter olabilir (ör. `Veri kaynağı.txt`).
  Klasörde okunamayan Excel kilit dosyaları (`~$*.xlsx`) bulunabilir.
- Depo, projenin kendi `.git` deposundan bağımsız bir bare depodur;
  projede `.git` varsa ona dokunma.

## İlkeler
1. **Tek klasör:** Sistemin tamamı `checkpoint.git/` içindedir.
2. **Bayt bayt aynılık:** Geri yüklenen dosya kaydedilenle aynıdır;
   satır sonu (CRLF/LF) dönüşümü yapılmaz.
3. **Veri kaybı yok:** `restore` öncesinde otomatik checkpoint alınır.
   Üzerine yazılacak ya da silinecek dosyalar önce `recycle/` klasörüne
   kopyalanır.
4. **İzolasyon:** Git yalnızca `GIT_DIR` / `GIT_WORK_TREE` /
   `GIT_INDEX_FILE` ile çağrılır. Global git config'e dokunulmaz.
5. **Plumbing:** Snapshot'lar `write-tree` + `commit-tree` + `update-ref`
   ile alınır; hook ve kullanıcı ayarı devreye girmez.
6. **Boş checkpoint yok:** Değişiklik yoksa commit oluşturulmaz.

## Hiyerarşi
```
.agent/
└── checkpoint.git/
    ├── HEAD                  # ref: refs/heads/main
    ├── config                # depo + checkpoint ayarları
    ├── description           # "Checkpoint deposu — <PROJE_ADI>"
    ├── index                 # snapshot index'i (GIT_INDEX_FILE)
    ├── hooks/                # boş — örnek hook'lar silinir
    ├── info/
    │   ├── exclude           # snapshot dışı kalıplar
    │   └── attributes        # "* -text"
    ├── objects/
    │   ├── info/
    │   └── pack/
    ├── refs/
    │   ├── heads/            # main → son checkpoint
    │   ├── tags/             # sabitlenmiş (pin) checkpoint'ler
    │   └── checkpoints/      # <oturum>/<sıra> → her checkpoint
    ├── logs/                 # git reflog'u
    ├── recycle/              # restore öncesi yedekler: <YYYYMMDD-HHMMSS>/...
    └── bin/
        ├── checkpoint.sh     # CLI (Bash)
        └── checkpoint.cmd    # Windows sarmalayıcı → Git Bash
```
`recycle/` ve `bin/` git'in kullandığı adlarla çakışmaz. Bunların dışında
depo köküne özel dosya ekleme.

## Dosya içerikleri

### `config`
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
	logAllRefUpdates = always
[gc]
	auto = 0
[user]
	name = checkpoint
	email = checkpoint@local
[checkpoint]
	maxFileSize = 50m
	retentionDays = 30
	maxCheckpoints = 500
	recycleRetentionDays = 14
```
Betik `[checkpoint]` ayarlarını `git config --get checkpoint.<anahtar>`
ile okur; değerleri koda sabit yazmaz.

### `info/exclude`
```
.agent/
.git/
node_modules/
.venv/
venv/
__pycache__/
.pytest_cache/
.mypy_cache/
~$*
*.tmp
Thumbs.db
desktop.ini
```

### `info/attributes`
```
* -text
```

## `bin/checkpoint.sh`
Bash, `set -euo pipefail`. Betik yolları kendi konumundan hesaplar:
`GIT_DIR=<betik>/..` ve `ROOT=GIT_DIR/../..`. Ardından şu ortamı kurar:
```bash
export GIT_DIR="$CP_HOME"
export GIT_WORK_TREE="$ROOT"
export GIT_INDEX_FILE="$CP_HOME/index"
```
Dosya yolları her yerde `-z` (NUL ayraçlı) işlenir.

| Komut | Davranış |
|---|---|
| `init` | İdempotent kurulum. Eksik parçaları tamamlar, var olan checkpoint'leri silmez. |
| `save "<mesaj>" [--session <id>]` | Dosyaları `ls-files -z --cached --others --exclude-standard` ile listeler, `checkpoint.maxFileSize` sınırını aşanları uyarıyla atlar, index'i `update-index -z --add --remove --stdin` ile günceller. Ardından `write-tree` çalıştırır; ağaç değişmediyse çıkar. Değiştiyse `commit-tree` ile commit oluşturur, `refs/checkpoints/<oturum>/<sıra:06d>` ve `refs/heads/main` ref'lerini günceller, checkpoint kimliğini yazdırır. |
| `list [--session <id>] [--limit N]` | `for-each-ref refs/checkpoints` ile kimlik, zaman, oturum, mesaj ve pin durumunu listeler. |
| `status` | Son checkpoint'ten bu yana değişen dosyaları gösterir. |
| `diff <id> [<id2>]` | İki checkpoint'i karşılaştırır; tek kimlik verilirse çalışma alanıyla karşılaştırır. |
| `show <id> <yol>` | Dosyanın o checkpoint'teki içeriğini yazdırır. |
| `restore <id> [<yol>...]` | Önce `pre-restore` checkpoint'i alır. Değişecek dosyaları `recycle/<zaman>/` altına yedekler. Hedef ağacı `read-tree` ile geçici index'e okur ve `checkout-index -a -f` ile yazar. Hedefte olmayan izlenen dosyaları silmez, `recycle/` klasörüne taşır. Yol verilirse yalnızca o yolları geri yükler. |
| `pin <id> <ad>` / `unpin <ad>` | `refs/tags/<ad>` ekler ya da kaldırır. Sabitlenen checkpoint `prune` ile silinmez. |
| `prune [--dry-run]` | Saklama sınırlarını aşan, sabitlenmemiş checkpoint'leri kaldırır, `reflog expire` + `gc` çalıştırır ve eski `recycle/` klasörlerini temizler. |
| `verify` | `fsck --full --strict` çalıştırır ve sonucu raporlar. |

**Kimlik ve commit mesajı:**
```
<mesaj>

Checkpoint-Id: cp-<YYYYMMDD-HHMMSS>-<kısa-sha>
Session: <oturum>
Sequence: <sıra>
Created-At: <ISO 8601, ofsetli>
```
Checkpoint listesi için ayrı bir dosya tutulmaz; tek kaynak ref'ler ve
commit trailer'larıdır.

**Kilit:** `save`, `restore` ve `prune` sırasında `mkdir "$CP_HOME/checkpoint.lock"`
ile kilit alınır ve `trap` ile her çıkışta kaldırılır.

**Çıkış kodları:** `0` başarılı · `1` kullanım hatası · `2` kilit alınamadı ·
`3` git hatası.

### `bin/checkpoint.cmd`
Argümanları Git Bash ile `checkpoint.sh`'e iletir ve çıkış kodunu döndürür.
Git Bash bulunamazsa anlaşılır bir hata mesajı verir.

## Uygulama adımları
1. `<PROJE_KÖKÜ>\.agent\` zaten varsa **dur ve sor**; üzerine yazma.
2. `git init --bare --initial-branch=main "<PROJE_KÖKÜ>/.agent/checkpoint.git"`
3. `hooks/*.sample` dosyalarını sil.
4. `config`, `description`, `info/exclude` ve `info/attributes` dosyalarını
   yaz (UTF-8, BOM yok, LF).
5. `refs/checkpoints/`, `recycle/` ve `bin/` klasörlerini oluştur;
   `bin/checkpoint.sh` ve `bin/checkpoint.cmd` dosyalarını yaz.
6. `bin/checkpoint.sh init`, ardından `bin/checkpoint.sh save "İlk checkpoint"`.

## Doğrulama (geçici bir test klasöründe)
1. Depo bare, `HEAD` → `refs/heads/main`.
2. `init` ikinci kez çalıştırıldığında hiçbir şeyi değiştirmez.
3. Değişiklik yokken `save` yeni checkpoint oluşturmaz.
4. CRLF içeren bir dosya kaydedilip geri yüklendiğinde `sha256sum` aynı.
5. Türkçe adlı bir dosya kayıt ve geri yüklemeden bozulmadan geçer.
6. `~$test.xlsx`, `node_modules/` ve `.agent/` snapshot'a girmez.
7. Sınırı aşan büyük dosya uyarıyla atlanır.
8. Silinen dosya `restore` ile geri gelir; fazla dosya `recycle/`
   klasörüne taşınır, kalıcı olarak silinmez.
9. `restore` öncesinde `pre-restore` checkpoint'i oluşur.
10. Paralel iki `save` çağrısında depo bozulmaz.
11. `prune --dry-run` sabitlenmiş checkpoint'i listelemez.
12. `verify` hatasız tamamlanır.

## Kısıtlar
- Proje dosyalarını yalnızca `restore` değiştirir; onun da yedeği alınır.
- Global git config'e ve projenin `.git` deposuna dokunma.
- Git for Windows dışında bağımlılık ekleme.
- Listede olmayan dosya oluşturma.

## Çıktı
Oluşturulan hiyerarşiyi (`find .agent`, `objects/` hariç), doğrulama
sonuçlarını (geçti/kaldı) ve tasarımdan sapmaları kısaca raporla.
