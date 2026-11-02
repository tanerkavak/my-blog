# -*- coding: utf-8 -*-
"""
Scraper Yöneticisi — GUI iskeleti (tkinter)
-------------------------------------------
Orijinal uygulamanın yalnızca arayüzü: menüler, araç çubukları, arama/filtre,
scraper tablosu, alt sekmeler (Çıktı / Detay / Genel Günlük), sağ tık menüsü,
durum çubuğu ve diyalog pencereleri.

İş mantığı (tarama, kontrol, kuyruk, süreç yönetimi, export, kayıt/ayar dosyaları,
modül yükleme) bilinçli olarak kaldırıldı. Butonlar ve menü komutları aşağıdaki
"İŞLEYİCİLER" bölümündeki boş metotlara bağlıdır; mantığı oraya ekleyebilirsiniz.
"""
import os
import tkinter as tk
import tkinter.font as tkfont
from tkinter import ttk

WIN = os.name == "nt"

FILTRELER = ("Tümü", "Yeni (bu tarama)", "Hiç çalışmamış", "Başarılı",
             "Hatalı / Uyarılı", "Kontrol sorunlu", "Çalışan / Sırada", "Kayıp")

PENCERE_GENISLIK = 860      # sabit pencere boyutu (px)
PENCERE_YUKSEKLIK = 560
ALT_PANEL_YUKSEKLIK = 150   # sabit alt sekme paneli yüksekliği (px)

KOLONLAR = ("yol", "kontrol", "kayit", "ilerleme")
BASLIKLAR = {"#0": "Scraper Adı", "yol": "Scraper Yolu", "kontrol": "Kontrol",
             "kayit": "Kayıt", "ilerleme": "İlerleme"}
GENISLIK = {"#0": 190, "yol": 250, "kontrol": 170, "kayit": 60, "ilerleme": 90}
STRETCH = ("#0", "yol", "kontrol")          # pencere genişleyince büyüyen sütunlar
SAGA_YASLI = ("kayit",)                      # sayısal sütunlar

# Ayarlar penceresindeki alanlar: (etiket, anahtar, varsayılan, gözat?, ipucu)
AYAR_ALANLARI = (
    ("Python yorumlayıcısı", "python", r"C:\Python\PyEnv\Scripts\python.exe", True,
     r"Varsayılan: C:\Python\PyEnv\Scripts\python.exe"),
    ("Kök klasör", "kok", "", True, "Bu klasör ve tüm alt klasörleri taranır"),
    ("Dosya kalıbı", "kalip", "*scraper*.py", False,
     "';' ile ayrılmış glob kalıpları, örn. *scraper*.py;*_bot.py"),
    ("Hariç klasörler", "haric", "__pycache__;.git;.venv;venv;node_modules", False,
     "';' ile ayrılmış klasör adı kalıpları, örn. __pycache__;*eski*"),
    ("Paralel çalışma", "paralel", "3", False, "Aynı anda çalışacak scraper sayısı"),
    ("Zaman aşımı (dk)", "zaman_asimi_dk", "0", False,
     "0 = sınırsız; aşılırsa süreç ağacı sonlandırılır"),
    ("Export klasörü", "export", "_export_", True,
     "Çıktılar buraya scraper'ın klasör yapısıyla taşınır"),
)


def kisalt_yol(yol):
    """Yolu son klasör + dosya adına indirir: '.../vitra/vitra_scraper.py'.
    'Scraper Yolu' sütununa satır eklerken bu fonksiyonla kısaltılmış değeri yazın."""
    parcalar = (yol or "").replace("\\", "/").split("/")
    if len(parcalar) <= 2:
        return "/".join(parcalar)
    return ".../" + "/".join(parcalar[-2:])


def ilerleme_metni(oran, parca=5):
    """0.0-1.0 arası oranı '▰▰▰▱▱' biçiminde çubuğa çevirir ('İlerleme' sütunu için).
    Örn. ilerleme_metni(0.6) -> '▰▰▰▱▱'"""
    oran = max(0.0, min(1.0, float(oran or 0)))
    dolu = round(oran * parca)
    return "▰" * dolu + "▱" * (parca - dolu)


