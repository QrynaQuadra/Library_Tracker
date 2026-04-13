import customtkinter as ctk
from tkinter import ttk, Menu
import datetime
from database import Database
from ui_components import UI

class KutuphaneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.title("English Cafe - Kütüphane Yönetim Sistemi")
        self.geometry("1150x800")
        
        # Tema ve Sekme Yapısı
        ctk.set_appearance_mode("Dark")
        self.tabview = ctk.CTkTabview(self, width=1100, height=750, corner_radius=15)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_dash = self.tabview.add("📊 Dashboard")
        self.tab_islem = self.tabview.add("🔄 Ödünç & İade")
        self.tab_kitaplar = self.tabview.add("📚 Kitap Listesi")
        self.tab_ogrenciler = self.tabview.add("🎓 Öğrenci Listesi")
        self.tab_ekle = self.tabview.add("➕ Kitap Ekle")

        self.arayuz_yukle()
        self.verileri_tazele()

    def arayuz_yukle(self):
        # --- 1. DASHBOARD ---
        self.dash_container = ctk.CTkFrame(self.tab_dash, fg_color="transparent")
        self.dash_container.pack(expand=True, pady=20)
        
        self.lbl_t_kitap = UI.kart_yap(self.dash_container, "Toplam Kitap", 0, 0, "#3b82f6")
        self.lbl_t_odunc = UI.kart_yap(self.dash_container, "Ödünçtekiler", 0, 1, "#f59e0b")
        self.lbl_t_ogr = UI.kart_yap(self.dash_container, "Öğrenci Sayısı", 1, 0, "#10b981")

        # --- 2. ÖDÜNÇ & İADE ---
        p = ctk.CTkFrame(self.tab_islem, fg_color="#252526", corner_radius=20)
        p.pack(pady=40, padx=50, fill="both", expand=True)
        
        ctk.CTkLabel(p, text="Kitap Ödünç / İade İşlemi", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.e_kno = ctk.CTkEntry(p, placeholder_text="Kitap Numarasını Giriniz...", height=45, font=("Arial", 14))
        self.e_kno.pack(pady=10, padx=150, fill="x")
        
        self.e_ad = ctk.CTkEntry(p, placeholder_text="Öğrenci Adı...", height=45, font=("Arial", 14))
        self.e_ad.pack(pady=10, padx=150, fill="x")
        
        self.e_soy = ctk.CTkEntry(p, placeholder_text="Öğrenci Soyadı...", height=45, font=("Arial", 14))
        self.e_soy.pack(pady=10, padx=150, fill="x")
        
        btn_f = ctk.CTkFrame(p, fg_color="transparent")
        btn_f.pack(pady=30)
        
        ctk.CTkButton(btn_f, text="📤 Ödünç Ver", command=self.odunc_ver, fg_color="#3b82f6", height=45, width=150, font=("Arial", 14, "bold")).grid(row=0, column=0, padx=20)
        ctk.CTkButton(btn_f, text="📥 İade Al", command=self.iade_al, fg_color="#10b981", height=45, width=150, font=("Arial", 14, "bold")).grid(row=0, column=1, padx=20)

        # --- 3. KİTAP LİSTESİ ---
        self.tree_k = ttk.Treeview(self.tab_kitaplar, columns=("no", "ad", "durum"), show="headings")
        for c in ("no", "ad", "durum"): 
            self.tree_k.heading(c, text=c.upper())
            self.tree_k.column(c, anchor="center")
        self.tree_k.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.m_sag = Menu(self, tearoff=0)
        self.m_sag.add_command(label="🗑️ Seçili Kitabı Sil", command=self.kitap_sil)
        self.tree_k.bind("<Button-3>", self.sag_tik_goster)

        # --- 4. ÖĞRENCİ LİSTESİ ---
        self.tree_o = ttk.Treeview(self.tab_ogrenciler, columns=("id", "ad", "soyad", "ceza"), show="headings")
        for c in ("id", "ad", "soyad", "ceza"): 
            self.tree_o.heading(c, text=c.upper())
            self.tree_o.column(c, anchor="center")
        self.tree_o.pack(fill="both", expand=True, padx=20, pady=20)
        self.tree_o.bind("<Double-1>", self.kimlik_karti_ac)

        # --- 5. KİTAP EKLE ---
        ekle_p = ctk.CTkFrame(self.tab_ekle, fg_color="#252526", corner_radius=20)
        ekle_p.pack(pady=60, padx=100, fill="both")
        
        ctk.CTkLabel(ekle_p, text="Sisteme Yeni Kitap Tanımla", font=("Arial", 20, "bold")).pack(pady=20)
        self.e_yeni_no = ctk.CTkEntry(ekle_p, placeholder_text="Kitap Barkod / No", height=45)
        self.e_yeni_no.pack(pady=10, padx=100, fill="x")
        self.e_yeni_ad = ctk.CTkEntry(ekle_p, placeholder_text="Kitap Tam Adı", height=45)
        self.e_yeni_ad.pack(pady=10, padx=100, fill="x")
        
        ctk.CTkButton(ekle_p, text="💾 Veritabanına Kaydet", command=self.kitap_ekle, height=50, font=("Arial", 14, "bold")).pack(pady=30)

    # --- FONKSİYONLAR (Aynı Mantık) ---
    def sag_tik_goster(self, e):
        row = self.tree_k.identify_row(e.y)
        if row:
            self.tree_k.selection_set(row)
            self.m_sag.post(e.x_root, e.y_root)

    def odunc_ver(self):
        kno, ad, soy = self.e_kno.get(), self.e_ad.get(), self.e_soy.get()
        if not kno or not ad: return
        kitap = self.db.sorgu("SELECT durum, kitap_adi FROM Kitaplar WHERE kitap_no=?", (kno,))
        
        if kitap and kitap[0][0] == "Rafta":
            ogr = self.db.sorgu("SELECT id FROM Ogrenciler WHERE ad=? AND soyad=?", (ad, soy))
            if ogr: oid = ogr[0][0]
            else:
                self.db.sorgu("INSERT INTO Ogrenciler (ad, soyad) VALUES (?,?)", (ad, soy))
                oid = self.db.cursor.lastrowid
            
            tarih = datetime.date.today().isoformat()
            self.db.sorgu("INSERT INTO Odunc (kitap_no, ogrenci_id, tarih) VALUES (?,?,?)", (kno, oid, tarih))
            self.db.sorgu("INSERT INTO Gecmis (ogrenci_id, kitap_adi, tarih) VALUES (?,?,?)", (oid, kitap[0][1], tarih))
            self.db.sorgu("UPDATE Kitaplar SET durum=? WHERE kitap_no=?", (f"{ad} {soy}", kno))
            self.verileri_tazele()
            UI.bildirim(self, f"Başarılı: {kitap[0][1]} verildi.")
        else:
            UI.bildirim(self, "Hata: Kitap müsait değil!", "hata")

    def iade_al(self):
        kno = self.e_kno.get()
        self.db.sorgu("UPDATE Kitaplar SET durum='Rafta' WHERE kitap_no=?", (kno,))
        self.db.sorgu("DELETE FROM Odunc WHERE kitap_no=?", (kno,))
        self.verileri_tazele()
        UI.bildirim(self, "Kitap iade alındı.")

    def kitap_ekle(self):
        try:
            self.db.sorgu("INSERT INTO Kitaplar VALUES (?, ?, 'Rafta')", (self.e_yeni_no.get(), self.e_yeni_ad.get()))
            self.verileri_tazele()
            UI.bildirim(self, "Yeni kitap kaydedildi.")
        except:
            UI.bildirim(self, "Hata: Bu numara zaten kayıtlı!", "hata")

    def kitap_sil(self):
        secili = self.tree_k.selection()
        if secili:
            self.db.sorgu("DELETE FROM Kitaplar WHERE kitap_no=?", (self.tree_k.item(secili)["values"][0],))
            self.verileri_tazele()

    def kimlik_karti_ac(self, event):
        item = self.tree_o.selection()
        if not item: return
        oid, ad, soy, ceza = self.tree_o.item(item)["values"]
        
        profil = ctk.CTkToplevel(self)
        profil.title(f"Öğrenci Profili: {ad} {soy}")
        profil.geometry("600x650")
        profil.wait_visibility()
        profil.grab_set()

        ctk.CTkLabel(profil, text=f"👤 {ad} {soy}", font=("Arial", 22, "bold")).pack(pady=20)
        
        ctk.CTkLabel(profil, text="📚 Okuma Geçmişi (Tüm Zamanlar)", font=("Arial", 14, "bold")).pack()
        box = ctk.CTkTextbox(profil, width=520, height=220, font=("Consolas", 12))
        box.pack(pady=10)
        
        gecmis = self.db.sorgu("SELECT kitap_adi, tarih FROM Gecmis WHERE ogrenci_id=?", (oid,))
        for k, t in gecmis: box.insert("end", f" • {t} | {k}\n")
        box.configure(state="disabled")

        # Ceza Paneli
        c_f = ctk.CTkFrame(profil, fg_color="#333333")
        c_f.pack(pady=20, padx=40, fill="x")
        ctk.CTkLabel(c_f, text="⚠️ Ceza Puanı Ekle", font=("Arial", 14)).pack(pady=5)
        e_p = ctk.CTkEntry(c_f, placeholder_text="Puan (Örn: 5)", width=150)
        e_p.pack(pady=5)
        
        def ceza_kes():
            if e_p.get():
                self.db.sorgu("UPDATE Ogrenciler SET ceza_puani = ceza_puani + ? WHERE id=?", (int(e_p.get()), oid))
                self.verileri_tazele()
                profil.destroy()
                UI.bildirim(self, "Ceza güncellendi.")

        ctk.CTkButton(c_f, text="Cezayı Onayla", fg_color="#ef4444", command=ceza_kes).pack(pady=10)

    def verileri_tazele(self):
        for t in (self.tree_k, self.tree_o):
            for i in t.get_children(): t.delete(i)
        
        for r in self.db.sorgu("SELECT * FROM Kitaplar"): self.tree_k.insert("", "end", values=r)
        for r in self.db.sorgu("SELECT id, ad, soyad, ceza_puani FROM Ogrenciler"): self.tree_o.insert("", "end", values=r)

        tk = self.db.sorgu("SELECT COUNT(*) FROM Kitaplar")[0][0]
        ok = self.db.sorgu("SELECT COUNT(*) FROM Kitaplar WHERE durum!='Rafta'")[0][0]
        to = self.db.sorgu("SELECT COUNT(*) FROM Ogrenciler")[0][0]
        
        self.lbl_t_kitap.configure(text=str(tk))
        self.lbl_t_odunc.configure(text=str(ok))
        self.lbl_t_ogr.configure(text=str(to))