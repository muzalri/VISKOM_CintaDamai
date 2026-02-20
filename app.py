"""
Aplikasi Web Pendeteksi Jalan Berlubang (Pothole Detection)
VISKOM - Cinta Damai

Menggunakan Flask + YOLOv8 + WebSocket untuk deteksi real-time
"""

import os
import uuid
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from detector.pothole_detector import PotholeDetector

# ============================================================
# Konfigurasi Aplikasi
# ============================================================
app = Flask(__name__)
app.config['SECRET_KEY'] = 'viskom-cinta-damai-2024'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['RESULT_FOLDER'] = os.path.join(os.path.dirname(__file__), 'results')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp', 'bmp'}

# Inisialisasi SocketIO untuk real-time communication
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Buat folder jika belum ada
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

# Inisialisasi Detector
detector = PotholeDetector()

# Riwayat deteksi
detection_history = []


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
    total_potholes = sum(d['num_potholes'] for d in detection_history)

    return jsonify({
        'success': True,
        'total_scans': total,
        'total_detected': detected,
        'total_potholes': total_potholes,
        'detection_rate': round((detected / total * 100), 1) if total > 0 else 0
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


# ============================================================
# Main
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  POTHOLE DETECTION - VISKOM Cinta Damai")
    print("  Aplikasi Pendeteksi Jalan Berlubang")
    print("=" * 60)
    print(f"  Upload folder : {app.config['UPLOAD_FOLDER']}")
    print(f"  Result folder : {app.config['RESULT_FOLDER']}")
    print(f"  Model loaded  : {detector.model is not None}")
    print("=" * 60)

    # Jalankan server dengan WebSocket support
    # Gunakan host='0.0.0.0' agar bisa diakses dari HP
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
