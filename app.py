"""
Aplikasi Web Pendeteksi Jalan Berlubang (Pothole Detection)
VISKOM - Cinta Damai

Menggunakan Flask + YOLOv8 + WebSocket untuk deteksi real-time
"""

import os
import uuid
import time
import base64
import cv2
import numpy as np
import json
from datetime import datetime
from math import radians, cos, sin, asin, sqrt
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from config import config
from models import db, Pothole, UserLocation, Alert, DetectionHistory
from detector.pothole_detector import PotholeDetector

# ============================================================
# Konfigurasi Aplikasi
# ============================================================
load_dotenv()

app = Flask(__name__)

flask_env = os.environ.get('FLASK_ENV', 'development').lower()
app.config.from_object(config.get(flask_env, config['default']))
db.init_app(app)

# Inisialisasi SocketIO untuk real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Buat folder jika belum ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Inisialisasi Detector
detector = PotholeDetector()

# Riwayat deteksi
detection_history = []


# ============================================================
# Database Functions
# ============================================================
def init_db():
    """Inisialisasi database untuk menyimpan data pothole"""
    with app.app_context():
        db.create_all()


def add_pothole(latitude, longitude, confidence, severity='medium', description='', proximity_radius_km=0.02):
    """
    Tambahkan pothole baru ke database atau update existing dalam radius proximity
    proximity_radius_km: radius dalam km untuk dianggap sebagai lokasi yang sama (default 20 meter)
    """
    try:
        potholes = Pothole.query.order_by(Pothole.id.asc()).all()
        existing_nearby = None

        for pothole in potholes:
            distance = haversine_distance(latitude, longitude, pothole.latitude, pothole.longitude)
            if distance <= proximity_radius_km:
                existing_nearby = pothole
                break

        timestamp = datetime.utcnow()

        if existing_nearby:
            old_confidence = existing_nearby.confidence
            old_severity = existing_nearby.severity

            new_confidence = max(confidence, old_confidence)
            severity_priority = {'high': 3, 'medium': 2, 'low': 1}
            new_severity = old_severity if severity_priority.get(old_severity, 0) >= severity_priority.get(severity, 0) else severity

            existing_nearby.confidence = new_confidence
            existing_nearby.severity = new_severity
            existing_nearby.timestamp = timestamp
            db.session.commit()

            print(f"[DB] Updated existing pothole {existing_nearby.id} at ({latitude:.6f}, {longitude:.6f})")
            return existing_nearby.id

        pothole = Pothole(
            latitude=latitude,
            longitude=longitude,
            confidence=confidence,
            timestamp=timestamp,
            severity=severity,
            description=description,
            user_agent=request.headers.get('User-Agent', 'Unknown')
        )
        db.session.add(pothole)
        db.session.commit()

        print(f"[DB] Created new pothole {pothole.id} at ({latitude:.6f}, {longitude:.6f})")
        return pothole.id
    except Exception as e:
        db.session.rollback()
        print(f"[DB] Error adding pothole: {e}")
        return None


def get_all_potholes():
    """Dapatkan semua pothole dari database"""
    try:
        potholes = Pothole.query.order_by(Pothole.id.asc()).all()
        return [pothole.to_dict() for pothole in potholes]
    except Exception as e:
        print(f"[DB] Error getting potholes: {e}")
        return []


def get_nearby_potholes(latitude, longitude, radius_km=5):
    """Dapatkan pothole yang dekat dengan koordinat tertentu (dalam radius)"""
    try:
        potholes = Pothole.query.order_by(Pothole.id.asc()).all()

        nearby = []
        for pothole in potholes:
            distance = haversine_distance(latitude, longitude, pothole.latitude, pothole.longitude)
            if distance <= radius_km:
                nearby.append({
                    'id': pothole.id,
                    'latitude': pothole.latitude,
                    'longitude': pothole.longitude,
                    'confidence': pothole.confidence,
                    'timestamp': pothole.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    'severity': pothole.severity,
                    'distance_km': round(distance, 3)
                })
        
        return sorted(nearby, key=lambda x: x['distance_km'])
    except Exception as e:
        print(f"[DB] Error getting nearby potholes: {e}")
        return []


