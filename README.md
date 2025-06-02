# 🌊 SMARTSEA - Akıllı Deniz Rota Sistemi (Python)

SMARTSEA, deniz taşımacılığı için geliştirilen **tek dosyalı, akıllı bir rota planlama ve güvenlik yazılımıdır**. Python kullanılarak geliştirilen bu sistem, kullanıcıya en kısa ve güvenli deniz rotasını önerir. Aynı zamanda çeşitli güvenlik önlemleri, animasyonlar ve veritabanı kayıt sistemi içerir.

---

## 🎯 Amaç

Bu proje, deniz yolculuklarında karşılaşılabilecek zorlukları (fırtına, korsan saldırıları, teknik arızalar gibi) simüle ederek, **optimum ve güvenli bir rota önerisi sunmayı** hedefler. Kullanıcı dostu bir arayüzle tüm işlemler kolayca yönetilebilir.

---

## 🧩 Özellikler

- 🚢 En kısa ve alternatif 3 rota hesaplama (Dijkstra algoritması)
- ⚠️ Risk simülasyonu (fırtına, korsan vb.)
- 🔁 Kullanıcının kararına göre rota yeniden hesaplama
- 🔊 Risk durumunda sesli uyarı (alert.mp3 ile)
- 📈 Rota görselleştirme ve animasyon (matplotlib)
- 🗃️ SQLite veritabanına kayıt (routes.db)
- 📄 TXT formatında rota raporu oluşturma
- 🔐 SHA-256 hash özeti ve Huffman kodlama
- 🧪 Hamming testi ile veri bütünlüğü kontrolü
- 🖥️ Tkinter ile görsel kullanıcı arayüzü

---

## 🛡️ Güvenlik Özellikleri

- SHA-256 ile rota verilerinin özeti alınır.  
- Huffman Kodlama ile rota metni sıkıştırılır.  
- Hamming Testi ile veri hatası simüle edilir.  

---

## 🎥 Animasyon Özelliği

Matplotlib kullanılarak rota üzerindeki geçişler canlı olarak gösterilir. Her adımda geminin bulunduğu noktaya göre en yakın 3 liman da ekranda belirtilir.

---

## 👨‍💻 Geliştirici Notu

Bu proje, algoritma tabanlı rota planlama ve karar destek sistemlerinin temelini atmak amacıyla geliştirilmiştir. Gerçek zamanlı veri bağlantısı içermez ancak genişletmeye uygundur.

---

## 🛠️ Geliştirme Hedefleri

- [ ] Hava durumu API’si ile gerçek zamanlı risk verisi  
- [ ] Harici gemi takip sistemleri (AIS entegrasyonu)  
- [ ] Web tabanlı sürüm (Flask/Django ile)  
- [ ] Mobil uygulama için Flutter/React Native adaptasyonu  

## ⚙️ Kurulum ve Çalıştırma

SMARTSEA uygulamasını çalıştırmak için aşağıdaki adımları takip edebilirsiniz:

### 1. Python Kurulumu

Bu proje Python 3 ile geliştirilmiştir. Henüz kurulu değilse, [python.org](https://www.python.org/downloads/) üzerinden Python 3.x sürümünü indirip yükleyin.

### 2. Gerekli Kütüphanelerin Kurulumu 

Terminal ya da komut istemcisinde aşağıdaki komutu çalıştırarak eksik kütüphaneleri yükleyin:

```bash
pip install matplotlib playsound

### 3. Ses Dosyasını Ekleyin
Risk uyarısı sırasında çalması için proje dizinine bir ses dosyası yerleştirin:
