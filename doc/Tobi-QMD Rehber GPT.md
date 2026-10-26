# QMD (Query Markup Documents) — Türkçe Kullanım Rehberi

> **Proje:** [tobi/qmd — GitHub](https://github.com/tobi/qmd)  
> **Paket:** `@tobilu/qmd`  
> **Amaç:** Markdown notlarını, dokümantasyonu, toplantı kayıtlarını ve diğer metin tabanlı bilgi kaynaklarını yerel olarak indekslemek ve aramak.

## İçindekiler

- [1. QMD nedir?](#1-qmd-nedir)
- [2. Ne işe yarar?](#2-ne-işe-yarar)
- [3. Nasıl çalışır?](#3-nasıl-çalışır)
- [4. Gereksinimler](#4-gereksinimler)
- [5. Kurulum](#5-kurulum)
- [6. İlk kurulum ve hızlı başlangıç](#6-i̇lk-kurulum-ve-hızlı-başlangıç)
- [7. Arama komutları](#7-arama-komutları)
- [8. Belgeleri açma ve sonuçları dışa aktarma](#8-belgeleri-açma-ve-sonuçları-dışa-aktarma)
- [9. Koleksiyon ve bağlam yönetimi](#9-koleksiyon-ve-bağlam-yönetimi)
- [10. İndeksi güncelleme](#10-i̇ndeksi-güncelleme)
- [11. Yapay zekâ ajanları ve MCP](#11-yapay-zekâ-ajanları-ve-mcp)
- [12. Örnek iş akışı](#12-örnek-i̇ş-akışı)
- [13. Sorun giderme](#13-sorun-giderme)
- [14. Avantajlar ve sınırlamalar](#14-avantajlar-ve-sınırlamalar)
- [15. Resmî kaynaklar](#15-resmî-kaynaklar)

## 1. QMD nedir?

QMD, “Query Markup Documents” ifadesinin kısaltmasıdır. Bilgisayardaki Markdown dosyaları, notlar, toplantı dökümleri ve dokümantasyonlar üzerinde arama yapabilen, komut satırından kullanılan yerel bir arama motorudur.

Geleneksel dosya araması çoğunlukla tam kelime eşleşmesine dayanır. QMD ise farklı arama yöntemlerini bir araya getirerek hem belirli kelimeleri hem de benzer anlamdaki ifadeleri bulmaya çalışır.

Örneğin belgelerinizde “sunucuya dağıtım” ifadesi geçmese bile “uygulama nasıl yayına alınır?” sorgusu, anlamsal arama sayesinde ilgili bir belgeyi bulabilir.

QMD; komut satırı aracı (CLI), Node.js/Bun kütüphanesi ve MCP sunucusu olarak kullanılabilir.

## 2. Ne işe yarar?

QMD şu senaryolarda yararlıdır:

- Büyük bir Markdown not arşivinde bilgi bulmak.
- Proje dokümantasyonunda belirli bir özelliği veya hata çözümünü aramak.
- Toplantı notlarından kararları ve yapılacak işleri bulmak.
- Obsidian benzeri Markdown tabanlı bilgi klasörlerinde arama yapmak.
- Yapay zekâ ajanlarına yerel belgelerden bağlam sağlamak.
- Sonuçları JSON veya dosya listesi olarak başka araçlara aktarmak.

**Önemli:** QMD tek başına bir sohbet botu ya da belge düzenleyicisi değildir. Temel görevi belgeleri indekslemek, ilgili olanları bulmak ve içeriklerini geri getirmektir.

## 3. Nasıl çalışır?

QMD üç temel arama yaklaşımını birleştirir:

1. **BM25 / tam metin araması (`search`):** Aramadaki kelimelerin belgelerdeki eşleşmelerini bulur. Belirli terimler ve teknik isimler için kullanışlıdır.
2. **Vektör araması (`vsearch`):** Metinlerin anlam benzerliğine bakar. Sorgudaki kelimeler belgede birebir geçmese de ilgili sonuçlar bulabilir.
3. **Hibrit arama (`query`):** Sorguyu genişletir, tam metin ve vektör sonuçlarını birleştirir ve sonuçları yerel bir dil modeliyle yeniden sıralar.

Basitleştirilmiş akış:

```text
Belgeler
   |
   v
Koleksiyon ve indeks
   |
   +--> Tam metin araması (BM25)
   |
   +--> Vektör/anlamsal arama
             |
             v
      Sonuçları birleştirme
             |
             v
      LLM ile yeniden sıralama
             |
             v
        İlgili belgeler
```

QMD, yerel model çalıştırmak için `node-llama-cpp` ve GGUF biçimindeki modellerden yararlanır. İlk kullanımda model dosyalarının indirilmesi ve embedding oluşturulması gerekebilir; bu yüzden disk alanı, RAM ve işlemci performansı önemlidir.

## 4. Gereksinimler

- Desteklenen bir işletim sistemi ve terminal.
- Güncel Node.js veya Bun kurulumu.
- Belgelerin bulunduğu yerel klasör.
- Vektör ve hibrit arama için model dosyalarını indirmeye yetecek internet bağlantısı ve disk alanı (ilk kurulumda).
- Daha hızlı yerel model çalıştırma için yeterli RAM; donanım ihtiyacı seçilen modellere ve veri miktarına göre değişir.

Sürüm gereksinimleri değişebileceği için kurulumdan önce [resmî README](https://github.com/tobi/qmd) ve paket belgelerini kontrol edin.

## 5. Kurulum

### Seçenek A — npm ile

```bash
npm install -g @tobilu/qmd
```

### Seçenek B — Bun ile

```bash
bun install -g @tobilu/qmd
```

### Global kurulum yapmadan çalıştırma

```bash
npx @tobilu/qmd --help
```

veya:

```bash
bunx @tobilu/qmd --help
```

Kurulumdan sonra komutun erişilebilir olduğunu kontrol edin:

```bash
qmd --help
```

> **Not:** Windows'ta komut bulunamıyorsa Node.js/npm veya Bun'ın PATH ayarlarını kontrol edin. Komut ve model desteğiyle ilgili en güncel işletim sistemi notları için GitHub deposunu inceleyin.

## 6. İlk kurulum ve hızlı başlangıç

Aşağıdaki örneklerde `~/notes` gibi yollar kullanılmıştır. Kendi klasör yolunuzla değiştirin.

### 6.1. Bir klasörü koleksiyon olarak ekleyin

```bash
qmd collection add ~/notes --name notes
```

Başka klasörler de ekleyebilirsiniz:

```bash
qmd collection add ~/Documents/meetings --name meetings
qmd collection add ~/work/docs --name docs
```

Koleksiyon, QMD'nin tarayacağı bir belge grubudur.

### 6.2. Koleksiyona açıklayıcı bağlam ekleyin

```bash
qmd context add qmd://notes "Kişisel notlar ve fikirler"
qmd context add qmd://meetings "Toplantı kayıtları ve kararlar"
qmd context add qmd://docs "Teknik dokümantasyon"
```

Bağlam açıklamaları, arama sonuçlarının ne tür bir koleksiyondan geldiğini anlamaya yardımcı olur. Açıklamayı kısa ve doğru tutun.

### 6.3. Vektör indeksini oluşturun

```bash
qmd embed
```

Bu işlem, anlamsal aramada kullanılan vektör temsillerini oluşturur. İlk çalıştırma, model indirme ve dosya sayısına bağlı olarak zaman alabilir.

### 6.4. İlk aramanızı yapın

```bash
qmd search "proje zaman çizelgesi"
qmd vsearch "uygulama nasıl yayına alınır"
qmd query "çeyreklik planlama süreci"
```

- `search`: kelime odaklı arama.
- `vsearch`: anlam benzerliğine dayalı arama.
- `query`: hibrit arama ve yeniden sıralama.

Genel amaçlı ve daha kaliteli sonuçlar için `query` ile başlayın; hız veya belirli terim eşleşmesi öncelikliyse diğer modları deneyin.

## 7. Arama komutları

### Belirli bir koleksiyonda arama

```bash
qmd search "API" -c docs
```

### Sonuç sayısını belirleme

```bash
qmd query -n 10 "kimlik doğrulama akışı"
```

### En düşük skor eşiği belirleme

```bash
qmd query --min-score 0.3 "hata yönetimi"
```

Skor eşiği yükseldikçe daha az ama daha ilgili sonuç gelebilir. En uygun değeri kendi belgelerinizde deneyerek belirleyin.

### Sonuçların neden geldiğini inceleme

```bash
qmd query --explain "veritabanı bağlantı zaman aşımı"
```

### Yeniden sıralamayı atlayarak hızlandırma

```bash
qmd query --no-rerank "auth"
```

Bu seçenek daha hızlı olabilir; sonuç sıralaması hibrit aramanın tam yeniden sıralama aşamasından geçmez.

### JSON biçiminde sonuç alma

```bash
qmd search "authentication" --json -n 10
```

### Eşleşen dosyaları listeleme

```bash
qmd query --all --files --min-score 0.4 "hata ayıklama"
```

### Belirli bir amaca göre sorguyu netleştirme

```bash
qmd query --intent "web sayfası yüklenme süreleri" "performans"
```

`--intent`, belirsiz bir kelimenin hangi anlamda aranacağını açıklamak için kullanılabilir.

## 8. Belgeleri açma ve sonuçları dışa aktarma

### Bir belgeyi yoluyla getirme

```bash
qmd get "meetings/2024-01-15.md"
```

### Arama sonucunda görülen belge kimliğiyle getirme

```bash
qmd get "#abc123"
```

`#abc123` yalnızca örnektir; kendi arama sonucunuzdaki belge kimliğini kullanın.

### Belgenin tamamını gösterme

```bash
qmd get "docs/api-reference.md" --full
```

### Birden fazla belgeyi desenle getirme

```bash
qmd multi-get "journals/2025-05*.md"
```

### Sonuçları Markdown olarak alma

```bash
qmd search --md --full "error handling"
```

### Tam dosya yollarını gösterme

```bash
qmd search --full-path "API"
```

Seçeneklerin sürüme göre değişebileceğini unutmayın; gerektiğinde `qmd search --help` ve `qmd get --help` komutlarını çalıştırın.

## 9. Koleksiyon ve bağlam yönetimi

Koleksiyonları konuya göre ayırmak arama sonuçlarını yönetmeyi kolaylaştırır. Örneğin:

- `notes`: kişisel notlar
- `meetings`: toplantı dökümleri
- `docs`: teknik belgeler
- `projects`: proje kayıtları

Örnek:

```bash
qmd collection add ~/projects --name projects
qmd context add qmd://projects "Aktif projelerin planları, kararları ve teknik notları"
qmd query -c projects "kim hangi işi üstlendi"
```

Koleksiyon adları ve yollarının kendi kurulumunuzda doğru tanımlandığını kontrol edin. Koleksiyon/bağlam yönetiminin ayrıntıları için [resmî README](https://github.com/tobi/qmd) içindeki güncel komut açıklamalarına bakın.

## 10. İndeksi güncelleme

Kaynak belgeler değiştikçe QMD indeksini de güncel tutun. Yaygın kullanım:

```bash
qmd update
```

Vektörleri yeniden oluşturmanız gerektiğinde:

```bash
qmd embed
```

Bunların çalışma ayrıntıları ve seçenekleri QMD sürümüne bağlı olabilir; güncellemeden önce `qmd update --help` ve resmî belgeleri kontrol edin.

## 11. Yapay zekâ ajanları ve MCP

QMD yalnızca terminalden kullanılmak zorunda değildir. MCP (Model Context Protocol) sunucusu üzerinden destekleyen yapay zekâ istemcilerine belge arama ve getirme araçları sağlayabilir.

### 11.1. MCP sunucusunu başlatma

```bash
qmd mcp
```

QMD'nin MCP araçları sürüme göre değişebilmekle birlikte, temel olarak şu işlevleri sunar:

- `query`: ilgili belgeleri arama.
- `get`: bir belgeyi getirme.
- `multi_get`: birden çok belgeyi toplu getirme.
- `status`: indeks ve koleksiyon durumunu görme.
- `metadata`: indekslenmiş metadata alanlarını keşfetme.

### 11.2. Claude Desktop örneği

Resmî README'de örneklenen yapılandırma dosyası macOS'ta şu konumdadır:

`~/Library/Application Support/Claude/claude_desktop_config.json`

Örnek yapılandırma:

```json
{
  "mcpServers": {
    "qmd": {
      "command": "qmd",
      "args": ["mcp"]
    }
  }
}
```

Bu yapılandırma örneği her istemci ve işletim sistemi için aynı olmayabilir. Kullandığınız uygulamanın MCP yapılandırma biçimini kontrol edin ve değişiklikten sonra uygulamayı yeniden başlatın.

### 11.3. Claude Code

Resmî depoda belirtilen eklenti kurulum örneği:

```bash
claude plugin marketplace add tobi/qmd
claude plugin install qmd@qmd
```

Komutların kullanılabilirliği Claude Code sürümünüze ve eklenti sistemine bağlıdır. Alternatif olarak istemcinin desteklediği biçimde MCP sunucusunu elle yapılandırabilirsiniz.

### 11.4. HTTP aktarımı hakkında uyarı

QMD sürümünüz HTTP sunucusu sunuyorsa, yalnızca yerel kullanım için tasarlanmış uç noktaları kimlik doğrulaması olmadan internete açmayın. Resmî doküman, ağ arayüzüne açılan sunucular için host/origin doğrulaması ve erişim güvenliğine dikkat çekiyor. Uzak erişim gerekiyorsa uygun kimlik doğrulama ve ağ kısıtlamaları uygulayın.

## 12. Örnek iş akışı

Bir proje klasörünüzde yüzlerce Markdown belgesi olduğunu varsayalım.

```bash
# 1. Proje belgelerini koleksiyon olarak ekle
qmd collection add ~/work/my-project/docs --name project-docs

# 2. Koleksiyonu tanımla
qmd context add qmd://project-docs "My Project teknik belgeleri ve proje kararları"

# 3. Anlamsal arama indeksini hazırla
qmd embed

# 4. Bir soruyu araştır
qmd query "kullanıcı girişinde token nasıl yenileniyor"

# 5. Belirli bir dosyayı getir
qmd get "authentication.md"

# 6. Sonuçları bir yapay zekâ ajanına aktarmaya uygun JSON üret
qmd query --json -n 10 "token yenileme akışı"
```

Dosya adlarınız ve klasör yapınız farklıysa yolları uyarlayın. Örnek belge adları gerçek deponuzda bulunmayabilir.

## 13. Sorun giderme

### `qmd: command not found`

- QMD'nin global olarak kurulduğunu kontrol edin.
- npm veya Bun'ın global çalıştırılabilir dosya dizininin `PATH` içinde olduğundan emin olun.
- Yeni bir terminal açıp tekrar deneyin.
- Gerekirse `npx @tobilu/qmd --help` ile global kurulum olmadan test edin.

### İlk arama yavaş

- İlk kullanımda modellerin indirilmesi veya hazırlanması gerekebilir.
- Çok sayıda belgeyi indekslemek zaman alabilir.
- İlk denemede `qmd search` ile kelime araması yapıp ardından `qmd embed` ve `qmd query` aşamalarını deneyin.

### Anlamsal arama sonuç vermiyor veya zayıf

- İlgili klasörün koleksiyon olarak eklendiğini kontrol edin.
- İndeksin güncel olduğundan emin olun.
- Gerekliyse `qmd embed` çalıştırın.
- `search`, `vsearch` ve `query` sonuçlarını karşılaştırın.
- `--intent` ile arama amacını daha açık belirtin.

### Çok fazla ilgisiz sonuç geliyor

- `--min-score` değerini yükseltmeyi deneyin.
- Koleksiyonu `-c` ile sınırlandırın.
- Sorguyu daha spesifik yazın.
- Koleksiyon bağlam açıklamalarını gözden geçirin.

### Model veya donanım kaynaklı sorunlar

- Disk alanını, RAM kullanımını ve model indirme durumunu kontrol edin.
- Daha küçük veya uygun bir model seçeneği olup olmadığını resmî belgelerden inceleyin.
- Sorun devam ederse QMD GitHub deposundaki Issues bölümünde benzer hata kayıtlarını arayın.

## 14. Avantajlar ve sınırlamalar

### Avantajlar

- Belgeler üzerinde yerel arama yaklaşımı sunar.
- Kelime eşleşmesini ve anlamsal aramayı birleştirir.
- CLI, kütüphane ve MCP üzerinden farklı iş akışlarına uyarlanabilir.
- JSON ve dosya listesi çıktıları otomasyon ve yapay zekâ ajanları için kullanışlıdır.
- Belgeleri konu bazında koleksiyonlara ayırmaya ve bağlam eklemeye imkân tanır.

### Sınırlamalar

- İlk kurulum ve vektör oluşturma ek zaman, disk alanı ve işlem gücü gerektirebilir.
- Arama kalitesi belge düzenine, sorguya ve seçilen modellere bağlıdır.
- Bir arama motoru olduğu için belgelerde olmayan bilgileri kendiliğinden doğrulamaz.
- MCP veya HTTP entegrasyonunda istemci yapılandırması ve güvenlik ayarları gerekir.
- Komutlar ve desteklenen özellikler geliştikçe değişebilir; güncel README ve sürüm notları esas alınmalıdır.

## 15. Resmî kaynaklar

- **GitHub deposu ve kurulum:** https://github.com/tobi/qmd
- **README:** https://github.com/tobi/qmd/blob/main/README.md
- **Sorgu sözdizimi:** https://github.com/tobi/qmd/blob/main/docs/SYNTAX.md
- **Sürümler ve değişiklikler:** https://github.com/tobi/qmd/releases

---

## Hızlı başvuru

| Amaç | Komut |
|---|---|
| Kurulum | `npm install -g @tobilu/qmd` |
| Klasör ekleme | `qmd collection add ~/notes --name notes` |
| Vektörleri oluşturma | `qmd embed` |
| Kelime araması | `qmd search "aranacak kelime"` |
| Anlamsal arama | `qmd vsearch "sorun doğal dille"` |
| Hibrit arama | `qmd query "aranan konu"` |
| Belge getirme | `qmd get "dosya.md"` |
| JSON çıktı | `qmd search "konu" --json` |
| İndeksi güncelleme | `qmd update` |
| MCP sunucusu | `qmd mcp` |

> Bu doküman başlangıç rehberidir. Komutların en güncel biçimi ve işletim sistemi desteği için her zaman [resmî GitHub deposunu](https://github.com/tobi/qmd) kontrol edin.