def haversine_distance(lat1, lon1, lat2, lon2):
    """Hitung jarak antara dua koordinat GPS (dalam km)"""
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km


def allowed_file(filename):
    """Cek apakah ekstensi file diizinkan"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ============================================================
# Routes
# ============================================================
@app.route('/')
def index():
    """Halaman utama"""
    return render_template('index.html')


@app.route('/hazard-map')
def hazard_map():
    """Halaman Hazard Map - Peta interaktif pothole"""
    return render_template('hazard_map.html')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve file yang diupload"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/results/<filename>')
def result_file(filename):
    """Serve file hasil deteksi"""
    return send_from_directory(app.config['RESULT_FOLDER'], filename)


@app.route('/api/detect', methods=['POST'])
def detect_pothole():
    """
    API endpoint untuk deteksi jalan berlubang.
    Menerima gambar dari kamera HP, memproses, dan mengirim hasilnya.
    """
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'Tidak ada gambar yang dikirim'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'Tidak ada file yang dipilih'}), 400

    if file and allowed_file(file.filename):
        # Generate nama file unik
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        try:
            # Proses deteksi
            result = detector.detect(filepath, app.config['RESULT_FOLDER'])

            # Simpan ke riwayat
            detection_record = {
                'id': len(detection_history) + 1,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'original_image': unique_filename,
                'result_image': result.get('result_image', ''),
                'detected': result['detected'],
                'num_potholes': result['num_potholes'],
                'confidence': result.get('avg_confidence', 0),
                'detections': result.get('detections', [])
            }
            detection_history.append(detection_record)

            # Kirim sinyal real-time via WebSocket jika terdeteksi lubang
            if result['detected']:
                socketio.emit('pothole_alert', {
                    'message': f"⚠️ PERINGATAN: Terdeteksi {result['num_potholes']} lubang jalan!",
                    'num_potholes': result['num_potholes'],
                    'confidence': result.get('avg_confidence', 0),
                    'result_image': f"/results/{result.get('result_image', '')}",
                    'timestamp': detection_record['timestamp']
                })

            return jsonify({
                'success': True,
                'detected': result['detected'],
                'num_potholes': result['num_potholes'],
                'confidence': result.get('avg_confidence', 0),
                'detections': result.get('detections', []),
                'original_image': f"/uploads/{unique_filename}",
                'result_image': f"/results/{result.get('result_image', '')}",
                'message': f"Terdeteksi {result['num_potholes']} lubang jalan!" if result['detected'] else "Tidak ada lubang jalan terdeteksi."
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Error saat memproses gambar: {str(e)}'
            }), 500
    else:
        return jsonify({
            'success': False,
            'message': 'Format file tidak didukung. Gunakan PNG, JPG, JPEG, WEBP, atau BMP.'
        }), 400


@app.route('/api/history', methods=['GET'])
def get_history():
    """Dapatkan riwayat deteksi"""
    return jsonify({
        'success': True,
        'history': list(reversed(detection_history))
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Dapatkan statistik deteksi"""
    total = len(detection_history)
    detected = sum(1 for d in detection_history if d['detected'])
    detection_potholes = sum(d['num_potholes'] for d in detection_history)

    try:
        total_potholes = Pothole.query.count()
    except Exception:
        total_potholes = 0

    return jsonify({
        'success': True,
        'total_scans': total,
        'total_detected': detected,
        'total_potholes': total_potholes,
        'detection_potholes': detection_potholes,
        'detection_rate': round((detected / total * 100), 1) if total > 0 else 0
    })


