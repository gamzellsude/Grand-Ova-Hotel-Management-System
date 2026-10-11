import customtkinter as ctk
from tkinter import messagebox
import sqlite3
import re
from datetime import datetime
import hashlib

# ==========================================
# 1. TEMA VE RENK PALETİ (FIGMA BİREBİR)
# ==========================================
ctk.set_appearance_mode("dark")
C_BG = "#131315"
C_SIDEBAR = "#1a1a1d"
C_CARD = "#212124"
C_GOLD = "#e8c37b"
C_GREEN = "#4cd964"
C_RED = "#ff3b30"
C_TEXT = "#ffffff"
C_TEXT_GRI = "#8e8e93"

RENK_TEK = "#4fc3f7"   # Mavi
RENK_CIFT = "#e066ff"  # Mor/Pembe
RENK_DUBLE = "#ffd54f" # Sarı

# Global Widget Referansları
lbl_ust_musait = None
lbl_ust_dolu = None
lbl_ust_ciro = None
oda_widgetleri = {}

# ==========================================
# GÜVENLİK: ŞİFRE HASHLEME FONKSİYONU
# ==========================================
def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode('utf-8')).hexdigest()

# ==========================================
# 2. VERİTABANI BAĞLANTISI VE HATA YÖNETİMİ
# ==========================================
def veritabani_kur():
    try:
        conn = sqlite3.connect('otel_veritabani.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS odalar (oda_no INTEGER PRIMARY KEY, durum TEXT, tip TEXT, ozellikler TEXT, isim TEXT, tc TEXT, ucret REAL, gun INTEGER, giris_tarihi TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS raporlar (id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT, oda_no INTEGER, odeme_turu TEXT, tutar REAL, islem_tarihi TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS gecmis_raporlar (id INTEGER PRIMARY KEY AUTOINCREMENT, isim TEXT, oda_no INTEGER, odeme_turu TEXT, tutar REAL, islem_tarihi TEXT, gun_sonu_tarihi TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS ayarlar (anahtar TEXT PRIMARY KEY, deger TEXT)''')
        
        c.execute("SELECT deger FROM ayarlar WHERE anahtar='sifre'")
        if not c.fetchone():
            c.execute("INSERT INTO ayarlar VALUES ('sifre', '')")
        
        c.execute("SELECT COUNT(*) FROM odalar")
        if c.fetchone()[0] == 0:
            for kat in range(1, 6):
                for o in range(1, 12):
                    no = kat * 100 + o
                    # Tabloya göre oda tiplerinin ayarlanması (111 numaralı oda Çift Kişilik)
                    if o in [1, 2]: 
                        tip, oz = "TEK KİŞİLİK", "1 Tek Yatak, TV, Wi-Fi"
                    elif o in [4, 9] or (kat == 1 and o == 11): 
                        tip, oz = "ÇİFT KİŞİLİK", "1 Çift Yatak, Klima, TV, Balkon"
                    else: 
                        tip, oz = "DUBLE", "1 Çift+1 Tek Yatak, Jakuzi, Manzara"
                    c.execute("INSERT INTO odalar VALUES (?, 'Müsait', ?, ?, '', '', 0, 0, '')", (no, tip, oz))
        conn.commit()
    except sqlite3.Error as e:
        messagebox.showerror("Kritik Hata", f"Veritabanı oluşturulamadı!\nHata: {e}")
    finally:
        if conn: conn.close()

def db_oku(sorgu, parametreler=()):
    try:
        conn = sqlite3.connect('otel_veritabani.db')
        c = conn.cursor()
        c.execute(sorgu, parametreler)
        veri = c.fetchall()
        return veri
    except sqlite3.Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Veri okuma hatası!\nHata: {e}")
        return []
    finally:
        if conn: conn.close()

def db_yaz(sorgu, parametreler=()):
    try:
        conn = sqlite3.connect('otel_veritabani.db')
        c = conn.cursor()
        c.execute(sorgu, parametreler)
        conn.commit()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Veritabanı Hatası", f"Veri yazma hatası!\nHata: {e}")
        return False
    finally:
        if conn: conn.close()

# Veri Doğrulama Fonksiyonları
def sadece_sayi_mi(deger): return deger.isdigit()
def gecerli_ucret_mi(deger): 
    try:
        float(deger)
        return True
    except ValueError:
        return False
