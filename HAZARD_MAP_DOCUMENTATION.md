# 🗺️ Hazard Map - Fitur Peta Lubang Jalan Interaktif

## 📋 Ringkasan Fitur

Hazard Map adalah fitur peta interaktif yang menampilkan lokasi-lokasi lubang jalan (pothole) yang terdeteksi dengan sistem proximity alert dan radius dinamis berdasarkan kecepatan pengguna.

### Fitur Utama:

1. **🗺️ Peta Interaktif (Leaflet Maps)**
   - Visualisasi real-time lokasi pothole
   - Integrasi GPS untuk tracking user
   - Zoom, pan, dan navigasi peta
   - Marker dinamis dengan warna berdasarkan severity

2. **⚠️ Proximity Alert System**
   - Deteksi ketika user mendekati pothole
   - Alert otomatis dengan notification
   - Jarak real-time dalam meter

3. **📊 Dynamic Radius Calculator**
   - Radius alert bervariasi berdasarkan kecepatan user
   - Formula: `radius_km = 0.05 * (speed_kmh / 50)`
   - Range: 50 meter (idle) hingga 250+ meter (high speed)

4. **📱 GPS Tracking**
   - Real-time location tracking (watchPosition)
   - Accuracy display
   - Speed calculation
   - Status indicator

5. **📈 Statistik & Analytics**
   - Total pothole count
   - Severity breakdown (High/Medium/Low)
   - Average confidence scores
   - Potholes terdekat

---

## 🚀 Cara Menggunakan

### Akses Hazard Map

1. **Dari Halaman Utama**
   - Klik tombol "Hazard Map" di header
   - atau akses langsung: `http://your-server:5000/hazard-map`

2. **Tracking Mode**
   - Klik tombol satelit (<i class="fas fa-satellite-dish"></i>) untuk activate GPS tracking
   - Browser akan meminta permission untuk akses lokasi
   - Status GPS ditampilkan di kiri bawah

### Fitur Peta

- **Zoom**: Gunakan mouse wheel atau pinch gesture
- **Pan**: Drag peta untuk menggeser
- **Lokasi Saya**: Klik lokasi crosshairs untuk center map pada posisi current
- **Refresh**: Klik refresh untuk memperbarui data pothole
- **Info Pothole**: Klik marker untuk lihat detail pothole

### Alert Notification

Ketika user berada dalam radius proximity dari pothole:

- **Animasi**: Notifikasi slide down dari atas
- **Info**: Jarak pothole, severity level, confidence
- **Auto-dismiss**: Notifikasi hilang setelah 5 detik

---

## 📡 API Endpoints

### 1. Get All Potholes

```
GET /api/hazard-map/potholes
```

**Response:**

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

### 2. Check Nearby Potholes (Proximity)

```
POST /api/hazard-map/nearby
Content-Type: application/json

{
  "latitude": -6.2088,
  "longitude": 106.8456,
  "speed": 25.5,
  "accuracy": 30
}
```

**Response:**

```json
{
  "success": true,
  "user_location": {
    "latitude": -6.2088,
    "longitude": 106.8456,
    "speed": 25.5,
    "accuracy": 30
  },
  "dynamic_radius_km": 0.127,
  "nearby_potholes": [
    {
      "id": 1,
      "latitude": -6.209,
      "longitude": 106.846,
      "confidence": 0.85,
      "timestamp": "2024-05-12 10:30:15",
      "severity": "high",
      "distance_km": 0.045
    }
  ],
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

### 3. Add New Pothole

```
POST /api/hazard-map/add
Content-Type: application/json

