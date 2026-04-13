import customtkinter as ctk
from tkinter import ttk, Menu
import sqlite3
import datetime

# --- TASARIM AYARLARI ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

ENTRY_KWARGS = {
    "height": 40, 
    "corner_radius": 10, 
    "fg_color": "#333333", 
    "border_width": 1, 
    "font": ("Arial", 13)
}
BTN_KWARGS = {
    "height": 40, 
    "corner_radius": 10, 
    "font": ("Arial", 14, "bold")
}
CARD_COLOR = "#252526"

class KutuphaneApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("English Cafe - Kütüphane Yönetim Sistemi")
        self.geometry("1150x780")
        self.configure(fg_color="#1e1e1e")
        
        self.veritabani_kur()
        
        # --- SEKMELER ---
        self.tabview = ctk.CTkTabview(
            self, 
            width=1050, 
            height=730, 
            corner_radius=15, 
            fg_color="#1e1e1e", 
            segmented_button_selected_color="#3b82f6"
        )
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.tab_dashboard = self.tabview.add("📊 Dashboard")
        self.tab_odunc_iade = self.tabview.add("🔄 Ödünç & İade")
        self.tab_kitap_liste = self.tabview.add("📚 Kitap Listesi")
        self.tab_ogrenci_liste = self.tabview.add("🎓 Öğrenci Listesi")
        self.tab_kitap_ekle = self.tabview.add("➕ Kitap Ekle")
        
        self.arayuz_kur()
        self.guncelle_her_seyi()

    def veritabani_kur(self):
        self.conn = sqlite3.connect("kafe_kutuphane.db")
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Kitaplar (kitap_no INTEGER PRIMARY KEY, kitap_adi TEXT, durum TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Ogrenciler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, sinif TEXT, ceza_puani INTEGER DEFAULT 0)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Odunc (id INTEGER PRIMARY KEY AUTOINCREMENT, kitap_no INTEGER, ogrenci_id INTEGER, teslim_tarihi TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Cezalar (id INTEGER PRIMARY KEY AUTOINCREMENT, ogrenci_id INTEGER, tur TEXT, detay TEXT, tarih TEXT)''')
        
        self.conn.commit()

    def bildirim_goster(self, baslik, mesaj, tur="basari"):
        if hasattr(self, "aktif_bildirim") and self.aktif_bildirim.winfo_exists():
            self.aktif_bildirim.destroy()

        renk = "#10b981" if tur == "basari" else "#ef4444"
        ikon = "✅" if tur == "basari" else "⚠️"

        bildirim_frame = ctk.CTkFrame(self, fg_color="#2b2b2b", border_width=2, border_color=renk, corner_radius=10)
        bildirim_frame.place(relx=0.97, rely=0.95, anchor="se")
        self.aktif_bildirim = bildirim_frame

        ctk.CTkLabel(bildirim_frame, text=f"{ikon} {baslik}", font=("Arial", 15, "bold"), text_color=renk).pack(padx=20, pady=(15, 2), anchor="w")
        ctk.CTkLabel(bildirim_frame, text=mesaj, font=("Arial", 13), text_color="gray80").pack(padx=20, pady=(0, 15), anchor="w")
        
        self.after(3500, lambda: bildirim_frame.destroy() if bildirim_frame.winfo_exists() else None)

    def kart_olustur(self, parent, ikon, baslik, row, col, vurgu):
        kart = ctk.CTkFrame(parent, corner_radius=20, fg_color=CARD_COLOR, border_width=2, border_color=vurgu, width=300, height=160)
        kart.grid(row=row, column=col, padx=20, pady=20)
        kart.grid_propagate(False)
        
        ctk.CTkLabel(kart, text=ikon, font=("Arial", 36)).pack(pady=(20, 0))
        ctk.CTkLabel(kart, text=baslik, font=("Arial", 16, "bold"), text_color="gray70").pack()
        
        lbl_deger = ctk.CTkLabel(kart, text="0", font=("Arial", 46, "bold"), text_color=vurgu)
        lbl_deger.pack()
        return lbl_deger

    def arayuz_kur(self):
        # ==========================================
        # 1. DASHBOARD
        # ==========================================
        self.dash_frame = ctk.CTkFrame(self.tab_dashboard, fg_color="transparent")
        self.dash_frame.pack(fill="both", expand=True, pady=40)
        self.dash_frame.columnconfigure((0, 1), weight=1)
        
        self.lbl_toplam_kitap = self.kart_olustur(self.dash_frame, "📚", "Toplam Kitap", 0, 0, "#3b82f6")
        self.lbl_oduncte = self.kart_olustur(self.dash_frame, "🔄", "Ödünçteki Kitaplar", 0, 1, "#f59e0b")
        self.lbl_toplam_ogr = self.kart_olustur(self.dash_frame, "🎓", "Kayıtlı Öğrenci", 1, 0, "#10b981")
        self.lbl_geciken = self.kart_olustur(self.dash_frame, "⚠️", "Geciken İadeler", 1, 1, "#ef4444")

        # ==========================================
        # 2. ÖDÜNÇ & İADE EKRANI
        # ==========================================
        oi_container = ctk.CTkFrame(self.tab_odunc_iade, fg_color="transparent")
        oi_container.pack(fill="both", expand=True, padx=40, pady=30)
        oi_container.columnconfigure((0, 1), weight=1)

        # Ödünç Verme Paneli
        odunc_panel = ctk.CTkFrame(oi_container, corner_radius=20, fg_color=CARD_COLOR)
        odunc_panel.grid(row=0, column=0, padx=20, sticky="nsew")
        
        ctk.CTkLabel(odunc_panel, text="📤 Kitap Ödünç Ver", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.ent_odunc_no = ctk.CTkEntry(odunc_panel, placeholder_text="Kitap No", **ENTRY_KWARGS)
        self.ent_odunc_no.pack(pady=5, padx=40, fill="x")
        
        self.ent_ogr_ad = ctk.CTkEntry(odunc_panel, placeholder_text="Öğrenci Adı", **ENTRY_KWARGS)
        self.ent_ogr_ad.pack(pady=5, padx=40, fill="x")
        
        self.ent_ogr_soyad = ctk.CTkEntry(odunc_panel, placeholder_text="Öğrenci Soyadı", **ENTRY_KWARGS)
        self.ent_ogr_soyad.pack(pady=5, padx=40, fill="x")
        
        self.ent_ogr_sinif = ctk.CTkEntry(odunc_panel, placeholder_text="Sınıf", **ENTRY_KWARGS)
        self.ent_ogr_sinif.pack(pady=5, padx=40, fill="x")
        
        ctk.CTkButton(odunc_panel, text="Onayla", command=self.odunc_ver, **BTN_KWARGS).pack(pady=20, padx=40, fill="x")

        # İade Alma Paneli
        iade_panel = ctk.CTkFrame(oi_container, corner_radius=20, fg_color=CARD_COLOR)
        iade_panel.grid(row=0, column=1, padx=20, sticky="nsew")
        
        ctk.CTkLabel(iade_panel, text="📥 İade Al", font=("Arial", 20, "bold")).pack(pady=20)
        
        self.ent_iade_no = ctk.CTkEntry(iade_panel, placeholder_text="Kitap No", **ENTRY_KWARGS)
        self.ent_iade_no.pack(pady=20, padx=40, fill="x")
        
        ctk.CTkButton(iade_panel, text="İadeyi Tamamla", fg_color="#10b981", command=self.iade_al, **BTN_KWARGS).pack(padx=40, fill="x")

        # ==========================================
        # 3. KİTAP VE ÖĞRENCİ LİSTELERİ (TREEVIEW)
        # ==========================================
        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=35, fieldbackground=CARD_COLOR)
        style.map("Treeview", background=[('selected', '#3b82f6')])

        # --- Kitap Listesi ---
        self.ent_arama_kitap = ctk.CTkEntry(self.tab_kitap_liste, placeholder_text="🔍 Kitap Ara...", **ENTRY_KWARGS)
        self.ent_arama_kitap.pack(fill="x", padx=20, pady=10)
        
        self.tree_kitap = ttk.Treeview(self.tab_kitap_liste, columns=("no", "ad", "durum"), show="headings")
        self.tree_kitap.heading("no", text="No")
        self.tree_kitap.heading("ad", text="Kitap Adı")
        self.tree_kitap.heading("durum", text="Durum")
        self.tree_kitap.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Sağ Tık Menüsü Ayarı
        self.sag_tik_menu = Menu(self, tearoff=0)
        self.sag_tik_menu.add_command(label="🗑️ Kitabı Sil", command=self.kitap_sil_sagtik)
        self.tree_kitap.bind("<Button-3>", self.sag_tik_goster)

        # --- Öğrenci Listesi ---
        self.ent_arama_ogr = ctk.CTkEntry(self.tab_ogrenci_liste, placeholder_text="🔍 Öğrenci Ara...", **ENTRY_KWARGS)
        self.ent_arama_ogr.pack(fill="x", padx=20, pady=10)
        
        self.tree_ogrenci = ttk.Treeview(self.tab_ogrenci_liste, columns=("id", "ad", "soyad", "sinif", "ceza"), show="headings")
        self.tree_ogrenci.heading("id", text="ID")
        self.tree_ogrenci.heading("ad", text="Ad")
        self.tree_ogrenci.heading("soyad", text="Soyad")
        self.tree_ogrenci.heading("sinif", text="Sınıf")
        self.tree_ogrenci.heading("ceza", text="Ceza Puanı")
        self.tree_ogrenci.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Çift tıklama ile profil açma
        self.tree_ogrenci.bind("<Double-1>", self.kimlik_karti_ac)

        # ==========================================
        # 4. KİTAP EKLEME EKRANI
        # ==========================================
        ekle_frame = ctk.CTkFrame(self.tab_kitap_ekle, corner_radius=20, fg_color=CARD_COLOR)
        ekle_frame.pack(pady=100, padx=100)
        
        self.ent_yeni_k_no = ctk.CTkEntry(ekle_frame, placeholder_text="Kitap No", width=300, **ENTRY_KWARGS)
        self.ent_yeni_k_no.pack(pady=10, padx=40)
        
        self.ent_yeni_k_adi = ctk.CTkEntry(ekle_frame, placeholder_text="Kitap Adı", width=300, **ENTRY_KWARGS)
        self.ent_yeni_k_adi.pack(pady=10, padx=40)
        
        ctk.CTkButton(ekle_frame, text="Kitabı Kaydet", command=self.kitap_ekle, **BTN_KWARGS).pack(pady=20)


    # ==========================================
    # FONKSİYONLAR VE MANTIK
    # ==========================================

    def sag_tik_goster(self, event):
        item = self.tree_kitap.identify_row(event.y)
        if item:
            self.tree_kitap.selection_set(item)
            self.sag_tik_menu.post(event.x_root, event.y_root)

    def kitap_sil_sagtik(self):
        secili = self.tree_kitap.selection()
        if secili:
            k_no = self.tree_kitap.item(secili)["values"][0]
            self.cursor.execute("DELETE FROM Kitaplar WHERE kitap_no=?", (k_no,))
            self.conn.commit()
            self.guncelle_her_seyi()
            self.bildirim_goster("Silindi", "Kitap sistemden kaldırıldı.")

    def kimlik_karti_ac(self, event):
        secili = self.tree_ogrenci.selection()
        if not secili: 
            return
            
        ogr_id, ad, soyad, sinif, ceza = self.tree_ogrenci.item(secili)["values"]

        profil = ctk.CTkToplevel(self)
        profil.title(f"Öğrenci Profili: {ad} {soyad}")
        profil.geometry("600x400")
        
        # Linux için kritik düzeltme: Pencere oluşana kadar bekle
        profil.wait_visibility() 
        profil.grab_set()

        ctk.CTkLabel(profil, text=f"👤 {ad} {soyad}", font=("Arial", 22, "bold")).pack(pady=20)
        ctk.CTkLabel(profil, text=f"Sınıf: {sinif} | Ceza Puanı: {ceza}", font=("Arial", 16)).pack()
        
        txt_gecmis = ctk.CTkTextbox(profil, width=500, height=200, font=("Arial", 14))
        txt_gecmis.pack(pady=20)
        
        self.cursor.execute("SELECT tur, detay FROM Cezalar WHERE ogrenci_id=?", (ogr_id,))
        kayitlar = self.cursor.fetchall()
        
        if not kayitlar:
            txt_gecmis.insert("end", "Öğrencinin herhangi bir ceza kaydı bulunmamaktadır.")
        else:
            for tur, detay in kayitlar:
                txt_gecmis.insert("end", f"• {tur}: {detay}\n")
                
        txt_gecmis.configure(state="disabled")

    def odunc_ver(self):
        k_no = self.ent_odunc_no.get()
        ad = self.ent_ogr_ad.get()
        soyad = self.ent_ogr_soyad.get()
        sinif = self.ent_ogr_sinif.get()
        
        if not all([k_no, ad, soyad, sinif]): 
            self.bildirim_goster("Hata", "Lütfen tüm alanları doldurun.", "hata")
            return
        
        self.cursor.execute("SELECT durum FROM Kitaplar WHERE kitap_no=?", (k_no,))
        kitap = self.cursor.fetchone()
        
        if kitap and kitap[0] == "Rafta":
            # Öğrenci var mı kontrol et, yoksa ekle
            self.cursor.execute("SELECT id FROM Ogrenciler WHERE ad=? AND soyad=?", (ad, soyad))
            ogrenci = self.cursor.fetchone()
            
            if ogrenci:
                oid = ogrenci[0]
            else:
                self.cursor.execute("INSERT INTO Ogrenciler (ad, soyad, sinif) VALUES (?,?,?)", (ad, soyad, sinif))
                oid = self.cursor.lastrowid
            
            # Ödünç işlemini kaydet
            tarih = (datetime.date.today() + datetime.timedelta(days=15)).strftime("%Y-%m-%d")
            self.cursor.execute("INSERT INTO Odunc (kitap_no, ogrenci_id, teslim_tarihi) VALUES (?,?,?)", (k_no, oid, tarih))
            self.cursor.execute("UPDATE Kitaplar SET durum=? WHERE kitap_no=?", (f"{ad} {soyad} (İade: {tarih})", k_no))
            self.conn.commit()
            
            self.guncelle_her_seyi()
            self.ent_odunc_no.delete(0, "end"); self.ent_ogr_ad.delete(0, "end")
            self.ent_ogr_soyad.delete(0, "end"); self.ent_ogr_sinif.delete(0, "end")
            self.bildirim_goster("Başarılı", "Kitap öğrenciye verildi.")
        else:
            self.bildirim_goster("Hata", "Kitap bulunamadı veya rafta değil.", "hata")

    def iade_al(self):
        k_no = self.ent_iade_no.get()
        
        if not k_no:
            return
            
        self.cursor.execute("UPDATE Kitaplar SET durum='Rafta' WHERE kitap_no=?", (k_no,))
        self.cursor.execute("DELETE FROM Odunc WHERE kitap_no=?", (k_no,))
        self.conn.commit()
        
        self.guncelle_her_seyi()
        self.ent_iade_no.delete(0, "end")
        self.bildirim_goster("İade Alındı", "Kitap tekrar rafa yerleştirildi.")

    def kitap_ekle(self):
        k_no = self.ent_yeni_k_no.get()
        k_adi = self.ent_yeni_k_adi.get()
        
        if not k_no or not k_adi:
            self.bildirim_goster("Hata", "Lütfen tüm alanları doldurun.", "hata")
            return
            
        try:
            self.cursor.execute("INSERT INTO Kitaplar VALUES (?, ?, 'Rafta')", (k_no, k_adi))
            self.conn.commit()
            self.guncelle_her_seyi()
            self.ent_yeni_k_no.delete(0, "end")
            self.ent_yeni_k_adi.delete(0, "end")
            self.bildirim_goster("Eklendi", "Yeni kitap sisteme kaydedildi.")
        except sqlite3.IntegrityError: 
            self.bildirim_goster("Hata", "Bu kitap numarası zaten kullanımda.", "hata")

    def guncelle_her_seyi(self):
        # Treeview'leri temizle
        for item in self.tree_kitap.get_children(): self.tree_kitap.delete(item)
        for item in self.tree_ogrenci.get_children(): self.tree_ogrenci.delete(item)
            
        # Kitapları yükle
        self.cursor.execute("SELECT * FROM Kitaplar")
        for row in self.cursor.fetchall(): 
            self.tree_kitap.insert("", "end", values=row)
        
        # Öğrencileri yükle
        self.cursor.execute("SELECT id, ad, soyad, sinif, ceza_puani FROM Ogrenciler")
        for row in self.cursor.fetchall(): 
            self.tree_ogrenci.insert("", "end", values=row)

        # Dashboard İstatistiklerini Güncelle
        self.cursor.execute("SELECT COUNT(*) FROM Kitaplar")
        self.lbl_toplam_kitap.configure(text=str(self.cursor.fetchone()[0]))
        
        self.cursor.execute("SELECT COUNT(*) FROM Kitaplar WHERE durum!='Rafta'")
        self.lbl_oduncte.configure(text=str(self.cursor.fetchone()[0]))
        
        self.cursor.execute("SELECT COUNT(*) FROM Ogrenciler")
        self.lbl_toplam_ogr.configure(text=str(self.cursor.fetchone()[0]))


if __name__ == "__main__":
    app = KutuphaneApp()
    app.mainloop()