# ------------------------------------------------------------ akışlı araç çubuğu
class AkisCubugu(ttk.Frame):
    """Grupları soldan sağa dizer; sığmayan grup alt satıra kayar (pencere daralınca
    butonlar kaybolmaz). sag=True gruplar son satırın sağına yaslanır."""

    def __init__(self, ust, bosluk=12, satir_bosluk=4):
        super().__init__(ust, height=1)
        self._sol, self._sag = [], []
        self._bosluk, self._satir_bosluk = bosluk, satir_bosluk
        self._is = None
        self.bind("<Configure>", self._zamanla)

    def grup(self, sag=False):
        g = ttk.Frame(self)
        g.bind("<Configure>", self._zamanla)
        (self._sag if sag else self._sol).append(g)
        self._zamanla()
        return g

    def _zamanla(self, _e=None):
        if self._is is None:
            self._is = self.after_idle(self._yerlestir)

    def _yerlestir(self):
        self._is = None
        W = self.winfo_width()
        if W <= 1:
            return
        b = self._bosluk
        satirlar, satir, x = [], [], 0
        for g in self._sol:
            w = g.winfo_reqwidth()
            if satir and x + w > W:
                satirlar.append(satir)
                satir, x = [], 0
            satir.append((g, x))
            x += w + b
        if self._sag:
            sw = sum(g.winfo_reqwidth() for g in self._sag) + b * (len(self._sag) - 1)
            if satir and x + sw > W:
                satirlar.append(satir)
                satir = []
            x = max(0, W - sw)
            for g in self._sag:
                satir.append((g, x))
                x += g.winfo_reqwidth() + b
        if satir:
            satirlar.append(satir)
        y = 0
        for s in satirlar:
            h = max(g.winfo_reqheight() for g, _ in s)
            for g, gx in s:
                g.place(x=gx, y=y + (h - g.winfo_reqheight()) // 2)
            y += h + self._satir_bosluk
        yukseklik = max(1, y - self._satir_bosluk)
        if int(self.cget("height")) != yukseklik:
            self.configure(height=yukseklik)


# ------------------------------------------------------------------ uygulama
class Uygulama(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scraper Yöneticisi")
        self.geometry(f"{PENCERE_GENISLIK}x{PENCERE_YUKSEKLIK}")
        self.resizable(False, False)      # boyut sabit

        self._stil()
        self._menu()
        self._arayuz()

        self.protocol("WM_DELETE_WINDOW", self.kapat)
        self.bind_all("<F5>", lambda e: self.yeniden_tara())
        self.bind_all("<Control-f>", lambda e: (self.ara_giris.focus_set(), "break"))

    # ------------------------------------------------------------- görünüm
    def _stil(self):
        stil = ttk.Style(self)
        if WIN and "vista" in stil.theme_names():
            stil.theme_use("vista")
        stil.configure("Treeview", rowheight=22)
        temel = tkfont.nametofont("TkDefaultFont")
        self.kalin = temel.copy()
        self.kalin.configure(weight="bold")

    def _menu(self):
        mb = tk.Menu(self)

        dosya = tk.Menu(mb, tearoff=False)
        dosya.add_command(label="Yeniden tara", accelerator="F5", command=self.yeniden_tara)
        dosya.add_command(label="Kontrol et", command=self.kontrol_et)
        dosya.add_separator()
        dosya.add_command(label="Kök klasörü aç", command=self.kok_klasoru_ac)
        dosya.add_command(label="Log klasörünü aç", command=self.log_klasoru_ac)
        dosya.add_command(label="Export klasörünü aç", command=self.export_ac)
        dosya.add_command(label="Ayarlar...", command=self.ayarlar_penceresi)
        dosya.add_separator()
        dosya.add_command(label="Çıkış", command=self.kapat)
        mb.add_cascade(label="Dosya", menu=dosya)

        calistir = tk.Menu(mb, tearoff=False)
        calistir.add_command(label="Seçilenleri çalıştır", accelerator="Enter",
                             command=self.secilenleri_calistir)
        calistir.add_command(label="Görünenleri çalıştır", command=self.gorunenleri_calistir)
        calistir.add_command(label="Tümünü çalıştır", command=self.tumunu_calistir)
        calistir.add_command(label="Hatalıları yeniden çalıştır", command=self.hatalilari_calistir)
        calistir.add_separator()
        calistir.add_command(label="Durdur", command=self.durdur)
        mb.add_cascade(label="Çalıştır", menu=calistir)

        self.modul_menu = tk.Menu(mb, tearoff=False)
        self.modul_menu.add_command(label="(yüklü modül yok)", state="disabled")
        self.modul_menu.add_separator()
        self.modul_menu.add_command(label="Modül klasörünü aç", command=self.modul_klasoru_ac)
        mb.add_cascade(label="Modüller", menu=self.modul_menu)

        self.config(menu=mb)

    def _arayuz(self):
        # --- Üst araç çubuğu
        ust = AkisCubugu(self)
        ust.pack(fill="x", padx=6, pady=(6, 0))
        g = ust.grup()
        for metin, komut in (("▶▶ Tümünü Çalıştır", self.tumunu_calistir),
                             ("▶ Seçilenleri Çalıştır", self.secilenleri_calistir),
                             ("■ Durdur", self.durdur)):
            ttk.Button(g, text=metin, command=komut).pack(side="left", padx=2)

        # --- İkinci çubuk: arama, filtre, genişlet/daralt, özet
        ikinci = AkisCubugu(self)
        ikinci.pack(fill="x", padx=6, pady=6)
        g = ikinci.grup()
        ttk.Label(g, text="Ara:").pack(side="left")
        self.ara_var = tk.StringVar()
        self.ara_giris = ttk.Entry(g, textvariable=self.ara_var, width=22)
        self.ara_giris.pack(side="left", padx=(4, 0))
        self.ara_var.trace_add("write", lambda *a: self.arama_degisti())

        g = ikinci.grup()
        ttk.Label(g, text="Filtre:").pack(side="left")
        self.filtre_var = tk.StringVar(value=FILTRELER[0])
        cb = ttk.Combobox(g, textvariable=self.filtre_var, values=FILTRELER,
                          state="readonly", width=20)
        cb.pack(side="left", padx=(4, 0))
        cb.bind("<<ComboboxSelected>>", lambda e: self.filtre_degisti())

        g = ikinci.grup()
        ttk.Button(g, text="Tümünü Genişlet", command=lambda: self.ac_kapa(True)).pack(side="left", padx=2)
        ttk.Button(g, text="Tümünü Daralt", command=lambda: self.ac_kapa(False)).pack(side="left", padx=2)

        self.ozet_lbl = ttk.Label(ikinci.grup(sag=True), text="0 scraper")
        self.ozet_lbl.pack(side="left")

        # --- Durum çubuğu (en altta)
        self.durum_lbl = ttk.Label(self, text="Hazır", relief="sunken", anchor="w", padding=(6, 2))
        self.durum_lbl.pack(fill="x", side="bottom")

        # --- Alt sekmeler: sabit yükseklik, sürüklenemez
        alt_cerceve = ttk.Frame(self, height=ALT_PANEL_YUKSEKLIK)
        alt_cerceve.pack(fill="x", side="bottom", padx=6, pady=(0, 4))
        alt_cerceve.pack_propagate(False)
        self.defter = ttk.Notebook(alt_cerceve)
        self.defter.pack(fill="both", expand=True)
        self.cikti_txt = self._metin_sekmesi("Çıktı")
        self.detay_txt = self._metin_sekmesi("Detay", font=("Segoe UI", 9))
        self.gunluk_txt = self._metin_sekmesi("Genel Günlük")

        # --- Tablo: kalan alanı doldurur
        agac_cerceve = ttk.Frame(self)
        agac_cerceve.pack(fill="both", expand=True, padx=6, pady=(0, 4))
        self.agac = ttk.Treeview(agac_cerceve, columns=KOLONLAR, selectmode="extended")
        for k in ("#0",) + KOLONLAR:
            self.agac.heading(k, text=BASLIKLAR[k], command=lambda k=k: self.sirala(k))
            self.agac.column(k, width=GENISLIK[k], stretch=k in STRETCH,
                             anchor="e" if k in SAGA_YASLI else "w")
        ys = ttk.Scrollbar(agac_cerceve, orient="vertical", command=self.agac.yview)
        self.agac.configure(yscrollcommand=ys.set)
        self.agac.pack(side="left", fill="both", expand=True)
        ys.pack(side="right", fill="y")

        # Satır renk etiketleri (satırlara tags=("ok",) vb. ile uygulanır)
        self.agac.tag_configure("klasor", font=self.kalin)
        self.agac.tag_configure("ok", foreground="#1a7f37")
        self.agac.tag_configure("hata", foreground="#c62828")
        self.agac.tag_configure("uyari", foreground="#b26a00")
        self.agac.tag_configure("calisiyor", foreground="#0b57d0", background="#e8f0fe")
        self.agac.tag_configure("sirada", foreground="#6a1b9a")
        self.agac.tag_configure("kayip", foreground="#9e9e9e")
        self.agac.tag_configure("yeni", font=self.kalin, background="#fff8d6")

        self.agac.bind("<<TreeviewSelect>>", lambda e: self.secim_degisti())
        self.agac.bind("<Return>", lambda e: self.secilenleri_calistir())
        self.agac.bind("<Double-1>", lambda e: self.cift_tik())
        self.agac.bind("<Button-3>", self._sag_tik)

        # --- Sağ tık menüsü (statik)
        self.sag_menu = tk.Menu(self, tearoff=False)
        m = self.sag_menu
        m.add_command(label="Çalıştır", command=self.secilenleri_calistir)
        m.add_command(label="Durdur", command=self.durdur)
        m.add_command(label="Kontrol et", command=self.kontrol_et)
        m.add_separator()
        m.add_command(label="Argümanları düzenle...", command=self.argumanlari_duzenle)
        m.add_command(label="--help çıktısını göster", command=self.yardim_goster)
        m.add_command(label="Not ekle / düzenle...", command=self.not_duzenle)
        m.add_separator()
        m.add_command(label="Klasörü aç", command=self.klasoru_ac)
        m.add_command(label="Scripti düzenleyicide aç", command=self.scripti_ac)
        m.add_command(label="Son çıktıyı aç", command=self.son_ciktiyi_ac)
        m.add_command(label="Export klasörünü aç", command=self.export_ac)
        m.add_command(label="Son logu aç", command=self.son_logu_ac)
        m.add_command(label="Veri kaynağı.txt aç", command=self.veri_kaynagi_ac)
        m.add_separator()
        m.add_command(label="Eksik paketleri kur (pip)...", command=self.paket_kur)
        m.add_command(label="Kayıttan sil", command=self.kayittan_sil)
        m.add_separator()
        m.add_command(label="Genişlet", command=lambda: self.ac_kapa(True))
        m.add_command(label="Daralt", command=lambda: self.ac_kapa(False))

    def _metin_sekmesi(self, ad, font=("Consolas", 9)):
        cer = ttk.Frame(self.defter)
        txt = tk.Text(cer, wrap="none", font=font, state="disabled", undo=False, height=1)
        ys = ttk.Scrollbar(cer, orient="vertical", command=txt.yview)
        xs = ttk.Scrollbar(cer, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        txt.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        cer.rowconfigure(0, weight=1)
        cer.columnconfigure(0, weight=1)
        txt.tag_configure("hata", foreground="#c62828")
        txt.tag_configure("baslik", font=self.kalin)
        txt.tag_configure("soluk", foreground="#777777")
        self.defter.add(cer, text=ad)
        return txt

    def _sag_tik(self, e):
        iid = self.agac.identify_row(e.y)
        if iid and iid not in self.agac.selection():
            self.agac.selection_set(iid)
            self.agac.focus(iid)
        self.sag_menu.tk_popup(e.x_root, e.y_root)

    # ------------------------------------------------------------- diyaloglar
    def ayarlar_penceresi(self):
        p = tk.Toplevel(self)
        p.title("Ayarlar")
        p.transient(self)
        p.grab_set()
        p.resizable(True, False)
        cer = ttk.Frame(p, padding=12)
        cer.pack(fill="both", expand=True)
        cer.columnconfigure(1, weight=1)
        self.ayar_alanlari = {}
        for r, (etiket, anahtar, varsayilan, gozat, ipucu) in enumerate(AYAR_ALANLARI):
            ttk.Label(cer, text=etiket).grid(row=r * 2, column=0, sticky="w", pady=(6, 0))
            v = tk.StringVar(value=varsayilan)
            ttk.Entry(cer, textvariable=v, width=70).grid(row=r * 2, column=1, sticky="ew",
                                                          padx=6, pady=(6, 0))
            if gozat:
                ttk.Button(cer, text="Gözat...", command=lambda v=v: self.gozat(v)).grid(
                    row=r * 2, column=2, pady=(6, 0))
            ttk.Label(cer, text=ipucu, foreground="#777").grid(row=r * 2 + 1, column=1,
                                                               sticky="w", padx=6)
            self.ayar_alanlari[anahtar] = v
        alt = ttk.Frame(cer)
        alt.grid(row=20, column=0, columnspan=3, sticky="e", pady=(14, 0))
        ttk.Button(alt, text="Kaydet", command=self.ayarlari_kaydet).pack(side="right", padx=4)
        ttk.Button(alt, text="İptal", command=p.destroy).pack(side="right")
        self._ayar_penceresi = p

    def metin_penceresi(self, baslik, metin=""):
        p = tk.Toplevel(self)
        p.title(baslik)
        p.geometry("760x480")
        p.transient(self)
        cer = ttk.Frame(p, padding=6)
        cer.pack(fill="both", expand=True)
        txt = tk.Text(cer, wrap="none", font=("Consolas", 9))
        ys = ttk.Scrollbar(cer, orient="vertical", command=txt.yview)
        xs = ttk.Scrollbar(cer, orient="horizontal", command=txt.xview)
        txt.configure(yscrollcommand=ys.set, xscrollcommand=xs.set)
        txt.grid(row=0, column=0, sticky="nsew")
        ys.grid(row=0, column=1, sticky="ns")
        xs.grid(row=1, column=0, sticky="ew")
        cer.rowconfigure(0, weight=1)
        cer.columnconfigure(0, weight=1)
        txt.insert("1.0", metin)
        txt.configure(state="disabled")
        ttk.Button(p, text="Kapat", command=p.destroy).pack(pady=(0, 8))
        return p

    def giris_penceresi(self, baslik, etiket, onay=None):
        """Tek satırlık giriş diyaloğu (argüman / not düzenleme için)."""
        p = tk.Toplevel(self)
        p.title(baslik)
        p.transient(self)
        p.grab_set()
        p.resizable(True, False)
        cer = ttk.Frame(p, padding=12)
        cer.pack(fill="both", expand=True)
        cer.columnconfigure(0, weight=1)
        ttk.Label(cer, text=etiket).grid(row=0, column=0, sticky="w")
        v = tk.StringVar()
        ttk.Entry(cer, textvariable=v, width=70).grid(row=1, column=0, sticky="ew", pady=(4, 0))
        alt = ttk.Frame(cer)
        alt.grid(row=2, column=0, sticky="e", pady=(12, 0))
        ttk.Button(alt, text="Tamam", command=(lambda: onay(v.get()) if onay else p.destroy())).pack(
            side="right", padx=4)
        ttk.Button(alt, text="İptal", command=p.destroy).pack(side="right")
        return p

    # ============================================================== İŞLEYİCİLER
    # Aşağıdaki metotların hepsi bilinçli olarak boştur; iş mantığını buraya ekleyin.

    # Dosya menüsü
    def yeniden_tara(self): pass
    def kontrol_et(self): pass
    def kok_klasoru_ac(self): pass
    def log_klasoru_ac(self): pass
    def export_ac(self): pass
    def ayarlari_kaydet(self): pass
    def gozat(self, degisken): pass

    # Çalıştır menüsü / araç çubuğu
    def secilenleri_calistir(self): pass
    def gorunenleri_calistir(self): pass
    def tumunu_calistir(self): pass
    def hatalilari_calistir(self): pass
    def durdur(self): pass

    # Modüller
    def modul_klasoru_ac(self): pass

    # Arama / filtre / tablo
    def arama_degisti(self): pass
    def filtre_degisti(self): pass
    def ac_kapa(self, ac): pass
    def sirala(self, kolon): pass
    def secim_degisti(self): pass
    def cift_tik(self): pass

    # Sağ tık menüsü
    def argumanlari_duzenle(self): pass
    def yardim_goster(self): pass
    def not_duzenle(self): pass
    def klasoru_ac(self): pass
    def scripti_ac(self): pass
    def son_ciktiyi_ac(self): pass
    def son_logu_ac(self): pass
    def veri_kaynagi_ac(self): pass
    def paket_kur(self): pass
    def kayittan_sil(self): pass

    # Kapanış
    def kapat(self):
        self.destroy()


if __name__ == "__main__":
    if WIN:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    Uygulama().mainloop()