def gecerli_isim_mi(deger): return bool(re.match("^[a-zA-ZğüşıöçĞÜŞİÖÇ ]+$", deger))
def gecerli_tc_pasaport_mu(deger): return deger.isalnum() and len(deger) >= 5 

# ==========================================
# 3. GİRİŞ EKRANI
# ==========================================
def giris_ekrani():
    veritabani_kur()
    res = db_oku("SELECT deger FROM ayarlar WHERE anahtar='sifre'")
    mevcut_sifre_hash = res[0][0] if res else ""
    ilk_kurulum = (mevcut_sifre_hash == "")

    login_app = ctk.CTk()
    login_app.title("Sisteme Giriş")
    login_app.geometry("450x550")
    login_app.configure(fg_color=C_BG)
    login_app.eval('tk::PlaceWindow . center')

    ctk.CTkLabel(login_app, text="GRAND OVA HOTEL", font=("Arial", 26, "bold"), text_color=C_GOLD).pack(pady=(60, 5))
    ctk.CTkLabel(login_app, text="Lütfen yeni 4 haneli şifre belirleyin." if ilk_kurulum else "Yönetim Sistemi Girişi", font=("Arial", 14), text_color=C_TEXT_GRI).pack(pady=(0, 40))

    sifre_var = ctk.StringVar()
    def sifre_kisitla(*args):
        deger = sifre_var.get()
        if not deger.isdigit(): sifre_var.set(''.join(filter(str.isdigit, deger)))
        if len(sifre_var.get()) > 4: sifre_var.set(sifre_var.get()[:4])
    sifre_var.trace_add('write', sifre_kisitla) 

    ctk.CTkEntry(login_app, textvariable=sifre_var, show="*", placeholder_text="4 Haneli Şifre", width=250, height=50, font=("Arial", 20, "bold"), justify="center").pack(pady=20)

    def islem_yap():
        girilen = sifre_var.get()
        if len(girilen) != 4:
            messagebox.showwarning("Uyarı", "Şifre 4 haneli rakam olmalıdır!", parent=login_app)
            return

        girilen_hash = sifre_hashle(girilen)

        if ilk_kurulum:
            if db_yaz("UPDATE ayarlar SET deger=? WHERE anahtar='sifre'", (girilen_hash,)):
                login_app.destroy()
                ana_uygulamayi_baslat()
        else:
            if girilen_hash == mevcut_sifre_hash:
                login_app.destroy()
                ana_uygulamayi_baslat()
            else:
                messagebox.showerror("Hata", "Hatalı Şifre!", parent=login_app)

    ctk.CTkButton(login_app, text="ŞİFREYİ KAYDET" if ilk_kurulum else "GİRİŞ YAP", font=("Arial", 14, "bold"), fg_color=C_GOLD, text_color="black", width=250, height=50, command=islem_yap).pack(pady=10)
    login_app.mainloop()

