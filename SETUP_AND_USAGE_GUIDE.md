# 🚀 Setup & Usage Guide - Hazard Map Feature

## 📋 Prasyarat

- Python 3.8+
- Flask 3.0.0+
- Flask-SocketIO 5.3.6+
- Modern browser dengan support:
  - Geolocation API
  - WebSocket
  - Canvas
  - Video/MediaDevices

## 🔧 Setup Hazard Map

### 1. Update Dependencies (Sudah included)

```bash
pip install flask flask-socketio gevent-websocket
```

### 2. Database Inisialisasi

Database `potholes.db` akan **otomatis dibuat** saat app pertama kali dijalankan:

```python
# Terjadi otomatis di app.py:
if __name__ == '__main__':
    init_db()  # Create tables
    socketio.run(app, host='0.0.0.0', port=5000)
```

### 3. Verifikasi Database

Database akan terlihat di:

```
d:\projek\VISKOM_CintaDamai\potholes.db
```

Untuk inspect database:

```bash
# Menggunakan sqlite3 CLI
sqlite3 potholes.db

# Query potholes
sqlite> SELECT * FROM potholes;
sqlite> SELECT * FROM user_locations;
```

---

## 🎯 Fitur & Cara Penggunaan

### Mode 1: Live Detection dengan GPS

1. **Buka Aplikasi**

   ```
   http://localhost:5000
   ```

2. **Klik "Buka Kamera"**
   - Browser akan minta akses kamera
   - Browser akan minta akses GPS

3. **Klik "Mulai Deteksi"**
   - Live detection dimulai
   - GPS coordinates akan dikirim setiap deteksi
   - Pothole yang terdeteksi disimpan ke database dengan koordinat

4. **Buka Hazard Map**
   - Klik button "Hazard Map" di header
   - Atau: `http://localhost:5000/hazard-map`
   - Peta akan menampilkan semua pothole yang terdeteksi

### Mode 2: Upload Gambar dengan Coordinates

1. **Di halaman Detection, pilih "Upload"**
2. **Upload gambar jalan**
3. **Manual add ke Hazard Map:**
   ```
   POST /api/hazard-map/add
   {
     "latitude": -6.2088,
     "longitude": 106.8456,
     "confidence": 0.75,
     "severity": "medium"
   }
   ```

### Mode 3: Hazard Map Exploration

1. **Akses Hazard Map**
   - Klik button "Hazard Map" atau `/hazard-map`

2. **Enable Tracking**
   - Klik icon satellite (<i class="fas fa-satellite-dish"></i>)
   - Browser akan minta akses GPS
   - GPS status akan muncul di kiri bawah

3. **Fitur Peta**
   - **Zoom**: Mouse wheel atau pinch
   - **Pan**: Drag peta
   - **Click Marker**: Lihat detail pothole
   - **Refresh**: Update data terbaru
   - **My Location**: Center pada posisi user

4. **Proximity Alerts**
   - Saat user mendekati pothole dalam radius
   - Notifikasi akan muncul dari atas
   - Alert berisi jarak dan severity

---

## 📊 API Contoh & Response

### Get All Potholes

```bash
curl -X GET http://localhost:5000/api/hazard-map/potholes
```

Response:

```json
{
  "success": true,
  "potholes": [
    {
      "id": 1,
      "latitude": -6.2088,
      "longitude": 106.8456,
      "confidence": 0.85,
      "timestamp": "2024-05-12 10:30:15",
      "severity": "high"
    }
  ],
  "total": 1
}
```

### Check Proximity

```bash
curl -X POST http://localhost:5000/api/hazard-map/nearby \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -6.2088,
    "longitude": 106.8456,
    "speed": 25.5,
    "accuracy": 30
  }'
```

Response:

```json
{
  "success": true,
  "dynamic_radius_km": 0.127,
  "alerts": [
    {
      "id": 1,
      "distance_m": 45.2,
      "severity": "high",
      "confidence": 0.85
    }
  ],
  "alert_count": 1
}
```

### Add Pothole Manual

```bash
curl -X POST http://localhost:5000/api/hazard-map/add \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -6.2090,
    "longitude": 106.8460,
    "confidence": 0.75,
    "severity": "medium"
  }'
```

---

## 🔨 Customization

### A. Mengubah Default Radius

Edit `app.py` baris ~80:

```python
def get_hazard_map_nearby():
    # ...
    base_radius = 0.05  # 50 meter = 0.05 km

    # Untuk 100 meter default:
    base_radius = 0.1

    # Untuk 25 meter default:
    base_radius = 0.025
```

### B. Mengubah Sensitivity Radius Terhadap Speed

Edit `app.py` baris ~85:

```python
# Default: 50 km/h = 1x multiplier
speed_factor = max(1, speed / 50)

# Lebih sensitif (radius berkembang lebih cepat):
speed_factor = max(1, speed / 30)

# Kurang sensitif (radius berkembang lambat):
speed_factor = max(1, speed / 100)
```

### C. Mengubah Map Tile Provider

Edit `hazard_map.html` baris ~440:

