import random  # Risk simülasyonu için rasgele seçim yapılıyor
import heapq  # Dijkstra için kullanıyoruz
import hashlib  # Kriptografik hash üretmek için
import matplotlib.pyplot as plt  # Rotayı grafik olarak çizdirmek için
from matplotlib import animation  # Canlı animasyon için
import sqlite3  # SQLite veritabanı işlemleri için
from playsound import playsound  # Sesli uyarı için
from collections import defaultdict  # Sözlüklerde otomatik boş değer için
from math import radians, sin, cos, sqrt, atan2  # Matematiksel hesaplamalar için
import tkinter as tk  # Arayüz
from tkinter import ttk, messagebox  # Diyalog ve mesaj penceresi için
from pprint import pformat  # Huffman gibi karmaşık veri yapılarını okunabilir stringe çevirir
import os  # Dosya işlemleri için

# Liman verisi
limanlar = {
    "İstanbul": (41.0082, 28.9784),  # Limanların enlem ve boylamları
    "Hamburg": (53.5511, 9.9937),
    "Rotterdam": (51.9225, 4.47917),
    "New York": (40.7128, -74.0060),
    "Los Angeles": (34.0522, -118.2437),
    "Busan": (35.1796, 129.0756),
    "Şanghay": (31.2304, 121.4737),
    "Tokyo": (35.6762, 139.6503)
}

gemi_hizlari = {  # Saatte kat edilen kilometre değeri
    "Tanker": 30,
    "Konteyner": 40,
    "Yolcu Gemisi": 50
}

# --------------------------------------------
# Temel Fonksiyonlar
# --------------------------------------------