{
  "latitude": -6.2088,
  "longitude": 106.8456,
  "confidence": 0.75,
  "severity": "medium"
}
```

### 4. Get Hazard Map Statistics

```
GET /api/hazard-map/stats
```

**Response:**

```json
{
  "success": true,
  "total_potholes": 10,
  "high_severity": 3,
  "medium_severity": 5,
  "low_severity": 2,
  "average_confidence": 0.78
}
```

---

## 🎨 Severity Levels & Colors

| Severity   | Color               | Range             | Meaning                     |
| ---------- | ------------------- | ----------------- | --------------------------- |
| **High**   | 🔴 Red (#FF6B6B)    | > 80% confidence  | Critical - Immediate hazard |
| **Medium** | 🟠 Orange (#FFA500) | 60-80% confidence | Warning - Caution advised   |
| **Low**    | 🟡 Yellow (#FFD93D) | < 60% confidence  | Info - Minor pothole        |

---

## 🔄 Dynamic Radius Formula

```
Speed (km/h) | Radius (m) | Safe Distance
0-20         | 50m        | Very close
20-50        | 75m        | Close
50-100       | 150m       | Moderate
100+         | 250m+      | Far ahead warning
```

### Rumus Perhitungan:

```
base_radius = 0.05 km (50 meter)
speed_factor = max(1, speed_kmh / 50)
dynamic_radius = base_radius * speed_factor
```

---

## 🗄️ Database Schema

### Tabel: potholes

```sql
CREATE TABLE potholes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  confidence REAL NOT NULL,
  timestamp TEXT NOT NULL,
  severity TEXT NOT NULL,
  description TEXT,
  user_agent TEXT
)
```

### Tabel: user_locations

```sql
CREATE TABLE user_locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  latitude REAL NOT NULL,
  longitude REAL NOT NULL,
  speed REAL,
  timestamp TEXT NOT NULL,
  accuracy REAL
)
```

---

## 🔌 WebSocket Events

### Client → Server

**Stream Frame dengan GPS Data**

```javascript
socket.emit("stream_frame", {
  image: base64Image,
  gps: {
    latitude: -6.2088,
    longitude: 106.8456,
    speed: 25.5,
    accuracy: 30,
  },
});
```

### Server → Client

**Hazard Map Update**

```javascript
socket.on("hazard_map_update", (data) => {
  // data: {
  //   message: "Pothole baru terdeteksi: HIGH",
  //   pothole_id: 1,
  //   latitude: -6.2088,
  //   longitude: 106.8456,
  //   confidence: 0.85,
  //   severity: "high"
  // }
});
```

---

## 📍 Integrasi GPS Streaming

### Mengirim Deteksi dengan GPS Data

```javascript
// Dari live detection
socket.emit("stream_frame", {
  image: canvasDataUrl,
  gps: {
    latitude: userLat,
    longitude: userLon,
    speed: speedMsToKmh,
    accuracy: gpsAccuracy,
  },
});
```

Ketika pothole terdeteksi dengan GPS data, koordinat langsung disimpan ke database dan broadcast ke semua client yang mengakses Hazard Map.

---

## 🛠️ Customization

### Mengubah Base Radius

Edit file `app.py` baris: `base_radius = 0.05`

```python
# Untuk radius 100 meter default:
base_radius = 0.1  # 100 meter = 0.1 km
```

### Mengubah Speed Factor

```python
# Default: 1 speed unit = 50 km/h
# Untuk sensitivity lebih tinggi:
speed_factor = max(1, speed / 30)  # Lebih sensitif
speed_factor = max(1, speed / 100) # Lebih tidak sensitif
```

### Custom Map Tile

Edit `hazard_map.html` baris dengan L.tileLayer:

```javascript
// OpenStreetMap (default)
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png");

// Stamen Terrain
L.tileLayer("https://tile.opentopomap.org/{z}/{x}/{y}.png");

// Satellite
L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
);
```

---

## 🐛 Troubleshooting

### GPS Tidak Aktif

- Pastikan HTTPS atau localhost (GPS hanya bekerja di secure context)
- Izinkan browser untuk akses lokasi
- Check browser console untuk error messages

### Potholes Tidak Muncul di Map

- Refresh halaman
- Check koneksi ke server API
- Lihat console untuk network errors
- Verify database potholes.db ada

### Radius Tidak Berubah Dinamis

- Pastikan device mengirim speed data
- Check GPS accuracy dan speed dari gpsStatus widget
- Test dengan berbagai kecepatan pergerakan

### Performance Issues

- Limit number of markers displayed (reduce zoom level)
- Implement marker clustering untuk banyak data
- Reduce map update frequency

---

## 🔮 Future Enhancements

1. **Marker Clustering**
   - Combine nearby markers untuk better performance
   - Show cluster count

2. **Historical Heat Map**
   - Visualisasi area dengan banyak pothole
   - Time-range filtering

3. **Route Optimization**
   - Suggest routes yang avoid pothole areas
   - Integration dengan routing service

4. **Community Reporting**
   - Allow users untuk report baru pothole
   - Voting system untuk verify pothole

5. **Mobile App**
   - Native Android/iOS app
   - Background tracking capability
   - Push notifications

6. **Integration Tracking**
   - Send alert ke driver/fleet management
   - Real-time tracking dashboard

---

## 📝 License

VISKOM Cinta Damai - 2024

---

## 👥 Support

Untuk pertanyaan atau issue, hubungi tim development VISKOM.