# ============================================================
# Hazard Map API Endpoints
# ============================================================
@app.route('/api/hazard-map/potholes', methods=['GET'])
def get_hazard_map_potholes():
    """API untuk mendapatkan semua pothole untuk Hazard Map"""
    potholes = get_all_potholes()
    return jsonify({
        'success': True,
        'potholes': potholes,
        'total': len(potholes)
    })


@app.route('/api/hazard-map/nearby', methods=['POST'])
def get_hazard_map_nearby():
    """API untuk mendapatkan pothole yang dekat dengan user (proximity check)"""
    data = request.get_json()
    
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({
            'success': False,
            'message': 'Latitude dan longitude diperlukan'
        }), 400
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    speed = data.get('speed', 0)  # km/h
    accuracy = data.get('accuracy', 30)  # meters
    
    # Hitung radius dinamis berdasarkan kecepatan
    base_radius = 0.05  # 50 meter = 0.05 km
    speed_factor = max(1, speed / 50)  # Semakin cepat, radius semakin besar
    dynamic_radius = base_radius * speed_factor
    
    nearby = get_nearby_potholes(latitude, longitude, dynamic_radius)
    
    # Generate alert jika ada pothole yang sangat dekat
    alerts = []
    for pothole in nearby:
        if pothole['distance_km'] <= dynamic_radius:  # Alert aktif dalam radius penuh
            alerts.append({
                'id': pothole['id'],
                'distance_m': round(pothole['distance_km'] * 1000, 1),
                'severity': pothole['severity'],
                'confidence': pothole['confidence']
            })
    
    return jsonify({
        'success': True,
        'user_location': {
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'accuracy': accuracy
        },
        'dynamic_radius_km': round(dynamic_radius, 4),
        'nearby_potholes': nearby,
        'alerts': alerts,
        'alert_count': len(alerts)
    })


@app.route('/api/hazard-map/add', methods=['POST'])
def add_hazard_map_pothole():
    """API untuk menambahkan pothole baru ke hazard map"""
    data = request.get_json()
    
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({
            'success': False,
            'message': 'Latitude, longitude, dan confidence diperlukan'
        }), 400
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    confidence = data.get('confidence', 0.5)
    severity = data.get('severity', 'medium')
    
    # Tentukan severity berdasarkan confidence
    if confidence > 0.8:
        severity = 'high'
    elif confidence > 0.6:
        severity = 'medium'
    else:
        severity = 'low'
    
    pothole_id = add_pothole(latitude, longitude, confidence, severity)
    
    if pothole_id:
        # Broadcast update ke semua client yang sedang membuka hazard map
        socketio.emit('hazard_map_update', {
            'message': f"Pothole baru terdeteksi: {severity.upper()}",
            'pothole_id': pothole_id,
            'latitude': latitude,
            'longitude': longitude,
            'confidence': confidence,
            'severity': severity
        })
        
        return jsonify({
            'success': True,
            'pothole_id': pothole_id,
            'message': 'Pothole berhasil ditambahkan ke Hazard Map'
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': 'Gagal menambahkan pothole'
        }), 500


@app.route('/api/hazard-map/stats', methods=['GET'])
def get_hazard_map_stats():
    """API untuk mendapatkan statistik Hazard Map"""
    potholes = get_all_potholes()
    
    high_severity = len([p for p in potholes if p['severity'] == 'high'])
    medium_severity = len([p for p in potholes if p['severity'] == 'medium'])
    low_severity = len([p for p in potholes if p['severity'] == 'low'])
    
    avg_confidence = np.mean([p['confidence'] for p in potholes]) if potholes else 0
    
    return jsonify({
        'success': True,
        'total_potholes': len(potholes),
        'high_severity': high_severity,
        'medium_severity': medium_severity,
        'low_severity': low_severity,
        'average_confidence': round(float(avg_confidence), 3)
    })


