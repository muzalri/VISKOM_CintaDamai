# Ringkasan Update Draft Jurnal dengan Fitur Hazard Map

## Status Update: ✅ SELESAI

Draft bab metodologi dan hasil pembahasan sudah diupdate untuk memasukkan fitur **Hazard Map** yang baru. Berikut ringkasan perubahan yang telah dilakukan:

---

## Perubahan Utama

### 1. **Subbab 3.5 Arsitektur Sistem** - UPDATED ✅
**Penambahan:**
- Penjelasan tentang fitur Hazard Map sebagai peta interaktif
- Integrasi geolokasi pengguna dengan deteksi pothole
- Dynamic proximity alert berdasarkan kecepatan kendaraan

**Narasi baru:**
> "Selain itu, sistem juga dilengkapi dengan fitur **Hazard Map** yang merupakan peta interaktif berbasis web untuk menampilkan lokasi-lokasi jalan berlubang yang terdeteksi. Hazard Map mengintegrasikan data geolokasi pengguna, koordinat pothole dari database, dan informasi kecepatan kendaraan untuk memberikan peringatan proximity alert secara real-time."

### 2. **Subbab 3.7 Implementasi Sistem** - UPDATED ✅
**Penambahan lengkap:**
- Dua halaman utama: deteksi dan Hazard Map
- Teknologi Leaflet.js untuk rendering peta interaktif
- OpenStreetMap sebagai basemap
- Database models: Pothole, UserLocation, Alert, DetectionHistory
- 3 API endpoints dengan deskripsi lengkap:
  - GET `/api/hazard-map/potholes`
  - POST `/api/hazard-map/nearby` (dengan proximity check)
  - POST `/api/hazard-map/add`
- Formula haversine untuk perhitungan jarak

### 3. **Subbab 4.4 Hasil Implementasi Sistem Web** - UPDATED ✅
**Penambahan:**
- Hasil implementasi Hazard Map berhasil terintegrasi
- Marker pothole dengan warna sesuai severity level
- Proximity alert berfungsi dengan informasi jarak dan severity
- WebSocket broadcast untuk update real-time

**Narasi tambahan:**
> "Fitur Hazard Map berhasil mengintegrasikan deteksi pothole dengan geolokasi pengguna. Peta interaktif menampilkan marker untuk setiap lokasi pothole dengan warna berbeda sesuai severity level (merah untuk high, kuning untuk medium, hijau untuk low)."

### 4. **Tabel-tabel Baru** - UPDATED ✅
Ditambahkan 2 tabel wajib:

**Tabel 4.3. API Endpoints Hazard Map**
| Endpoint | Method | Deskripsi | Parameter |
| --- | --- | --- | --- |
| `/api/hazard-map/potholes` | GET | Mengambil semua data pothole | - |
| `/api/hazard-map/nearby` | POST | Proximity check pothole | latitude, longitude, speed, accuracy |
| `/api/hazard-map/add` | POST | Tambah pothole baru | latitude, longitude, confidence, severity |

**Tabel 4.4. Severity Level Pothole**
| Severity | Warna Marker | Confidence Range | Deskripsi |
| --- | --- | --- | --- |
| High | Merah | > 0,80 | Pothole besar atau sangat dalam |
| Medium | Kuning | 0,60 - 0,80 | Pothole sedang atau cukup dalam |
| Low | Hijau | < 0,60 | Pothole kecil atau depresi kecil |

### 5. **Gambar-gambar Baru** - PENDING (siap list)
Ditambahkan daftar gambar wajib:
- **Gambar 4.8a.** Tampilan Hazard Map dengan marker pothole
- **Gambar 4.8b.** Proximity alert dari Hazard Map

Gambar opsional tambahan:
- **Gambar 4.11.** Interface detail marker pothole di Hazard Map
- **Gambar 4.12.** Radius dinamis proximity alert

---

## Gambar yang Perlu Diambil dari Project

### Dari Hazard Map di Project
1. **Gambar 4.8a** - Ambil screenshot dari halaman `/hazard-map` saat aplikasi dijalankan
   - Tampilkan peta dengan beberapa marker pothole berwarna
   - Sumber: browser screenshot saat app.py running

2. **Gambar 4.8b** - Screenshot notifikasi proximity alert
   - Tampilkan popup/alert saat mendekati zona pothole
   - Sumber: browser screenshot + simulate proximity event

3. **Gambar 4.11** (opsional) - Popup marker detail
   - Klik marker di peta untuk melihat detail pothole
   - Info: koordinat, confidence, severity, waktu

4. **Gambar 4.12** (opsional) - Radius circle visualization
   - Tampilkan lingkaran radius yang berubah sesuai kecepatan
   - Tekan tombol untuk simulate perubahan kecepatan

---

## Checklist Selesai

- [x] Update subbab 3.5 Arsitektur Sistem dengan Hazard Map
- [x] Update subbab 3.7 Implementasi Sistem dengan detail API & database
- [x] Update subbab 4.4 Hasil Implementasi dengan Hazard Map results
- [x] Tambah Tabel 4.3 (API Endpoints)
- [x] Tambah Tabel 4.4 (Severity Levels)
- [x] Tambah gambar Hazard Map ke daftar gambar wajib
- [ ] Ambil screenshot Hazard Map dari aplikasi
- [ ] Ambil screenshot proximity alert

---

## Status File Draft

📄 **File Draft:** `draft_bab_metodologi_hasil_pembahasan.md`

✅ **Siap digunakan:** Ya, semua narasi dan tabel sudah update

⏳ **Pending:** Screenshot gambar dari fitur Hazard Map (butuh aplikasi running)

---

## Langkah Selanjutnya

1. **Jalankan aplikasi** dengan `python app.py`
2. **Buka browser** ke `http://localhost:5000/hazard-map`
3. **Ambil screenshot** untuk gambar-gambar wajib
4. **Masukkan ke dalam jurnal** sesuai daftar gambar di draft
5. **Verifikasi** bahwa semua penjelasan sesuai dengan implementasi

---

## Catatan Penting

- Hazard Map menggunakan **Leaflet.js** (bukan Google Maps) untuk kesederhanaan
- Database model sudah ada di `models.py` (Pothole, UserLocation, Alert, DetectionHistory)
- API endpoint sudah fully functional di `app.py` (lines 294+)
- Proximity alert menggunakan **formula haversine** untuk kalkulasi jarak
- Radius dinamis dihitung berdasarkan kecepatan: `base_radius * (speed / 50)`

---

Draft jurnal siap untuk dilanjutkan ke tahap penulisan bab pendahuluan, kesimpulan, dan daftar pustaka! 🎉
