import sqlite3

class Database:
    def __init__(self, db_name="kutuphane.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.kurulum_yap()

    def kurulum_yap(self):
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Kitaplar (kitap_no INTEGER PRIMARY KEY, kitap_adi TEXT, durum TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Ogrenciler (id INTEGER PRIMARY KEY AUTOINCREMENT, ad TEXT, soyad TEXT, sinif TEXT, ceza_puani INTEGER DEFAULT 0)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Odunc (id INTEGER PRIMARY KEY AUTOINCREMENT, kitap_no INTEGER, ogrenci_id INTEGER, tarih TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Gecmis (id INTEGER PRIMARY KEY AUTOINCREMENT, ogrenci_id INTEGER, kitap_adi TEXT, tarih TEXT)")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Cezalar (id INTEGER PRIMARY KEY AUTOINCREMENT, ogrenci_id INTEGER, tur TEXT, puan INTEGER, tarih TEXT)")
        self.conn.commit()

    def sorgu(self, sql, params=()):
        self.cursor.execute(sql, params)
        self.conn.commit()
        return self.cursor.fetchall()