```javascript
// OpenStreetMap (default - umum digunakan)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap contributors",
});

// Alternatif: OpenTopoMap (terrain)
L.tileLayer("https://tile.opentopomap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenTopoMap contributors",
});

// Alternatif: Stamen Toner (hitam-putih, minimalis)
L.tileLayer("https://tile.stamen.com/toner/{z}/{x}/{y}.png", {
  attribution: "&copy; Stamen Design",
});

// Alternatif: Satellite (ESRI)
L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    attribution: "&copy; ESRI, DigitalGlobe",
  },
);
```

### D. Alert Notification Timeout

Edit `hazard_map.html` baris ~680:

```javascript
// Notifications hilang setelah 5 detik (default)
setTimeout(() => {
  alertEl.remove();
}, 5000);

// Untuk 10 detik:
setTimeout(() => {
  alertEl.remove();
}, 10000);
```

---

## 🐛 Troubleshooting

### Problem: GPS tidak aktif

**Penyebab:**

- Aplikasi tidak running di HTTPS atau localhost
- Browser tidak memiliki permission untuk GPS
- Device GPS tidak aktif

**Solusi:**

1. Pastikan akses via `http://localhost:5000` atau HTTPS
2. Check browser permission (Settings > Privacy > Location)
3. Aktifkan GPS di device (mobile)
4. Check browser console untuk error messages

### Problem: Potholes tidak muncul di Hazard Map

**Penyebab:**

- Database tidak ada atau kosong
- Server tidak running
- API endpoint error

**Solusi:**

```bash
# Check database
sqlite3 potholes.db "SELECT COUNT(*) FROM potholes;"

# Check server logs - lihat terminal saat app running
# Error akan ditampilkan di console

# Manual add test pothole
curl -X POST http://localhost:5000/api/hazard-map/add \
  -H "Content-Type: application/json" \
  -d '{"latitude":-6.2088,"longitude":106.8456,"confidence":0.8}'
```

### Problem: Radius tidak berubah dinamis

**Penyebab:**

- Speed tidak dikirim dari client
- GPS data tidak akurat

**Solusi:**

1. Check GPS status widget di Hazard Map
2. Pastikan speed tidak null (gerakkan device)
3. Check browser console untuk GPS data
4. Test dengan kecepatan yang berbeda (drive/walk)

### Problem: Performance lag di Hazard Map

**Penyebab:**

- Banyak marker di peta
- Rendering overhead

**Solusi:**

1. Zoom ke area dengan pothole sedikit
2. Implement marker clustering (future feature)
3. Reduce update frequency
4. Use lower resolution tile layer

---

## 🔗 Integration Points

### Frontend to Backend

- `http://localhost:5000/hazard-map` - Halaman map
- WebSocket: GPS data dikirim per frame via `stream_frame`

### Database Queries

- Potholes stored via `add_pothole()` function
- Retrieved via `get_all_potholes()` & `get_nearby_potholes()`

### Real-time Updates

- WebSocket event: `hazard_map_update` broadcast ke clients
- Automatic map refresh every 10 seconds

---

## 📱 Mobile Considerations

### iOS Safari

- Require HTTPS untuk GPS & camera
- Location permission harus diminta first time
- No service worker support untuk caching

### Android Chrome

- Works dengan HTTP localhost
- Camera & GPS permission request otomatis
- Better support untuk geolocation

### Firefox Mobile

- Full support untuk semua feature
- Good GPS accuracy

---

## 🚨 Security Notes

1. **GPS Data Privacy**
   - User coordinates disimpan di database
   - Implement authentication untuk sensitive data
   - Consider user privacy concerns

2. **Database Access**
   - SQLite tidak cocok untuk production
   - Migrate ke PostgreSQL/MySQL untuk deployment
   - Implement database encryption

3. **API Endpoints**
   - Add rate limiting untuk API
   - Implement CORS policy
   - Add user authentication

---

## 📈 Performance Tips

1. **Reduce Marker Count**
   - Filter by date range
   - Show only recent potholes
   - Implement clustering

2. **Optimize WebSocket**
   - Reduce stream frame rate
   - Compress GPS data
   - Batch updates

3. **Map Rendering**
   - Use lighter tile provider
   - Reduce map redraws
   - Implement viewport-based rendering

---

## 🎓 Next Steps

1. **Test Coverage**
   - Add unit tests untuk API endpoints
   - Test GPS accuracy di berbagai device

2. **Feature Enhancement**
   - Heat map visualization
   - Historical trend analysis
   - Community pothole reporting

3. **Deployment**
   - Move to production database
   - Setup HTTPS/SSL
   - Configure cloud hosting
   - Implement CDN untuk map tiles

---

## 📞 Support & Questions

Untuk pertanyaan atau issues:

1. Check console logs di browser (F12)
2. Check terminal logs saat app running
3. Verify database dengan sqlite3
4. Test API endpoints dengan curl/Postman

---

**Last Updated**: May 12, 2024
**Version**: 1.0
**Status**: Production Ready ✅