# ==========================================
# 4. ANA UYGULAMA
# ==========================================
def ana_uygulamayi_baslat():
    global lbl_ust_musait, lbl_ust_dolu, lbl_ust_ciro, oda_widgetleri
    app = ctk.CTk()
    app.title("GRAND OVA HOTEL - Yönetim Masası")
    app.state('zoomed')
    app.configure(fg_color=C_BG)

    FONT_BASLIK = ctk.CTkFont(family="Arial", size=20, weight="bold")
    tarih_bugun = datetime.now().strftime("%d.%m.%Y")

    def panoyu_yenile():
        odalar_verisi = db_oku("SELECT oda_no, durum, tip FROM odalar")
        if not odalar_verisi: return 
        
        dolu_sayisi = sum(1 for o in odalar_verisi if o[1] == "Dolu")
        
        if lbl_ust_musait: lbl_ust_musait.configure(text=str(55 - dolu_sayisi))
        if lbl_ust_dolu: lbl_ust_dolu.configure(text=str(dolu_sayisi))
        
        ciro_sorgu = db_oku("SELECT SUM(ucret * gun) FROM odalar WHERE durum='Dolu'")
        aktif_ciro = ciro_sorgu[0][0] if (ciro_sorgu and ciro_sorgu[0][0]) else 0
        if lbl_ust_ciro: lbl_ust_ciro.configure(text=f"₺ {aktif_ciro:,.0f}")

        for oda in odalar_verisi:
            no, durum, tip = oda
            if no in oda_widgetleri:
                w = oda_widgetleri[no]
                if durum == "Müsait":
                    w["kart"].configure(fg_color=C_CARD, border_width=0)
                    w["lbl_durum"].configure(text="Müsait", text_color=C_TEXT_GRI)
                    w["btn"].configure(text="GİRİŞ", fg_color="transparent", border_color=C_GOLD, text_color=C_GOLD, hover_color="#333")
                else:
                    w["kart"].configure(fg_color="#2a1a1a", border_width=1, border_color=C_RED)
                    w["lbl_durum"].configure(text="Dolu", text_color=C_RED)
                    w["btn"].configure(text="ÇIKIŞ", fg_color=C_RED, border_color=C_RED, text_color=C_TEXT, hover_color="#8b0000")

    def sifre_degistir_penceresi():
        mevcut_sifre_hash = db_oku("SELECT deger FROM ayarlar WHERE anahtar='sifre'")[0][0]
        p = ctk.CTkToplevel(app)
        p.title("Şifre Değiştir"); p.geometry("400x400"); p.configure(fg_color=C_BG); p.grab_set(); p.attributes('-topmost', True)
        ctk.CTkLabel(p, text="Şifre Değiştir", font=FONT_BASLIK, text_color=C_GOLD).pack(pady=(20, 20))
        eski_sifre = ctk.CTkEntry(p, placeholder_text="Mevcut Şifreniz", show="*", width=250, height=40)
        eski_sifre.pack(pady=10)
        yeni_sifre = ctk.CTkEntry(p, placeholder_text="Yeni 4 Haneli Şifre", show="*", width=250, height=40)
        yeni_sifre.pack(pady=10)

        def kaydet():
            if sifre_hashle(eski_sifre.get()) != mevcut_sifre_hash: 
                messagebox.showerror("Hata", "Mevcut şifre yanlış!", parent=p); return
            if len(yeni_sifre.get()) != 4 or not yeni_sifre.get().isdigit(): 
                messagebox.showwarning("Uyarı", "Yeni şifre 4 haneli rakam olmalıdır!", parent=p); return
            
            if db_yaz("UPDATE ayarlar SET deger=? WHERE anahtar='sifre'", (sifre_hashle(yeni_sifre.get()),)):
                messagebox.showinfo("Başarılı", "Şifreniz güncellendi.", parent=p)
                p.destroy()
                
        ctk.CTkButton(p, text="GÜNCELLE", fg_color=C_GOLD, text_color="black", font=("Arial", 12, "bold"), width=250, height=40, command=kaydet).pack(pady=20)

    def giris_penceresi(no, tip, ozellikler):
        p = ctk.CTkToplevel(app)
        p.title(f"Giriş - Oda {no}"); p.geometry("450x700"); p.configure(fg_color=C_BG); p.attributes('-topmost', True); p.grab_set()
        ctk.CTkLabel(p, text="Giriş İşlemi", font=FONT_BASLIK, text_color=C_GOLD).pack(pady=(20, 5))
        ctk.CTkLabel(p, text=f"Oda {no} • {tip}", font=("Arial", 14, "bold"), text_color=C_TEXT).pack()
        
        kutu = ctk.CTkFrame(p, fg_color=C_CARD, corner_radius=10); kutu.pack(fill="x", padx=40, pady=10, ipady=5)
        ctk.CTkLabel(kutu, text="🟢 ŞU AN MÜSAİT", text_color=C_GREEN, font=("Arial", 11, "bold")).pack(pady=(15,0))

        isim_e = ctk.CTkEntry(p, placeholder_text="Misafirin adı...", width=350, height=40, fg_color=C_CARD)
        tc_e = ctk.CTkEntry(p, placeholder_text="TC/Pasaport No...", width=350, height=40, fg_color=C_CARD)
        ucret_e = ctk.CTkEntry(p, placeholder_text="0.00", width=350, height=40, fg_color=C_CARD)
        gun_e = ctk.CTkEntry(p, placeholder_text="0", width=350, height=40, fg_color=C_CARD)
        tarih_e = ctk.CTkEntry(p, width=350, height=40, fg_color=C_CARD); tarih_e.insert(0, tarih_bugun)

        for baslik, entry in [("İSİM SOYİSİM", isim_e), ("TC / PASAPORT NO", tc_e), ("ÜCRET - GECELİK (₺)", ucret_e), ("GÜN SAYISI", gun_e), ("GİRİŞ TARİHİ", tarih_e)]:
            ctk.CTkLabel(p, text=baslik, text_color=C_TEXT_GRI, font=("Arial", 10, "bold")).pack(anchor="w", padx=50, pady=(5, 2))
            entry.pack()

        def kaydet():
            isim, tc, ucret, gun = isim_e.get().strip(), tc_e.get().strip(), ucret_e.get().strip(), gun_e.get().strip()
            
            if not gecerli_isim_mi(isim):
                messagebox.showerror("Hata", "Geçerli bir isim giriniz!", parent=p); return
            if not gecerli_tc_pasaport_mu(tc):
                messagebox.showerror("Hata", "Geçerli bir TC/Pasaport No giriniz!", parent=p); return
            if not gecerli_ucret_mi(ucret):
                messagebox.showerror("Hata", "Ücret geçerli bir sayı olmalıdır!", parent=p); return
            if not sadece_sayi_mi(gun) or int(gun) <= 0:
                messagebox.showerror("Hata", "Gün sayısı pozitif tam sayı olmalıdır!", parent=p); return

            if db_yaz("UPDATE odalar SET durum='Dolu', isim=?, tc=?, ucret=?, gun=?, giris_tarihi=? WHERE oda_no=?", (isim.upper(), tc, float(ucret), int(gun), tarih_e.get(), no)):
                p.destroy(); panoyu_yenile()

        f = ctk.CTkFrame(p, fg_color="transparent"); f.pack(fill="x", padx=50, pady=20)
        ctk.CTkButton(f, text="İptal", fg_color="transparent", border_width=1, border_color=C_TEXT_GRI, command=p.destroy, width=150).pack(side="left")
        ctk.CTkButton(f, text="GİRİŞ", fg_color=C_GOLD, text_color="black", command=kaydet, width=150).pack(side="right")

    def cikis_penceresi(no, isim, ucret, gun, ozellikler):
        try:
            tutar = float(ucret) * int(gun)
        except (ValueError, TypeError):
            tutar = 0.0

        p = ctk.CTkToplevel(app); p.title(f"Çıkış - Oda {no}"); p.geometry("450x500"); p.configure(fg_color=C_BG); p.attributes('-topmost', True); p.grab_set()
        ctk.CTkLabel(p, text="Çıkış İşlemi", font=FONT_BASLIK, text_color=C_GOLD).pack(pady=(20, 5))
        ctk.CTkLabel(p, text=f"Misafir: {isim} • Oda {no}", text_color=C_TEXT_GRI).pack()
        kutu = ctk.CTkFrame(p, fg_color=C_CARD, corner_radius=10); kutu.pack(fill="x", padx=40, pady=10, ipady=5)
        ctk.CTkLabel(kutu, text="🔴 ŞU AN DOLU", text_color=C_RED, font=("Arial", 11, "bold")).pack(pady=(5,0))
        ctk.CTkLabel(p, text=f"Tahsil Edilecek Tutar:\n₺{tutar:,.2f}", font=("Arial", 20, "bold"), text_color=C_TEXT).pack(pady=10)

        def odeme_al(yontem):
            tarih = datetime.now().strftime("%d.%m.%Y %H:%M")
            if db_yaz("INSERT INTO raporlar (isim, oda_no, odeme_turu, tutar, islem_tarihi) VALUES (?, ?, ?, ?, ?)", (isim, no, yontem, tutar, tarih)):
                db_yaz("UPDATE odalar SET durum='Müsait', isim='', tc='', ucret=0, gun=0, giris_tarihi='' WHERE oda_no=?", (no,))
                p.destroy(); panoyu_yenile()
                if sayfa_raporlar.winfo_ismapped(): rapor_sayfasini_guncelle()
                messagebox.showinfo("Başarılı", f"{yontem} ile ödeme alındı.")

        yontemler = ctk.CTkFrame(p, fg_color="transparent"); yontemler.pack(pady=10)
        for y in ["Nakit", "Kredi Kartı", "Havale"]:
            ctk.CTkButton(yontemler, text=y, fg_color=C_CARD, width=100, height=45, command=lambda yntm=y: odeme_al(yntm)).pack(side="left", padx=5)

    def odaya_tiklandi(no):
        veri = db_oku("SELECT durum, tip, ozellikler, isim, ucret, gun FROM odalar WHERE oda_no=?", (no,))
        if veri:
            oda = veri[0]
            if oda[0] == "Müsait": giris_penceresi(no, oda[1], oda[2])
            else: cikis_penceresi(no, oda[3], oda[4], oda[5], oda[2])

    # --- SAYFA YÖNETİMİ ---
    def sayfa_degistir(sayfa_adi):
        sayfa_odalar.pack_forget(); sayfa_raporlar.pack_forget()
        btn_kontrol.configure(fg_color="transparent"); btn_raporlar.configure(fg_color="transparent")
        if sayfa_adi == "odalar":
            sayfa_odalar.pack(fill="both", expand=True); btn_kontrol.configure(fg_color=C_CARD); panoyu_yenile()
        elif sayfa_adi == "raporlar":
            rapor_sayfasini_guncelle(); sayfa_raporlar.pack(fill="both", expand=True); btn_raporlar.configure(fg_color=C_CARD)

    # --- ARAYÜZ İSKELETİ ---
    # Sidebar genişliği 250'den 200'e düşürüldü
    sidebar = ctk.CTkFrame(app, width=200, fg_color=C_SIDEBAR, corner_radius=0); sidebar.pack(side="left", fill="y")
    ctk.CTkLabel(sidebar, text="GRAND OVA\nYÖNETİM", font=("Arial", 16, "bold"), text_color=C_GOLD).pack(pady=40)
    
    btn_kontrol = ctk.CTkButton(sidebar, text="Kontrol Paneli", anchor="w", fg_color=C_CARD, command=lambda: sayfa_degistir("odalar"))
    btn_kontrol.pack(fill="x", padx=10, pady=5)
    btn_raporlar = ctk.CTkButton(sidebar, text="Raporlar", anchor="w", fg_color="transparent", command=lambda: sayfa_degistir("raporlar"))
    btn_raporlar.pack(fill="x", padx=10, pady=5)
    ctk.CTkButton(sidebar, text="🔑 Şifre Değiştir", anchor="w", fg_color="transparent", command=sifre_degistir_penceresi).pack(fill="x", padx=10, pady=5)

    def gun_sonu_islemi():
        if messagebox.askyesno("Gün Sonu", "Bugünün cirosunu kapatıp arşive aktarmak istiyor musunuz?"):
            if db_yaz("INSERT INTO gecmis_raporlar (isim, oda_no, odeme_turu, tutar, islem_tarihi, gun_sonu_tarihi) SELECT isim, oda_no, odeme_turu, tutar, islem_tarihi, ? FROM raporlar", (datetime.now().strftime("%d.%m.%Y %H:%M"),)):
                db_yaz("DELETE FROM raporlar")
                panoyu_yenile()
                if sayfa_raporlar.winfo_ismapped(): rapor_sayfasini_guncelle()
                messagebox.showinfo("Başarılı", "Gün sonu yapıldı, kasa sıfırlandı.")

    ctk.CTkButton(sidebar, text="🌙 Gün Sonu Yap", fg_color="#5a1818", hover_color=C_RED, command=gun_sonu_islemi).pack(side="bottom", fill="x", padx=10, pady=30)

    main_content = ctk.CTkFrame(app, fg_color=C_BG, corner_radius=0); main_content.pack(side="right", fill="both", expand=True)
    topbar = ctk.CTkFrame(main_content, fg_color=C_BG, height=60); topbar.pack(fill="x", padx=15, pady=10)
    
    # Üst Panel Değerleri
    lbl_ust_musait = ctk.CTkLabel(topbar, text="55", text_color=C_GREEN, font=("Arial", 16, "bold"))
    lbl_ust_musait.pack(side="left", padx=(15, 5))
    ctk.CTkLabel(topbar, text="MÜSAİT", text_color=C_TEXT_GRI).pack(side="left", padx=(0, 20))
    lbl_ust_dolu = ctk.CTkLabel(topbar, text="0", text_color=C_RED, font=("Arial", 16, "bold"))
    lbl_ust_dolu.pack(side="left", padx=5)
    ctk.CTkLabel(topbar, text="DOLU", text_color=C_TEXT_GRI).pack(side="left")

    lbl_ust_ciro = ctk.CTkLabel(topbar, text="₺ 0", font=("Arial", 18, "bold"), text_color=C_GOLD)
    lbl_ust_ciro.pack(side="right", padx=15)
    
    sayfa_odalar = ctk.CTkScrollableFrame(main_content, fg_color=C_BG)
    sayfa_raporlar = ctk.CTkScrollableFrame(main_content, fg_color=C_BG)

    # --- TEK SIRA (SINGLE ROW) ODA KARTLARI DÖNGÜSÜ ---
    for kat in range(1, 6):
        kat_frame = ctk.CTkFrame(sayfa_odalar, fg_color=C_BG)
        kat_frame.pack(fill="x", padx=10, pady=5)
        
        # Kat Etiketi
        ctk.CTkLabel(kat_frame, text=f"{kat}. KAT", font=FONT_BASLIK, text_color=C_GOLD, width=65).pack(side="left", padx=(0, 5))
        
        for o in range(1, 12):
            no = kat * 100 + o
            
            # Arayüz renkleri ve tipleri
            if o in [1, 2]: 
                tip, renk = "TEK KİŞİLİK", RENK_TEK
            elif o in [4, 9] or (kat == 1 and o == 11): 
                tip, renk = "ÇİFT KİŞİLİK", RENK_CIFT
            else: 
                tip, renk = "DUBLE", RENK_DUBLE

            # Kart genişliği 90, yüksekliği 120 yapıldı
            kart = ctk.CTkFrame(kat_frame, fg_color=C_CARD, corner_radius=8, width=90, height=120)
            kart.pack(side="left", padx=4, pady=5)
            kart.pack_propagate(False) 
            
            # İç yazılar kart boyutuna göre milimetrik ayarlandı
            ctk.CTkLabel(kart, text=str(no), font=("Arial", 15, "bold"), text_color=C_GOLD).pack(anchor="w", padx=6, pady=(8, 0))
            ctk.CTkLabel(kart, text=tip, font=("Arial", 8, "bold"), text_color=renk).pack(anchor="w", padx=6)
            ld = ctk.CTkLabel(kart, text="Müsait", font=("Arial", 10), text_color=C_TEXT_GRI)
            ld.pack(anchor="w", padx=6, pady=(2, 5))
            
            # Buton boyut ve metinleri optimize edildi
            btn = ctk.CTkButton(kart, text="GİRİŞ", font=("Arial", 9, "bold"), height=22, command=lambda n=no: odaya_tiklandi(n))
            btn.pack(fill="x", padx=6, pady=(0, 5))
            
            oda_widgetleri[no] = {"kart": kart, "lbl_durum": ld, "btn": btn}

   # ================== RAPORLAR SAYFASI ==================
    ctk.CTkLabel(sayfa_raporlar, text="Raporlar", font=("Arial", 28, "bold"), text_color=C_GOLD).pack(anchor="w", padx=30, pady=(10, 0))
    ctk.CTkLabel(sayfa_raporlar, text="Günlük gelir özeti ve istatistikler", text_color=C_TEXT_GRI).pack(anchor="w", padx=30, pady=(0, 20))
    
    rapor_grid = ctk.CTkFrame(sayfa_raporlar, fg_color="transparent")
    rapor_grid.pack(fill="both", expand=True, padx=30)
    
    sol_sutun = ctk.CTkFrame(rapor_grid, fg_color="transparent")
    sol_sutun.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    sag_sutun = ctk.CTkFrame(rapor_grid, fg_color="transparent")
    sag_sutun.pack(side="right", fill="both", expand=True, padx=(10, 0))

    def rapor_sayfasini_guncelle():
        try:
            aktif_ciro_sorgu = db_oku("SELECT SUM(ucret * gun) FROM odalar WHERE durum='Dolu'")
            aktif_ciro = aktif_ciro_sorgu[0][0] if aktif_ciro_sorgu and aktif_ciro_sorgu[0][0] else 0
            
            tamamlanan_ciro_sorgu = db_oku("SELECT SUM(tutar) FROM raporlar")
            tamamlanan_ciro = tamamlanan_ciro_sorgu[0][0] if tamamlanan_ciro_sorgu and tamamlanan_ciro_sorgu[0][0] else 0
            
            dolu_oda_sorgu = db_oku("SELECT COUNT(*) FROM odalar WHERE durum='Dolu'")
            dolu_oda = dolu_oda_sorgu[0][0] if dolu_oda_sorgu else 0
            
            cikis_sayisi_sorgu = db_oku("SELECT COUNT(*) FROM raporlar")
            cikis_sayisi = cikis_sayisi_sorgu[0][0] if cikis_sayisi_sorgu else 0
        except Exception:
            return 

        for w in sol_sutun.winfo_children() + sag_sutun.winfo_children():
            w.destroy()

        def rapor_kutu_olustur(ebeveyn, baslik, deger_metni, alt_metin, yukseklik=120):
            kutu = ctk.CTkFrame(ebeveyn, fg_color=C_CARD, corner_radius=15, height=yukseklik)
            kutu.pack(fill="x", pady=10)
            kutu.pack_propagate(False)
            ctk.CTkLabel(kutu, text=baslik, font=("Arial", 12, "bold"), text_color=C_TEXT_GRI).pack(anchor="w", padx=20, pady=(15, 5))
            ctk.CTkLabel(kutu, text=deger_metni, font=("Arial", 28, "bold"), text_color=C_GOLD).pack(anchor="w", padx=20)
            ctk.CTkLabel(kutu, text=alt_metin, font=("Arial", 11), text_color=C_TEXT_GRI).pack(anchor="w", padx=20)

        rapor_kutu_olustur(sol_sutun, "BUGÜNKÜ TOPLAM CİRO", f"₺{(aktif_ciro + tamamlanan_ciro):,.0f}", "Aktif + Tamamlanan")
        rapor_kutu_olustur(sol_sutun, "AKTİF MİSAFİR CİROSU", f"₺{aktif_ciro:,.0f}", "Hâlâ konaklamakta")
        
        kat_durumu_kutu = ctk.CTkFrame(sol_sutun, fg_color=C_CARD, corner_radius=15)
        kat_durumu_kutu.pack(fill="x", pady=10, ipady=10)
        ctk.CTkLabel(kat_durumu_kutu, text="Kat Doluluk Durumu", font=("Arial", 12, "bold"), text_color=C_TEXT_GRI).pack(anchor="w", padx=20, pady=10)
        for kat in range(1, 6):
            kat_dolu_sorgu = db_oku("SELECT COUNT(*) FROM odalar WHERE durum='Dolu' AND oda_no LIKE ?", (f"{kat}%",))
            kat_dolu = kat_dolu_sorgu[0][0] if kat_dolu_sorgu else 0
            satir = ctk.CTkFrame(kat_durumu_kutu, fg_color="transparent")
            satir.pack(fill="x", padx=20, pady=5)
            ctk.CTkLabel(satir, text=f"Kat {kat}", font=("Arial", 12, "bold"), text_color=C_GOLD).pack(side="left")
            ctk.CTkLabel(satir, text=f"{kat_dolu}/11 Dolu", text_color=C_TEXT).pack(side="right")

        oran = int((dolu_oda / 55) * 100) if dolu_oda > 0 else 0
        rapor_kutu_olustur(sag_sutun, "DOLULUK ORANI", f"%{oran}", f"{dolu_oda} / 55 oda dolu")
        rapor_kutu_olustur(sag_sutun, "GÜNLÜK TAMAMLANAN ÇIKIŞ", str(cikis_sayisi), "Oda tahsil edildi")
        
        gecmis_kutu = ctk.CTkFrame(sag_sutun, fg_color=C_CARD, corner_radius=15)
        gecmis_kutu.pack(fill="x", pady=10, ipady=10, expand=True)
        ctk.CTkLabel(gecmis_kutu, text="Bugünkü Çıkışlar ve Kişi Bilgileri", font=("Arial", 12, "bold"), text_color=C_TEXT_GRI).pack(anchor="w", padx=20, pady=10)
        
        gecmis_veriler = db_oku("SELECT isim, oda_no, odeme_turu, tutar FROM raporlar ORDER BY id DESC LIMIT 5")
        if not gecmis_veriler:
            ctk.CTkLabel(gecmis_kutu, text="Bugün henüz ödeme yok.", text_color=C_TEXT_GRI).pack(pady=20)
        else:
            for islem in gecmis_veriler:
                satir = ctk.CTkFrame(gecmis_kutu, fg_color="transparent")
                satir.pack(fill="x", padx=20, pady=5)
                ctk.CTkLabel(satir, text=f"{islem[0]} (Oda {islem[1]})", text_color=C_TEXT, font=("Arial", 11, "bold")).pack(side="left")
                ctk.CTkLabel(satir, text=f"₺{islem[3]:,.0f} • {islem[2]}", text_color=C_GOLD).pack(side="right")

    sayfa_degistir("odalar")
    app.mainloop()

if __name__ == "__main__":
    giris_ekrani()