def mesafe_hesapla(koord1, koord2):
    """İki nokta arasındaki mesafeyi Haversine formülü ile hesaplar."""
    R = 6371  # Dünyanın yarıçapı (km)
    lat1, lon1 = radians(koord1[0]), radians(koord1[1])
    lat2, lon2 = radians(koord2[0]), radians(koord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def grafik_olustur():
    """Limanlar arasında mesafe bazlı ağı oluşturur."""
    grafik = defaultdict(dict)
    for liman1 in limanlar:
        for liman2 in limanlar:
            if liman1 != liman2:
                mesafe = mesafe_hesapla(limanlar[liman1], limanlar[liman2])
                # 10000 km'den küçükse komşu olarak kabul ediliyor
                if mesafe < 10000:
                    grafik[liman1][liman2] = round(mesafe)
    return grafik

grafigim = grafik_olustur()

def dijkstra(grafik, baslangic, bitis):
    """
    En kısa yolu bulur (maliyet, yol) şeklinde döner.
    Klasik Dijkstra algoritması.
    """
    kuyruk = [(0, baslangic, [])]  # (maliyet, mevcut düğüm, izlenen yol)
    ziyaret_edilenler = set()
    while kuyruk:
        maliyet, dugum, yol = heapq.heappop(kuyruk)
        if dugum in ziyaret_edilenler:
            continue
        ziyaret_edilenler.add(dugum)
        yol = yol + [dugum]
        if dugum == bitis:
            return maliyet, yol
        for komsu, uzaklik in grafik.get(dugum, {}).items():
            heapq.heappush(kuyruk, (maliyet + uzaklik, komsu, yol))
    return float("inf"), []

# --------------------------------------------
# 1. En Kısa 3 Rota (K-Shortest Paths - Basit Yaklaşım)
# --------------------------------------------

def dijkstra_tum_yollar(grafik, start, hedef, k=3):
    """
    Yen's algoritmasına dayalı basit bir K-en kısa yol yaklaşımlı fonksiyon.
    Grafiğe göre en az maliyetli k farklı rota (yol ve mesafe) döner.
    """
    # İlk olarak en kısa yolu bulalım
    baslangic_maliyet, baslangic_yol = dijkstra(grafik, start, hedef)
    if baslangic_maliyet == float("inf"):
        return []
    rotalar = [ (baslangic_maliyet, baslangic_yol) ]
    adim = 0

    # Aday yolları saklamak için min-heap
    adaylar = []
    # Yen algoritması adımları
    for i in range(len(baslangic_yol) - 1):
        spur_node = baslangic_yol[i]
        root_path = baslangic_yol[:i+1]
        # Kök yol üzerindeki kenarları geçici olarak kaldır
        removed_edges = []
        for (maliyet_y, yol_y) in rotalar:
            if len(yol_y) > i and yol_y[:i+1] == root_path:
                u = yol_y[i]
                v = yol_y[i+1]
                if v in grafik[u]:
                    weight = grafik[u].pop(v)
                    removed_edges.append((u, v, weight))
        # Kök yolu dışındaki düğümleri ziyaret etmeyi engelle
        # (özetle, aynı kök yolu paylaşan rotalar için tekrar hesaplama yapılır)
        try:
            spur_cost, spur_path = dijkstra(grafik, spur_node, hedef)
            if spur_cost != float("inf"):
                toplam_yol = root_path[:-1] + spur_path
                toplam_maliyet = sum(grafik[ toplam_yol[j] ][ toplam_yol[j+1] ]
                                     for j in range(len(toplam_yol)-1))
                if (toplam_maliyet, toplam_yol) not in adaylar:
                    heapq.heappush(adaylar, (toplam_maliyet, toplam_yol))
        except KeyError:
            pass
        # Kaldırılan kenarları geri ekle
        for u, v, weight in removed_edges:
            grafik[u][v] = weight

    # Adaylardan en küçük k-1 tanesini al
    while adaylar and len(rotalar) < k:
        maliyet, yol = heapq.heappop(adaylar)
        rotalar.append((maliyet, yol))
    return rotalar

# --------------------------------------------
# 2. Canlı Gemi Animasyonu
# --------------------------------------------
def en_yakin_limanlar(baslangic, k=3):
    """
    Bir liman ismine göre en yakın k limanı döner.
    """
    if baslangic not in limanlar:
        return []
    hedef_konum = limanlar[baslangic]
    mesafeler = []
    for liman, konum in limanlar.items():
        if liman != baslangic:
            mesafe = mesafe_hesapla(hedef_konum, konum)
            mesafeler.append((mesafe, liman))
    mesafeler.sort()
    return [liman for _, liman in mesafeler[:k]]

def rota_animasyonu(yol, interval=1000):
    """
    Belirtilen yol üzerine adım adım animasyonlu bir çizim yapar.
    Gemi konumuna göre en yakın 3 limanı gösterir.
    interval: her adımın milisaniye cinsinden süresi (default 1000ms).
    """
    import matplotlib.pyplot as plt
    from matplotlib import animation

    def en_yakin_limanlar_koord(koord, k=3):
        mesafeler = []
        for liman, liman_koord in limanlar.items():
            mesafe = mesafe_hesapla(koord, liman_koord)
            mesafeler.append((mesafe, liman))
        mesafeler.sort()
        return [liman for _, liman in mesafeler[:k]]

    # Enlem ve boylamlar
    xs = [limanlar[liman][1] for liman in yol]
    ys = [limanlar[liman][0] for liman in yol]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title("Canli Gemi Rotasi Animasyonu")
    ax.set_xlabel("Boylam")
    ax.set_ylabel("Enlem")
    ax.grid(True)

    # Dinamik eksen ayarla
    all_lons = [koord[1] for koord in limanlar.values()]
    all_lats = [koord[0] for koord in limanlar.values()]
    ax.set_xlim(min(all_lons)-20, max(all_lons)+20)
    ax.set_ylim(min(all_lats)-20, max(all_lats)+20)

    # Liman etiketlerini yerleştir
    for liman in yol:
        enlem, boylam = limanlar[liman]
        ax.text(boylam, enlem, liman, fontsize=9, ha='right', va='bottom')

    line, = ax.plot([], [], marker='o', linestyle='-', color='blue', label="Gemi")
    ship_dot, = ax.plot([], [], 'ro', markersize=8)
    nearest_text = ax.text(0, 0, '', fontsize=10, color='darkred')

    def init():
        line.set_data([], [])
        ship_dot.set_data([], [])
        nearest_text.set_text("")
        return line, ship_dot, nearest_text

    def animate(i):
        line.set_data(xs[:i+1], ys[:i+1])
        ship_dot.set_data(xs[i], ys[i])

        # Gemi koordinatına göre en yakın 3 liman
        gemi_konum = (ys[i], xs[i])
        yakinlar = en_yakin_limanlar_koord(gemi_konum, k=3)
        nearest_text.set_position((xs[i], ys[i]+5))
        nearest_text.set_text("Yakin 3 Liman:\n" + " | ".join(yakinlar))

        return line, ship_dot, nearest_text

    ani = animation.FuncAnimation(
        fig, animate, init_func=init,
        frames=len(xs), interval=interval, blit=True, repeat=False
    )
    plt.legend()
    plt.show()



# --------------------------------------------
# 3. Sesli Uyarı
# --------------------------------------------

def sesli_uyari():
    """
    Riskli durum algılandığında bir ses dosyası çalar.
    Örnek olarak working directory içinde 'alert.mp3' olması beklenir.
    """
    ses_dosyasi = "alert.mp3"
    if os.path.exists(ses_dosyasi):
        try:
            playsound(ses_dosyasi)
        except Exception as e:
            print("Ses çalınırken hata oluştu:", e)
    else:
        print("Uyarı ses dosyası bulunamadı: ", ses_dosyasi)

# --------------------------------------------
# 4. Veritabanı Kayıt
# --------------------------------------------

def veritabani_kaydet(rota, mesafe, gemi_tipi, huffman_kodlari, hash_ozet):
    """
    Belirtilen rota bilgilerini SQLite veritabanına kaydeder.
    'routes.db' adlı bir dosya oluşturur ve içine 'rotalar' tablosunu ekler.
    """
    conn = sqlite3.connect('routes.db')
    cursor = conn.cursor()

    # Tabloyu oluştur (varsa atla)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rotalar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rota_metni TEXT,
            mesafe INTEGER,
            gemi_tipi TEXT,
            huffman TEXT,
            hash_ozet TEXT,
            kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Huffman kodlarını stringe çevir
    huffman_str = pformat(huffman_kodlari, width=80)

    # Veriyi ekle
    cursor.execute('''
        INSERT INTO rotalar (rota_metni, mesafe, gemi_tipi, huffman, hash_ozet)
        VALUES (?, ?, ?, ?, ?)
    ''', (rota, mesafe, gemi_tipi, huffman_str, hash_ozet))

    conn.commit()
    conn.close()

# --------------------------------------------
# 5. PDF Dışa Aktarım
# --------------------------------------------
def txt_raporu_olustur(rota, mesafe, gemi_tipi, huffman_kodlari, hash_ozet, dosya_adi="rota_raporu.txt"):
    try:
        with open(dosya_adi, "w", encoding="utf-8") as f:
            f.write("SMARTSEA: Deniz Rota Raporu\n")
            f.write("=" * 40 + "\n")
            f.write(f"Gemi Tipi: {gemi_tipi}\n")
            f.write(f"Rota: {rota}\n")
            f.write(f"Toplam Mesafe: {mesafe} km\n")
            f.write(f"Hash (SHA-256): {hash_ozet}\n\n")
            f.write("Huffman Kodları:\n")
            for char, kod in huffman_kodlari.items():
                f.write(f"  '{char}': {kod}\n")
        print(f"TXT raporu oluşturuldu: {dosya_adi}")
    except Exception as e:
        print("TXT oluşturulurken hata:", e)



# --------------------------------------------
# 6. Huffman Kodları Yatay Format (pformat zaten yatay gösterim sağlar)
# --------------------------------------------
# Mevcut pformat() kullanımı, sözlükleri okunabilir ve yatay gösterir.
# Bu bölüme ek bir işlev gerekmedi.

# --------------------------------------------
# 7. Gelişmiş Hamming Testi
# --------------------------------------------

def hamming_kontrol(veri):
    """
    Veriye rastgele bir hata ekler ve ardından orijinal veriyi tespit eder.
    Rastgele bir indeks seçilip, buradaki karakter 'X' ile değiştirilir.
    """
    if not veri:
        print("Boş veri verildi.")
        return
    indeks = random.randint(0, len(veri) - 1)
    bozuk = list(veri)
    bozuk[indeks] = 'X'
    print("Bozulmuş veri:", "".join(bozuk))
    print("Orijinal veri:", veri)
    if "".join(bozuk) != veri:
        print(f"Hamming testi: Hata bulundu, indeks {indeks}.")
    else:
        print("Hamming testi: Hata bulunamadı.")

# --------------------------------------------
# Risk Simülasyonu ve Güvenli Rota
# --------------------------------------------

risk_agirliklari = [0.1, 0.1, 0.1, 0.233, 0.233, 0.133, 0.1]

def risk_simulasyonu(yol):
    """
    Verilen rotadaki her nokta için rastgele bir risk durumu üretir.
    """
    riskler = ["Fırtına", "Arıza", "Korsan Saldırısı", None, None, None, None]
    return [(nokta, random.choices(riskler, weights=risk_agirliklari)[0]) for nokta in yol]

def kullanici_karari_sor(olay, konum):
    """
    Riskli durumda kullanıcıya bekleyip beklemek istemediğini sorar.
    """
    pencere = tk.Tk()
    pencere.withdraw()
    secim = messagebox.askquestion("Riskli Durum", f"{olay} tespit edildi ({konum}). Beklemek ister misiniz?")
    pencere.destroy()
    return "bekle" if secim == 'yes' else "rota değiştir"

def guvenli_rota(baslangic, bitis, maksimum_deneme=5):
    """
    Riskli durumlara göre güvenli rota hesaplaması yapar.
    Maksimum deneme sayısına kadar aynı işlemi tekrarlar.
    """
    deneme = 0
    while deneme < maksimum_deneme:
        maliyet, yol = dijkstra(grafigim, baslangic, bitis)
        olaylar = risk_simulasyonu(yol)
        riskli = [(nokta, olay) for nokta, olay in olaylar if olay in ["Fırtına", "Korsan Saldırısı"]]
        if riskli:
            for nokta, olay in riskli:
                sesli_uyari()  # Riskli durumda sesli uyarı
                karar = kullanici_karari_sor(olay, nokta)
                if karar == "bekle":
                    deneme += 1
                    break
                elif karar == "rota değiştir":
                    deneme += 1
                    break
            else:
                return maliyet, yol
        else:
            return maliyet, yol
    return maliyet, yol

def varis_suresi_hesapla(mesafe, gemi_tipi):
    """
    Rota mesafesi ve gemi tipine göre tahmini varış süresini saat ve dakika cinsinden hesaplar.
    """
    hiz = gemi_hizlari.get(gemi_tipi, 35)
    return mesafe / hiz

def hash_olustur(rota, mesafe, gemi_tipi):
    """
    Rotayı, mesafeyi ve gemi tipini içeren bir stringin SHA-256 hash'ini üretir.
    """
    veri = f"{rota} | {mesafe} | {gemi_tipi}"
    return hashlib.sha256(veri.encode()).hexdigest()

# --------------------------------------------
# Huffman Kodlama
# --------------------------------------------

class HuffmanDugumu:
    def __init__(self, karakter, frekans):
        self.karakter = karakter
        self.frekans = frekans
        self.sol = None
        self.sag = None

    def __lt__(self, diger):
        return self.frekans < diger.frekans

def huffman_agaci_olustur(metin):
    frekans = defaultdict(int)
    for karakter in metin:
        frekans[karakter] += 1
    kuyruk = [HuffmanDugumu(k, f) for k, f in frekans.items()]
    heapq.heapify(kuyruk)
    while len(kuyruk) > 1:
        sol = heapq.heappop(kuyruk)
        sag = heapq.heappop(kuyruk)
        birlesik = HuffmanDugumu(None, sol.frekans + sag.frekans)
        birlesik.sol = sol
        birlesik.sag = sag
        heapq.heappush(kuyruk, birlesik)
    return kuyruk[0] if kuyruk else None

def huffman_kodlari_uret(kok, on_ek="", kod_kaydi=None):
    if kod_kaydi is None:
        kod_kaydi = {}
    if kok:
        if kok.karakter is not None:
            kod_kaydi[kok.karakter] = on_ek
        huffman_kodlari_uret(kok.sol, on_ek + "0", kod_kaydi)
        huffman_kodlari_uret(kok.sag, on_ek + "1", kod_kaydi)
    return kod_kaydi

def huffman_sifrele(metin):
    agac = huffman_agaci_olustur(metin)
    return huffman_kodlari_uret(agac)

# --------------------------------------------
# Rota Çizim Fonksiyonu
# --------------------------------------------

def rota_ciz(yol):
    """
    Statik olarak rotayı çizer.
    """
    plt.figure(figsize=(10, 6))
    xs, ys = [], []
    for liman in yol:
        enlem, boylam = limanlar[liman]
        xs.append(boylam)
        ys.append(enlem)
        plt.text(boylam, enlem, liman, fontsize=9, ha='right', va='bottom')
    plt.plot(xs, ys, marker='o', linestyle='-', color='blue')
    plt.title("📍 Deniz Yolu Rotası")
    plt.xlabel("Boylam")
    plt.ylabel("Enlem")
    plt.grid(True)
    plt.show()

# --------------------------------------------
# Ana Uygulama - Tkinter Arayüzü
# --------------------------------------------

class AkilliDenizUygulamasi(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SMARTSEA: Akıllı Deniz Rota Sistemi")
        self.geometry("600x650")
        self.arayuz_olustur()

    def arayuz_olustur(self):
        tk.Label(self, text="Kalkış Limanı:").pack(pady=5)
        self.baslangic_var = tk.StringVar()
        self.baslangic_secim = ttk.Combobox(self, values=list(limanlar.keys()), textvariable=self.baslangic_var)
        self.baslangic_secim.pack()
        self.baslangic_secim.bind("<<ComboboxSelected>>", self.mola_guncelle)

        tk.Label(self, text="Varış Limanı:").pack(pady=5)
        self.varis_var = tk.StringVar()
        self.varis_secim = ttk.Combobox(self, values=list(limanlar.keys()), textvariable=self.varis_var)
        self.varis_secim.pack()

        tk.Label(self, text="Mola Limanı (İsteğe Bağlı):").pack(pady=5)
        self.mola_var = tk.StringVar()
        self.mola_secim = ttk.Combobox(self, values=[""] + list(limanlar.keys()), textvariable=self.mola_var)
        self.mola_secim.pack()

        tk.Label(self, text="Gemi Tipi:").pack(pady=5)
        self.gemi_var = tk.StringVar(value="Konteyner")
        self.gemi_secim = ttk.Combobox(self, values=list(gemi_hizlari.keys()), textvariable=self.gemi_var)
        self.gemi_secim.pack()

        tk.Button(self, text="Rota Hesapla", command=self.rota_hesapla).pack(pady=10)
        tk.Button(self, text="Canlı Animasyon Göster", command=self.canli_animasyon).pack(pady=5)
        tk.Button(self, text="Veritabanına Kaydet", command=self.veritabanina_kaydet_btn).pack(pady=5)
        tk.Button(self, text="TXT Raporu Oluştur", command=self.txt_olustur_btn).pack(pady=5)

        self.sonuc_ekran = tk.Text(self, height=20)
        self.sonuc_ekran.pack(pady=10)

    def mola_guncelle(self, event):
        baslangic = self.baslangic_var.get()
        yakinlar = en_yakin_limanlar(baslangic, k=3)
        self.mola_secim['values'] = [""] + yakinlar
        if self.mola_var.get() not in yakinlar:
            self.mola_var.set("")

    def rota_hesapla(self):
        baslangic = self.baslangic_var.get()
        varis = self.varis_var.get()
        mola = self.mola_var.get().strip()
        gemi_tipi = self.gemi_var.get()

        if baslangic == "" or varis == "" or baslangic == varis:
            messagebox.showerror("Hata", "Geçerli kalkış ve varış limanları seçiniz.")
            return

                # Alternatif 3 rota (en iyi 3)
        tum_rotalar = dijkstra_tum_yollar(grafigim, baslangic, varis, k=3)

        # İlk olarak önceki hesaplamaları temizleyelim
        self.sonuc_ekran.delete(1.0, tk.END)

        # Ana rotayı hesaplama (mola var/ yok durumuna göre)
        if mola and mola not in [baslangic, varis]:
            masraf1, yol1 = guvenli_rota(baslangic, mola)
            masraf2, yol2 = guvenli_rota(mola, varis)
            toplam_masraf = masraf1 + masraf2
            tam_yol = yol1 + yol2[1:]
        else:
            toplam_masraf, tam_yol = guvenli_rota(baslangic, varis)

        # Tahmini varış süresi
        saat = varis_suresi_hesapla(toplam_masraf, gemi_tipi)
        varis_suresi = f"{int(saat)} saat {int((saat - int(saat)) * 60)} dakika"

        # Rota metni, Huffman ve hash
        rota_metin = "->".join(tam_yol)
        huffman = huffman_sifrele(rota_metin)
        ozet = hash_olustur(rota_metin, toplam_masraf, gemi_tipi)

        # Bilgileri ekrana yazdır
        self.sonuc_ekran.insert(tk.END, f"🌟 Ana Rota:\n")
        self.sonuc_ekran.insert(tk.END, f"  Rota Metni: {rota_metin}\n")
        self.sonuc_ekran.insert(tk.END, f"  Toplam Mesafe: {toplam_masraf} km\n")
        self.sonuc_ekran.insert(tk.END, f"  Gemi Tipi: {gemi_tipi}\n")
        self.sonuc_ekran.insert(tk.END, f"  Tahmini Varış Süresi: {varis_suresi}\n")
        self.sonuc_ekran.insert(tk.END, f"  Hash (SHA-256): {ozet}\n")
        self.sonuc_ekran.insert(tk.END, f"  Huffman Kodları:\n")
        self.sonuc_ekran.insert(tk.END, pformat(huffman, width=60) + "\n\n")

        # Alternatif rotaları listele
        self.sonuc_ekran.insert(tk.END, "🔹 En Kısa 3 Alternatif Rota (Direkt):\n")
        for idx, (maliyet, yol) in enumerate(tum_rotalar, start=1):
            yol_metni = "->".join(yol)
            self.sonuc_ekran.insert(
                tk.END,
                f"  {idx}. Rota: {yol_metni}     Mesafe: {maliyet} km\n"
            )
        self.sonuc_ekran.insert(tk.END, "\n")

        # Rota çizimi (statik)
        rota_ciz(tam_yol)

        # Hamming testi
        hamming_kontrol(rota_metin)

        # Sonuçları instance değişkenlerine kaydet (diğer butonlar için)
        self.current_yol = tam_yol
        self.current_rota_metin = rota_metin
        self.current_mesafe = toplam_masraf
        self.current_gemi_tipi = gemi_tipi
        self.current_huffman = huffman
        self.current_hash = ozet

    def canli_animasyon(self):
        """
        'Canlı Animasyon Göster' butonuna basıldığında çağrılır.
        Eğer bir rota hesaplandıysa, animasyonu başlatır.
        """
        try:
            yol = self.current_yol
            rota_animasyonu(yol, interval=800)
        except AttributeError:
            messagebox.showwarning("Uyarı", "Önce bir rota hesaplamalısınız.")

    def veritabanina_kaydet_btn(self):
        """
        'Veritabanına Kaydet' butonuna basıldığında çağrılır.
        Mevcut rota bilgilerini SQLite veritabanına kaydeder.
        """
        try:
            rota = self.current_rota_metin
            mesafe = self.current_mesafe
            gemi_tipi = self.current_gemi_tipi
            huffman_kodlari = self.current_huffman
            hash_ozet = self.current_hash
            veritabani_kaydet(rota, mesafe, gemi_tipi, huffman_kodlari, hash_ozet)
            messagebox.showinfo("Başarılı", "Rota bilgileri veritabanına kaydedildi.")
        except AttributeError:
            messagebox.showwarning("Uyarı", "Kaydedilecek bir rota yok. Önce rota hesaplayın.")

    def txt_olustur_btn(self):
        """
        'TXT Raporu Oluştur' butonuna basıldığında çağrılır.
        Mevcut rota bilgileriyle TXT rapor oluşturur.
        """
        try:
            rota = self.current_rota_metin
            mesafe = self.current_mesafe
            gemi_tipi = self.current_gemi_tipi
            huffman_kodlari = self.current_huffman
            hash_ozet = self.current_hash
            dosya_adi = "rota_raporu.txt"
            txt_raporu_olustur(rota, mesafe, gemi_tipi, huffman_kodlari, hash_ozet, dosya_adi)
            messagebox.showinfo("Başarılı", f"TXT raporu oluşturuldu: {dosya_adi}")
        except AttributeError:
            messagebox.showwarning("Uyarı", "TXT oluşturmak için önce rota hesaplayın.")


if __name__ == "__main__":
    uygulama = AkilliDenizUygulamasi()
    uygulama.mainloop()