# ============================================================
# WebSocket Events
# ============================================================
@socketio.on('connect')
def handle_connect():
    """Handle koneksi WebSocket baru"""
    print(f"[WS] Client terhubung: {request.sid}")
    emit('connected', {'message': 'Terhubung ke server deteksi jalan berlubang'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle diskoneksi WebSocket"""
    print(f"[WS] Client terputus: {request.sid}")


@socketio.on('request_status')
def handle_status_request():
    """Handle permintaan status"""
    emit('server_status', {
        'status': 'online',
        'model_loaded': detector.model is not None,
        'total_detections': len(detection_history)
    })


@socketio.on('stream_frame')
def handle_stream_frame(data):
    """
    Handle frame dari streaming kamera real-time.
    Mode lightweight: hanya kirim koordinat deteksi, bounding box digambar di client.
    """
    try:
        # Decode base64 image
        img_data = data.get('image', '')
        if ',' in img_data:
            img_data = img_data.split(',')[1]

        img_bytes = base64.b64decode(img_data)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            emit('stream_result', {'success': False, 'message': 'Gagal decode frame'})
            return

        # Proses deteksi - lightweight mode (tanpa render annotated image)
        result = detector.detect_frame(frame, lightweight=True)

        # Kirim sinyal alert jika terdeteksi lubang
        if result['detected']:
            socketio.emit('pothole_alert', {
                'message': f"⚠️ PERINGATAN: Terdeteksi {result['num_potholes']} lubang jalan!",
                'num_potholes': result['num_potholes'],
                'confidence': result.get('avg_confidence', 0),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Jika ada GPS data dalam stream, simpan koordinat pothole
            gps_data = data.get('gps', None)
            if gps_data and result['detections']:
                for detection in result['detections']:
                    pothole_id = add_pothole(
                        latitude=gps_data.get('latitude'),
                        longitude=gps_data.get('longitude'),
                        confidence=detection.get('confidence', 0.5),
                        severity='high' if detection.get('confidence', 0) > 0.7 else 'medium',
                        description=f"Live detection - Confidence: {detection.get('confidence', 0):.0%}"
                    )

                    if pothole_id:
                        socketio.emit('hazard_map_update', {
                            'message': 'Pothole baru berhasil ditambahkan',
                            'pothole_id': pothole_id,
                            'latitude': gps_data.get('latitude'),
                            'longitude': gps_data.get('longitude'),
                            'confidence': detection.get('confidence', 0.5),
                            'severity': 'high' if detection.get('confidence', 0) > 0.7 else 'medium'
                        })

        # Kirim HANYA koordinat deteksi (ringan, tanpa image)
        emit('stream_result', {
            'success': True,
            'detected': result['detected'],
            'num_potholes': result['num_potholes'],
            'confidence': result.get('avg_confidence', 0),
            'detections': result.get('detections', []),
            'frame_width': result.get('frame_width', 0),
            'frame_height': result.get('frame_height', 0),
            'method': result.get('method', 'AI'),
            'message': f"Terdeteksi {result['num_potholes']} lubang jalan!" if result['detected'] else "Tidak ada lubang jalan terdeteksi."
        })

    except Exception as e:
        print(f"[STREAM] Error: {e}")
        emit('stream_result', {'success': False, 'message': str(e)})


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    # Inisialisasi database
    init_db()
    
    print("=" * 60)
    print("  POTHOLE DETECTION - VISKOM Cinta Damai")
    print("  Aplikasi Pendeteksi Jalan Berlubang")
    print("=" * 60)
    print(f"  Upload folder : {app.config['UPLOAD_FOLDER']}")
    print(f"  Result folder : {app.config['RESULT_FOLDER']}")
    print(f"  Model loaded  : {detector.model is not None}")
    print(f"  Database      : MySQL via SQLAlchemy ({app.config.get('SQLALCHEMY_DATABASE_URI', 'not set').split('@')[-1] if '@' in app.config.get('SQLALCHEMY_DATABASE_URI', '') else 'configured'})")
    print("=" * 60)

    # Jalankan server dengan WebSocket support
    # Gunakan host='0.0.0.0' agar bisa diakses dari HP
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
