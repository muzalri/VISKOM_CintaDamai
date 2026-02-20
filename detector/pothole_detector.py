"""
Modul Deteksi Jalan Berlubang (Pothole Detector)
Menggunakan YOLOv8 untuk deteksi objek

Jika model YOLOv8 belum ditraining khusus untuk pothole,
modul ini akan menggunakan teknik Computer Vision tradisional
(OpenCV) sebagai fallback.
"""

import os
import cv2
import numpy as np
from datetime import datetime


class PotholeDetector:
    """
    Kelas untuk mendeteksi jalan berlubang pada gambar.
    
    Mendukung 2 mode:
    1. YOLOv8 (jika model tersedia) - lebih akurat
    2. OpenCV Traditional CV (fallback) - tanpa model training
    """

    def __init__(self, model_path=None):
        """
        Inisialisasi detector.
        
        Args:
            model_path: Path ke model YOLOv8 (.pt file). 
                       Jika None, akan coba load default atau gunakan OpenCV.
        """
        self.model = None
        self.model_type = 'opencv'  # default fallback
        self.confidence_threshold = 0.35

        # Coba load model YOLOv8
        if model_path and os.path.exists(model_path):
            self._load_yolo_model(model_path)
        else:
            # Coba cari model di folder default
            default_paths = [
                os.path.join(os.path.dirname(__file__), '..', 'model', 'pothole_best.pt'),
                os.path.join(os.path.dirname(__file__), '..', 'model', 'best.pt'),
                os.path.join(os.path.dirname(__file__), '..', 'runs', 'detect', 'train', 'weights', 'best.pt'),
            ]
            for path in default_paths:
                if os.path.exists(path):
                    self._load_yolo_model(path)
                    break

        if self.model is None:
            print("[DETECTOR] Model YOLOv8 tidak ditemukan. Menggunakan deteksi OpenCV.")
            print("[DETECTOR] Untuk hasil lebih baik, letakkan model .pt di folder 'model/'")
        else:
            print(f"[DETECTOR] Model YOLOv8 berhasil dimuat! Mode: {self.model_type}")

    def _load_yolo_model(self, model_path):
        """Load model YOLOv8"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.model_type = 'yolo'
            print(f"[DETECTOR] YOLOv8 model loaded dari: {model_path}")
        except ImportError:
            print("[DETECTOR] ultralytics belum terinstall. Jalankan: pip install ultralytics")
            self.model = None
        except Exception as e:
            print(f"[DETECTOR] Gagal load model YOLOv8: {e}")
            self.model = None

    def detect(self, image_path, result_folder):
        """
        Deteksi jalan berlubang pada gambar.
        
        Args:
            image_path: Path ke file gambar
            result_folder: Folder untuk menyimpan hasil
            
        Returns:
            dict: Hasil deteksi berisi detected, num_potholes, detections, dll.
        """
        if self.model_type == 'yolo' and self.model is not None:
            return self._detect_yolo(image_path, result_folder)
        else:
            return self._detect_opencv(image_path, result_folder)

    def _detect_yolo(self, image_path, result_folder):
        """Deteksi menggunakan YOLOv8"""
        # Jalankan inferensi
        results = self.model(image_path, conf=self.confidence_threshold)

        # Baca gambar asli untuk anotasi
        img = cv2.imread(image_path)
        detections = []

        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    # Koordinat bounding box
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                    confidence = float(box.conf[0].cpu().numpy())
                    class_id = int(box.cls[0].cpu().numpy())

                    detections.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': round(confidence, 3),
                        'class': 'pothole',
                        'width': int(x2 - x1),
                        'height': int(y2 - y1)
                    })

                    # Gambar bounding box
                    color = (0, 0, 255)  # Merah
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)

                    # Label
                    label = f"Lubang {confidence:.0%}"
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
                    cv2.rectangle(img, (x1, y1 - label_size[1] - 10),
                                  (x1 + label_size[0], y1), color, -1)
                    cv2.putText(img, label, (x1, y1 - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Tambahkan info di gambar
        num_potholes = len(detections)
        self._add_info_overlay(img, num_potholes, detections)

        # Simpan hasil
        result_filename = f"result_{os.path.basename(image_path)}"
        result_path = os.path.join(result_folder, result_filename)
        cv2.imwrite(result_path, img)

        avg_conf = np.mean([d['confidence'] for d in detections]) if detections else 0

        return {
            'detected': num_potholes > 0,
            'num_potholes': num_potholes,
            'detections': detections,
            'result_image': result_filename,
            'avg_confidence': round(float(avg_conf), 3),
            'method': 'YOLOv8'
        }

    def _detect_opencv(self, image_path, result_folder):
        """
        Deteksi menggunakan teknik Computer Vision tradisional (OpenCV).
        Menggunakan kombinasi edge detection, contour analysis, dan
        analisis warna untuk mendeteksi area yang kemungkinan lubang jalan.
        """
        # Baca gambar
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Tidak dapat membaca gambar: {image_path}")

        original = img.copy()
        height, width = img.shape[:2]

        # ====== PREPROCESSING ======
        # Resize jika terlalu besar
        max_dim = 800
        scale = 1
        if max(height, width) > max_dim:
            scale = max_dim / max(height, width)
            img = cv2.resize(img, None, fx=scale, fy=scale)
            height, width = img.shape[:2]

        # Convert ke berbagai color space
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

        # ====== DETEKSI AREA GELAP (Lubang biasanya gelap) ======
        # Adaptive thresholding
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        adaptive_thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 21, 8
        )

        # Otsu thresholding
        _, otsu_thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Area gelap berdasarkan HSV (Value rendah = gelap)
        dark_mask = cv2.inRange(hsv, (0, 0, 0), (180, 255, 100))

        # Kombinasikan mask
        combined_mask = cv2.bitwise_or(adaptive_thresh, dark_mask)
        combined_mask = cv2.bitwise_and(combined_mask, otsu_thresh)

        # ====== EDGE DETECTION ======
        edges = cv2.Canny(blur, 50, 150)
        edges_dilated = cv2.dilate(edges, np.ones((3, 3), np.uint8), iterations=2)

        # Gabungkan edge dengan mask
        final_mask = cv2.bitwise_or(combined_mask, edges_dilated)

        # ====== MORPHOLOGICAL OPERATIONS ======
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel, iterations=3)
        final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel, iterations=2)

        # ====== CONTOUR DETECTION ======
        contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        min_area = (width * height) * 0.005  # Min 0.5% dari gambar
        max_area = (width * height) * 0.40  # Max 40% dari gambar

        for contour in contours:
            area = cv2.contourArea(contour)

            # Filter berdasarkan ukuran
            if area < min_area or area > max_area:
                continue

            # Bounding box
            x, y, w, h = cv2.boundingRect(contour)

            # Filter rasio aspek (lubang biasanya tidak terlalu panjang/tipis)
            aspect_ratio = w / h if h > 0 else 0
            if aspect_ratio > 5 or aspect_ratio < 0.2:
                continue

            # Hitung "kebulatan" kontur
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0

            # Analisis kegelapan area
            roi_gray = gray[y:y + h, x:x + w]
            mean_intensity = np.mean(roi_gray)

            # Analisis tekstur (standar deviasi intensitas)
            std_intensity = np.std(roi_gray)

            # Hitung confidence berdasarkan fitur
            confidence = self._calculate_confidence(
                area, width * height, circularity, mean_intensity,
                std_intensity, aspect_ratio
            )

            if confidence >= self.confidence_threshold:
                # Konversi koordinat kembali ke ukuran asli
                if scale != 1:
                    x = int(x / scale)
                    y = int(y / scale)
                    w = int(w / scale)
                    h = int(h / scale)

                detections.append({
                    'bbox': [x, y, x + w, y + h],
                    'confidence': round(confidence, 3),
                    'class': 'pothole',
                    'width': w,
                    'height': h,
                    'area': int(area / (scale * scale)),
                    'circularity': round(circularity, 3)
                })

        # Sort by confidence
        detections.sort(key=lambda d: d['confidence'], reverse=True)

        # Non-Maximum Suppression sederhana
        detections = self._nms(detections, iou_threshold=0.4)

        # ====== VISUALISASI ======
        result_img = original.copy()
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']

            # Warna berdasarkan confidence
            if conf > 0.7:
                color = (0, 0, 255)  # Merah - high confidence
            elif conf > 0.5:
                color = (0, 165, 255)  # Orange - medium
            else:
                color = (0, 255, 255)  # Kuning - low

            # Gambar bounding box dengan efek
            cv2.rectangle(result_img, (x1, y1), (x2, y2), color, 3)

            # Overlay transparan
            overlay = result_img.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, 0.15, result_img, 0.85, 0, result_img)

            # Label
            label = f"Lubang {conf:.0%}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(result_img, (x1, y1 - label_size[1] - 10),
                          (x1 + label_size[0] + 5, y1), color, -1)
            cv2.putText(result_img, label, (x1 + 2, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Tambahkan info overlay
        num_potholes = len(detections)
        self._add_info_overlay(result_img, num_potholes, detections)

        # Simpan hasil
        result_filename = f"result_{os.path.basename(image_path)}"
        result_path = os.path.join(result_folder, result_filename)
        cv2.imwrite(result_path, result_img)

        avg_conf = np.mean([d['confidence'] for d in detections]) if detections else 0

        return {
            'detected': num_potholes > 0,
            'num_potholes': num_potholes,
            'detections': detections,
            'result_image': result_filename,
            'avg_confidence': round(float(avg_conf), 3),
            'method': 'OpenCV'
        }

    def _calculate_confidence(self, area, total_area, circularity, mean_intensity,
                              std_intensity, aspect_ratio):
        """
        Hitung confidence score berdasarkan berbagai fitur.
        
        Fitur yang dianalisis:
        - Ukuran area relatif terhadap gambar
        - Kebulatan kontur (circularity)
        - Intensitas rata-rata (lubang cenderung gelap)
        - Variasi tekstur
        - Rasio aspek
        """
        score = 0.0

        # Skor ukuran area (0-0.2)
        area_ratio = area / total_area
        if 0.01 < area_ratio < 0.15:
            score += 0.2
        elif 0.005 < area_ratio < 0.25:
            score += 0.1

        # Skor kegelapan (0-0.3) - lubang biasanya gelap
        if mean_intensity < 60:
            score += 0.3
        elif mean_intensity < 90:
            score += 0.2
        elif mean_intensity < 120:
            score += 0.1

        # Skor kebulatan (0-0.2) - lubang biasanya agak bulat
        if 0.2 < circularity < 0.9:
            score += 0.2
        elif circularity >= 0.1:
            score += 0.1

        # Skor variasi tekstur (0-0.15)
        if std_intensity > 20:
            score += 0.15
        elif std_intensity > 10:
            score += 0.08

        # Skor rasio aspek (0-0.15) - tidak terlalu panjang
        if 0.4 < aspect_ratio < 2.5:
            score += 0.15
        elif 0.25 < aspect_ratio < 4:
            score += 0.08

        return min(score, 1.0)

    def _nms(self, detections, iou_threshold=0.4):
        """Non-Maximum Suppression sederhana"""
        if len(detections) <= 1:
            return detections

        keep = []
        used = set()

        for i, det_i in enumerate(detections):
            if i in used:
                continue
            keep.append(det_i)

            for j, det_j in enumerate(detections[i + 1:], i + 1):
                if j in used:
                    continue
                iou = self._compute_iou(det_i['bbox'], det_j['bbox'])
                if iou > iou_threshold:
                    used.add(j)

        return keep

    def _compute_iou(self, box1, box2):
        """Hitung Intersection over Union (IoU)"""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0

    def _add_info_overlay(self, img, num_potholes, detections):
        """Tambahkan overlay informasi pada gambar hasil"""
        height, width = img.shape[:2]

        # Background untuk info
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (width, 70), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, img, 0.4, 0, img)

        # Status text
        if num_potholes > 0:
            status = f"TERDETEKSI: {num_potholes} LUBANG JALAN"
            color = (0, 0, 255)
        else:
            status = "AMAN - TIDAK ADA LUBANG JALAN"
            color = (0, 255, 0)

        cv2.putText(img, status, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cv2.putText(img, f"Scan: {timestamp}", (10, 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Confidence info
        if detections:
            avg_conf = np.mean([d['confidence'] for d in detections])
            cv2.putText(img, f"Conf: {avg_conf:.0%}", (width - 150, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
