# 🛣️ Pothole Detector - Sistem Deteksi Jalan Berlubang

**VISKOM Cinta Damai** - Aplikasi web pendeteksi jalan berlubang menggunakan Computer Vision

## 📋 Fitur

- 📸 **Akses Kamera HP** - Ambil foto langsung dari kamera smartphone (preferensi kamera belakang)
- 📤 **Upload Gambar** - Upload gambar jalan dari galeri/file
- 🤖 **Deteksi AI** - Proses deteksi menggunakan YOLOv8 atau OpenCV
- 🔔 **Real-time Alert** - Notifikasi langsung via WebSocket jika terdeteksi lubang jalan
- 📊 **Dashboard** - Statistik dan riwayat deteksi
- 📱 **Responsive** - Tampilan optimal di HP maupun desktop

## 🏗️ Arsitektur

```
Kamera HP → Capture/Upload → Flask Server → AI Detection → WebSocket Alert
                                   ↓
                              YOLOv8 / OpenCV
                                   ↓
                         Bounding Box + Confidence
                                   ↓
                         Kirim Sinyal ke User
```

## 📁 Struktur Proyek

```
VISKOM_CintaDamai/
├── app.py                          # Server Flask utama
├── requirements.txt                # Dependencies Python
├── detector/
│   ├── __init__.py
│   └── pothole_detector.py         # Modul deteksi AI
├── model/
│   └── (pothole_best.pt)           # Model YOLOv8 (opsional)
├── static/
│   ├── css/
│   │   └── style.css               # Stylesheet
│   └── js/
│       └── app.js                  # Frontend JavaScript
├── templates/
│   └── index.html                  # Halaman utama
├── uploads/                        # Gambar yang diupload (auto-generated)
└── results/                        # Gambar hasil deteksi (auto-generated)
```

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
# Buat virtual environment (opsional tapi disarankan)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Server

```bash
python app.py
```

Server akan berjalan di `http://0.0.0.0:5000`

### 3. Akses dari HP

1. Pastikan HP dan komputer/laptop **dalam jaringan WiFi yang sama**
2. Cari IP komputer: jalankan `ipconfig` (Windows) atau `ifconfig` (Linux/Mac)
3. Buka browser di HP, ketik: `http://<IP-KOMPUTER>:5000`
   - Contoh: `http://192.168.1.100:5000`

> ⚠️ **Catatan**: Untuk akses kamera di HP, beberapa browser memerlukan koneksi HTTPS. Jika kamera tidak bisa diakses, gunakan fitur upload gambar sebagai alternatif.

## 🤖 Mode Deteksi

### Mode 1: YOLOv8 (Rekomendasi)

Untuk akurasi terbaik, gunakan model YOLOv8 yang sudah di-training untuk deteksi pothole:

1. Download atau training model pothole detection
2. Letakkan file model (`.pt`) di folder `model/`
3. Rename menjadi `pothole_best.pt` atau `best.pt`
4. Restart server

**Training model sendiri:**

```python
from ultralytics import YOLO

# Load pre-trained model
model = YOLO('yolov8n.pt')

# Training dengan dataset pothole
results = model.train(
    data='pothole_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

Dataset pothole bisa didapat dari:

- [Roboflow Pothole Dataset](https://universe.roboflow.com/search?q=pothole)
- [Kaggle Pothole Dataset](https://www.kaggle.com/search?q=pothole+detection)

### Mode 2: OpenCV (Fallback)

Jika tidak ada model YOLOv8, sistem otomatis menggunakan deteksi OpenCV yang menganalisis:

- **Area gelap** pada gambar (lubang cenderung gelap)
- **Edge detection** (tepian lubang)
- **Contour analysis** (bentuk lubang)
- **Texture analysis** (variasi permukaan)

## 🔧 Alur Kerja Sistem

1. **User** membuka web di HP dan mengambil foto jalan
2. **Frontend** mengirim gambar ke server via HTTP POST
3. **Server** memproses gambar dengan AI (YOLOv8/OpenCV)
4. **Detector** menganalisis gambar dan menandai area berlubang
5. **Server** mengirim hasil kembali ke user + **sinyal WebSocket** jika terdeteksi lubang
6. **Frontend** menampilkan hasil + **alert notification** real-time

## 🌐 API Endpoints

| Method | Endpoint       | Deskripsi               |
| ------ | -------------- | ----------------------- |
| GET    | `/`            | Halaman utama           |
| POST   | `/api/detect`  | Upload & deteksi gambar |
| GET    | `/api/history` | Riwayat deteksi         |
| GET    | `/api/stats`   | Statistik deteksi       |

### Contoh Response `/api/detect`

```json
{
  "success": true,
  "detected": true,
  "num_potholes": 2,
  "confidence": 0.78,
  "detections": [
    {
      "bbox": [120, 200, 350, 400],
      "confidence": 0.85,
      "class": "pothole",
      "width": 230,
      "height": 200
    }
  ],
  "result_image": "/results/result_abc123.jpg",
  "message": "Terdeteksi 2 lubang jalan!"
}
```

## 📡 WebSocket Events

| Event            | Direction       | Deskripsi               |
| ---------------- | --------------- | ----------------------- |
| `connect`        | Client → Server | Koneksi baru            |
| `connected`      | Server → Client | Konfirmasi koneksi      |
| `pothole_alert`  | Server → Client | Alert lubang terdeteksi |
| `request_status` | Client → Server | Request status server   |
| `server_status`  | Server → Client | Response status         |

## 🛠️ Teknologi

- **Backend**: Python, Flask, Flask-SocketIO
- **AI/CV**: YOLOv8 (Ultralytics), OpenCV, NumPy
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Real-time**: WebSocket (Socket.IO)
- **Camera**: HTML5 MediaDevices API

## 📝 Lisensi

Proyek ini dibuat untuk keperluan mata kuliah **Visi Komputer (VISKOM)** - Tim Cinta Damai.
