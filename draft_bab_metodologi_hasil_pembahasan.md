# Draft Bab Metodologi Penelitian dan Bab Hasil dan Pembahasan

## Judul Penelitian

**Pengembangan Sistem Deteksi Jalan Berlubang Berbasis YOLO untuk Meningkatkan Keselamatan Berkendara**

## Catatan Penggunaan Dokumen

Dokumen ini merupakan draf bab metodologi penelitian serta bab hasil dan pembahasan yang disesuaikan dengan implementasi proyek pada repositori ini. Angka, nama file gambar, dan beberapa bagian narasi dapat disesuaikan kembali jika Anda ingin mengikuti format jurnal kampus atau gaya penulisan tertentu.

---

# BAB III. METODOLOGI PENELITIAN

## 3.1 Jenis Penelitian

Penelitian ini menggunakan pendekatan eksperimen dan pengembangan sistem. Tujuan utama penelitian adalah membangun sistem deteksi jalan berlubang berbasis YOLO yang dapat digunakan untuk mendukung keselamatan berkendara melalui identifikasi objek pothole pada citra jalan.

## 3.2 Alur Penelitian

Tahapan penelitian dimulai dari pengumpulan dataset, penyiapan data, pelatihan model YOLOv8, integrasi model ke dalam aplikasi web, pengujian sistem, dan analisis hasil deteksi. Sistem juga disiapkan dengan mekanisme fallback berbasis OpenCV apabila model YOLO tidak tersedia.

### Gambar yang dibutuhkan

- **Gambar 3.1. Alur metodologi penelitian**
  - **Letak**: diletakkan di akhir subbab 3.2, setelah paragraf yang menjelaskan tahapan penelitian.
  - **Keterangan**: diagram alur dari dataset -> training -> validasi -> integrasi aplikasi -> pengujian.
  - **Saran nama file**: `gambar_3_1_alur_metodologi.png`

## 3.3 Dataset Penelitian

Dataset yang digunakan berasal dari Roboflow dan telah disusun ke dalam tiga bagian, yaitu data latih, data validasi, dan data uji. Berdasarkan struktur dataset pada proyek, jumlah data terdiri atas 1.031 gambar latih, 296 gambar validasi, dan 150 gambar uji. Dataset hanya memiliki satu kelas objek, yaitu **pothole**.

### Tabel yang dibutuhkan

- **Tabel 3.1. Distribusi dataset penelitian**
  - **Letak**: setelah paragraf penjelasan dataset pada subbab 3.3.
  - **Keterangan**: berisi jumlah gambar dan label pada setiap split data.
  - **Isi yang disarankan**:

| Split Data | Jumlah Gambar | Jumlah Label | Keterangan                               |
| ---------- | ------------: | -----------: | ---------------------------------------- |
| Train      |          1031 |         1031 | Digunakan untuk melatih model            |
| Valid      |           296 |          296 | Digunakan untuk validasi selama training |
| Test       |           150 |          150 | Digunakan untuk evaluasi akhir           |

### Gambar yang dibutuhkan

- **Gambar 3.2. Contoh citra dataset pothole**
  - **Letak**: setelah penjelasan dataset.
  - **Keterangan**: menampilkan contoh gambar jalan berlubang dari dataset.
  - **Saran nama file**: `gambar_3_2_contoh_dataset.png`

- **Gambar 3.3. Struktur folder dataset**
  - **Letak**: setelah tabel distribusi dataset.
  - **Keterangan**: menunjukkan susunan folder train, valid, dan test beserta folder images dan labels.
  - **Saran nama file**: `gambar_3_3_struktur_dataset.png`

## 3.4 Pra-pemrosesan Data

Data pada penelitian ini dipersiapkan dalam format yang sesuai dengan YOLO, yaitu citra gambar beserta anotasi bounding box pada file label `.txt`. Pada tahap training, file konfigurasi `data_train.yaml` digunakan untuk mendefinisikan lokasi dataset, jumlah kelas, serta nama kelas pothole.

Langkah pra-pemrosesan yang digunakan pada sistem meliputi:

1. Penyesuaian struktur path dataset agar dapat dibaca oleh YOLO.
2. Penetapan jumlah kelas sebanyak satu, yaitu pothole.
3. Penggunaan ukuran input gambar 640 x 640 selama proses training.
4. Penetapan confidence threshold sebesar 0,35 pada tahap inferensi.

### Tabel yang dibutuhkan

- **Tabel 3.2. Parameter pra-pemrosesan**
  - **Letak**: setelah paragraf pra-pemrosesan data.
  - **Keterangan**: merangkum parameter utama yang digunakan.

| Parameter            | Nilai       | Keterangan                      |
| -------------------- | ----------- | ------------------------------- |
| Ukuran input         | 640 x 640   | Ukuran citra saat training YOLO |
| Jumlah kelas         | 1           | Kelas pothole                   |
| Confidence threshold | 0,35        | Ambang deteksi pada inferensi   |
| Format label         | `.txt` YOLO | Format anotasi bounding box     |

## 3.5 Arsitektur Sistem

Sistem dikembangkan menggunakan model YOLOv8s sebagai model utama deteksi objek. Proses inferensi dilakukan melalui aplikasi web berbasis Flask dan Flask-SocketIO agar hasil deteksi dapat ditampilkan secara real-time. Jika model YOLO tidak tersedia, sistem menggunakan metode OpenCV sebagai cadangan untuk tetap memberikan hasil deteksi.

### Gambar yang dibutuhkan

- **Gambar 3.4. Arsitektur sistem deteksi jalan berlubang**
  - **Letak**: setelah penjelasan arsitektur sistem.
  - **Keterangan**: menggambarkan alur kamera/upload gambar -> server Flask -> YOLO/OpenCV -> hasil deteksi -> notifikasi.
  - **Saran nama file**: `gambar_3_4_arsitektur_sistem.png`

- **Gambar 3.5. Diagram alur proses deteksi**
  - **Letak**: setelah pembahasan arsitektur sistem.
  - **Keterangan**: memperjelas alur data dari input hingga output.
  - **Saran nama file**: `gambar_3_5_flow_deteksi.png`

## 3.6 Konfigurasi Pelatihan Model

Pelatihan model dilakukan menggunakan YOLOv8s pretrained dengan konfigurasi utama sebagai berikut: 100 epoch, batch size 16, image size 640, patience 20, serta seed 42 agar hasil dapat direplikasi. Model terbaik disalin ke folder `model/` dengan nama `pothole_best.pt`.

### Tabel yang dibutuhkan

- **Tabel 3.3. Konfigurasi pelatihan YOLOv8**
  - **Letak**: setelah penjelasan konfigurasi training.
  - **Keterangan**: menampilkan parameter training utama.

| Parameter      | Nilai                    |
| -------------- | ------------------------ |
| Model dasar    | yolov8s.pt               |
| Epoch          | 100                      |
| Image size     | 640                      |
| Batch size     | 16                       |
| Patience       | 20                       |
| Device         | GPU 0 / auto             |
| Seed           | 42                       |
| Optimizer      | auto                     |
| Project output | `runs/pothole_detection` |

## 3.7 Implementasi Sistem

Implementasi sistem dilakukan dengan Python, Flask, Flask-SocketIO, OpenCV, NumPy, dan Ultralytics YOLO. Aplikasi memiliki endpoint utama untuk unggah gambar dan deteksi objek, riwayat deteksi, serta statistik deteksi. Selain itu, sistem juga mendukung pengiriman alert melalui WebSocket ketika pothole terdeteksi.

### Gambar yang dibutuhkan

- **Gambar 3.6. Tampilan antarmuka aplikasi web**
  - **Letak**: setelah penjelasan implementasi sistem.
  - **Keterangan**: screenshot halaman utama aplikasi.
  - **Saran nama file**: `gambar_3_6_ui_aplikasi.png`

- **Gambar 3.7. Contoh hasil deteksi pada aplikasi**
  - **Letak**: setelah penjelasan implementasi sistem.
  - **Keterangan**: menampilkan gambar hasil deteksi dengan bounding box dan label pothole.
  - **Saran nama file**: `gambar_3_7_hasil_deteksi_aplikasi.png`

## 3.8 Teknik Evaluasi

Evaluasi model dilakukan menggunakan metrik precision, recall, mAP50, dan mAP50-95. Precision digunakan untuk mengukur ketepatan prediksi positif, recall untuk mengukur kemampuan model menemukan seluruh objek pothole, mAP50 untuk menilai performa deteksi pada IoU 0,50, dan mAP50-95 untuk menilai performa pada berbagai ambang IoU.

### Tabel yang dibutuhkan

- **Tabel 3.4. Metrik evaluasi model**
  - **Letak**: akhir subbab metodologi atau awal bab hasil.
  - **Keterangan**: menjelaskan fungsi tiap metrik evaluasi.

| Metrik    | Fungsi                                         |
| --------- | ---------------------------------------------- |
| Precision | Mengukur ketepatan prediksi positif            |
| Recall    | Mengukur kemampuan menemukan objek pothole     |
| mAP50     | Mengukur performa deteksi pada IoU 0,50        |
| mAP50-95  | Mengukur performa rata-rata pada IoU 0,50-0,95 |

---

# BAB IV. HASIL DAN PEMBAHASAN

## 4.1 Hasil Pelatihan Model

Hasil pelatihan menunjukkan bahwa model YOLOv8s mampu mempelajari pola visual pothole pada citra jalan. Berdasarkan file hasil training pada `runs/pothole_detection/results.csv`, performa model pada epoch terakhir mencapai precision 0,8925, recall 0,6451, mAP50 0,7586, dan mAP50-95 0,4371. Nilai tersebut menunjukkan bahwa model sudah cukup baik dalam mendeteksi jalan berlubang, terutama dalam menghasilkan prediksi yang tepat.

### Tabel yang dibutuhkan

- **Tabel 4.1. Hasil metrik akhir training**
  - **Letak**: setelah paragraf hasil pelatihan model.
  - **Keterangan**: merangkum metrik performa pada epoch terakhir atau epoch terbaik.

| Metrik    |  Nilai |
| --------- | -----: |
| Precision | 0,8925 |
| Recall    | 0,6451 |
| mAP50     | 0,7586 |
| mAP50-95  | 0,4371 |

## 4.2 Pembahasan Hasil Training

Nilai precision yang tinggi menunjukkan bahwa prediksi pothole yang dihasilkan model cenderung benar. Hal ini penting karena sistem deteksi jalan berlubang tidak boleh terlalu sering menghasilkan false positive, sebab informasi yang salah dapat mengurangi kepercayaan pengguna. Namun, recall yang lebih rendah dibanding precision menunjukkan bahwa sebagian pothole masih belum berhasil terdeteksi. Kondisi ini dapat disebabkan oleh variasi pencahayaan, sudut kamera, ukuran pothole yang kecil, atau kemiripan tekstur permukaan jalan dengan objek lubang.

Peningkatan nilai mAP50 selama training memperlihatkan bahwa model semakin mampu mengenali ciri visual pothole. Hal ini sejalan dengan penggunaan YOLOv8s yang memang dirancang untuk deteksi objek secara cepat dan akurat. Dengan jumlah data latih yang cukup dan anotasi bounding box yang konsisten, model dapat mempelajari pola objek secara lebih baik.

### Gambar yang dibutuhkan

- **Gambar 4.1. Grafik hasil training loss**
  - **Letak**: setelah paragraf pembahasan hasil training.
  - **Keterangan**: menampilkan kurva train box loss, cls loss, dfl loss, dan validation loss.
  - **Saran nama file**: `gambar_4_1_grafik_loss.png`

- **Gambar 4.2. Grafik precision, recall, mAP50, dan mAP50-95**
  - **Letak**: setelah grafik loss.
  - **Keterangan**: memperlihatkan perkembangan metrik performa model selama training.
  - **Saran nama file**: `gambar_4_2_grafik_metrik.png`

## 4.3 Hasil Evaluasi Model

Evaluasi model dilakukan menggunakan data uji untuk melihat kemampuan model pada data yang belum pernah dilihat saat training. Hasil evaluasi divisualisasikan melalui confusion matrix, precision-recall curve, dan contoh prediksi pada data validasi maupun data uji. Visualisasi ini penting untuk melihat kesalahan klasifikasi dan konsistensi model saat mendeteksi pothole.

### Gambar yang dibutuhkan

- **Gambar 4.3. Confusion matrix**
  - **Letak**: setelah paragraf evaluasi model.
  - **Keterangan**: memperlihatkan perbandingan antara prediksi model dan label sebenarnya.
  - **Saran nama file**: `gambar_4_3_confusion_matrix.png`

- **Gambar 4.4. Confusion matrix normalized**
  - **Letak**: setelah confusion matrix utama.
  - **Keterangan**: memperlihatkan proporsi klasifikasi secara terstandarisasi.
  - **Saran nama file**: `gambar_4_4_confusion_matrix_normalized.png`

- **Gambar 4.5. Precision-Recall curve**
  - **Letak**: setelah confusion matrix normalized.
  - **Keterangan**: menunjukkan hubungan precision dan recall pada berbagai threshold.
  - **Saran nama file**: `gambar_4_5_pr_curve.png`

## 4.4 Hasil Implementasi Sistem Web

Hasil implementasi memperlihatkan bahwa model dapat diintegrasikan ke dalam aplikasi web berbasis Flask. Pengguna dapat mengunggah citra jalan, lalu sistem akan menampilkan hasil deteksi dalam bentuk bounding box, jumlah pothole yang ditemukan, confidence score, dan gambar hasil anotasi. Selain itu, sistem juga mendukung notifikasi real-time melalui SocketIO ketika pothole terdeteksi.

### Gambar yang dibutuhkan

- **Gambar 4.6. Tampilan halaman utama aplikasi**
  - **Letak**: setelah pembahasan implementasi web.
  - **Keterangan**: screenshot halaman utama web sebelum proses deteksi.
  - **Saran nama file**: `gambar_4_6_tampilan_awal_aplikasi.png`

- **Gambar 4.7. Hasil deteksi pada antarmuka web**
  - **Letak**: setelah screenshot halaman utama.
  - **Keterangan**: screenshot hasil deteksi yang menampilkan bounding box dan label pothole.
  - **Saran nama file**: `gambar_4_7_hasil_deteksi_web.png`

- **Gambar 4.8. Notifikasi real-time pothole alert**
  - **Letak**: setelah penjelasan notifikasi real-time.
  - **Keterangan**: bukti notifikasi jika pothole terdeteksi.
  - **Saran nama file**: `gambar_4_8_pothole_alert.png`

### Tabel yang dibutuhkan

- **Tabel 4.2. Ringkasan hasil implementasi sistem**
  - **Letak**: setelah pembahasan hasil implementasi web.
  - **Keterangan**: merangkum komponen sistem dan hasil yang ditampilkan.

| Komponen             | Hasil                |
| -------------------- | -------------------- |
| Upload gambar        | Berhasil             |
| Deteksi objek        | Berhasil             |
| Bounding box         | Berhasil ditampilkan |
| Confidence score     | Ditampilkan          |
| Riwayat deteksi      | Tersedia             |
| Notifikasi real-time | Tersedia             |

## 4.5 Pembahasan Kelebihan dan Keterbatasan Sistem

Kelebihan utama sistem ini adalah kemampuannya mendeteksi pothole secara otomatis dan menampilkan hasil secara real-time melalui web. Penggunaan YOLOv8s membuat sistem cukup cepat dan relatif akurat. Integrasi dengan Flask dan SocketIO juga menjadikan sistem lebih mudah digunakan pada perangkat desktop maupun smartphone.

Namun, sistem masih memiliki keterbatasan. Recall yang belum maksimal menunjukkan bahwa masih ada pothole yang tidak terdeteksi, terutama pada kondisi jalan yang sulit, pencahayaan buruk, atau objek yang berukuran kecil. Selain itu, performa sistem sangat bergantung pada kualitas dataset dan keragaman kondisi citra yang digunakan saat training.

### Gambar yang dibutuhkan

- **Gambar 4.9. Contoh kasus deteksi berhasil**
  - **Letak**: setelah pembahasan kelebihan sistem.
  - **Keterangan**: menampilkan citra dengan pothole yang terdeteksi dengan baik.
  - **Saran nama file**: `gambar_4_9_deteksi_berhasil.png`

- **Gambar 4.10. Contoh kasus deteksi yang kurang optimal**
  - **Letak**: setelah pembahasan keterbatasan sistem.
  - **Keterangan**: menampilkan citra dengan pothole kecil atau kondisi sulit yang belum terdeteksi sempurna.
  - **Saran nama file**: `gambar_4_10_deteksi_kurang_optimal.png`

## 4.6 Pembahasan Akhir

Secara keseluruhan, sistem deteksi jalan berlubang berbasis YOLO yang dikembangkan pada penelitian ini telah menunjukkan hasil yang layak untuk digunakan sebagai dasar sistem pemantauan jalan. Model mampu mengenali pothole dengan precision yang tinggi, sedangkan sistem web menyediakan antarmuka yang mudah digunakan untuk melihat hasil deteksi. Dengan pengembangan lanjutan pada dataset, augmentasi, dan validasi lapangan, performa sistem masih berpotensi ditingkatkan.

---

# Daftar Final Gambar dan Tabel

## Gambar Wajib

Gambar-gambar ini sebaiknya ada karena langsung mendukung metodologi dan hasil penelitian.

1. **Gambar 3.1. Alur metodologi penelitian**

- **Sumber**: dibuat manual dari alur proyek.
- **Isi**: dataset -> training -> validasi -> integrasi aplikasi -> pengujian.
- **Nama file disarankan**: `gambar_3_1_alur_metodologi.png`

2. **Gambar 3.2. Contoh citra dataset pothole**

- **Sumber**: folder dataset di [pothole.v1i.yolov8/train/images](pothole.v1i.yolov8/train/images), [pothole.v1i.yolov8/valid/images](pothole.v1i.yolov8/valid/images), atau [pothole.v1i.yolov8/test/images](pothole.v1i.yolov8/test/images).
- **Isi**: contoh citra jalan berlubang dari dataset.
- **Nama file disarankan**: `gambar_3_2_contoh_dataset.png`

3. **Gambar 3.3. Struktur folder dataset**

- **Sumber**: screenshot folder [pothole.v1i.yolov8](pothole.v1i.yolov8).
- **Isi**: struktur train, valid, test, images, dan labels.
- **Nama file disarankan**: `gambar_3_3_struktur_dataset.png`

4. **Gambar 3.4. Arsitektur sistem deteksi jalan berlubang**

- **Sumber**: dibuat manual berdasarkan [app.py](app.py) dan [detector/pothole_detector.py](detector/pothole_detector.py).
- **Isi**: alur kamera/upload -> server Flask -> YOLO/OpenCV -> hasil deteksi -> notifikasi.
- **Nama file disarankan**: `gambar_3_4_arsitektur_sistem.png`

5. **Gambar 3.5. Diagram alur proses deteksi**

- **Sumber**: dibuat manual.
- **Isi**: proses input gambar, inferensi, anotasi bounding box, dan output hasil.
- **Nama file disarankan**: `gambar_3_5_flow_deteksi.png`

6. **Gambar 4.1. Grafik hasil training loss**

- **Sumber**: [runs/pothole_detection/results.png](runs/pothole_detection/results.png).
- **Isi**: kurva loss dan metrik training.
- **Nama file disarankan**: `gambar_4_1_results_training.png`

7. **Gambar 4.3. Confusion matrix**

- **Sumber**: [runs/pothole_detection/confusion_matrix.png](runs/pothole_detection/confusion_matrix.png).
- **Isi**: perbandingan prediksi model dan label sebenarnya.
- **Nama file disarankan**: `gambar_4_3_confusion_matrix.png`

8. **Gambar 4.4. Confusion matrix normalized**

- **Sumber**: [runs/pothole_detection/confusion_matrix_normalized.png](runs/pothole_detection/confusion_matrix_normalized.png).
- **Isi**: confusion matrix dalam bentuk normalisasi.
- **Nama file disarankan**: `gambar_4_4_confusion_matrix_normalized.png`

9. **Gambar 4.5. Precision-Recall curve**

- **Sumber**: [runs/pothole_detection/PR_curve.png](runs/pothole_detection/PR_curve.png).
- **Isi**: hubungan precision dan recall pada berbagai threshold.
- **Nama file disarankan**: `gambar_4_5_pr_curve.png`

10. **Gambar 4.6. Tampilan halaman utama aplikasi**

- **Sumber**: screenshot dari browser saat aplikasi dijalankan.
- **Isi**: tampilan awal web sebelum deteksi.
- **Nama file disarankan**: `gambar_4_6_tampilan_awal_aplikasi.png`

11. **Gambar 4.7. Hasil deteksi pada antarmuka web**

- **Sumber**: screenshot hasil upload gambar di aplikasi.
- **Isi**: bounding box, label, confidence, dan gambar hasil anotasi.
- **Nama file disarankan**: `gambar_4_7_hasil_deteksi_web.png`

## Gambar Opsional

Gambar-gambar ini bagus untuk memperkuat pembahasan, tetapi tidak wajib jika ruang jurnal terbatas.

1. **Gambar 3.6. Tampilan antarmuka aplikasi web**

- **Sumber**: [templates/index.html](templates/index.html) sebagai acuan tampilan.
- **Isi**: screenshot UI, terutama bagian kamera, upload, dan hasil.
- **Nama file disarankan**: `gambar_3_6_ui_aplikasi.png`

2. **Gambar 3.7. Contoh hasil deteksi pada aplikasi**

- **Sumber**: hasil deteksi tersimpan di folder [results](results).
- **Isi**: contoh keluaran sistem.
- **Nama file disarankan**: `gambar_3_7_hasil_deteksi_aplikasi.png`

3. **Gambar 4.2. Grafik precision, recall, mAP50, dan mAP50-95**

- **Sumber**: [runs/pothole_detection/results.png](runs/pothole_detection/results.png) atau grafik yang dibuat dari [runs/pothole_detection/results.csv](runs/pothole_detection/results.csv).
- **Isi**: ringkasan perkembangan metrik performa.
- **Nama file disarankan**: `gambar_4_2_grafik_metrik.png`

4. **Gambar 4.8. Notifikasi real-time pothole alert**

- **Sumber**: screenshot alert saat deteksi aktif.
- **Isi**: notifikasi WebSocket ketika pothole terdeteksi.
- **Nama file disarankan**: `gambar_4_8_pothole_alert.png`

5. **Gambar 4.9. Contoh kasus deteksi berhasil**

- **Sumber**: salah satu file hasil di [results](results).
- **Isi**: contoh deteksi yang paling jelas dan rapi.
- **Nama file disarankan**: `gambar_4_9_deteksi_berhasil.png`

6. **Gambar 4.10. Contoh kasus deteksi yang kurang optimal**

- **Sumber**: salah satu hasil deteksi yang kurang maksimal atau contoh dari dataset uji.
- **Isi**: kasus saat model gagal atau kurang akurat.
- **Nama file disarankan**: `gambar_4_10_deteksi_kurang_optimal.png`

## Tabel Wajib

1. **Tabel 3.1. Distribusi dataset penelitian**
2. **Tabel 3.2. Parameter pra-pemrosesan**
3. **Tabel 3.3. Konfigurasi pelatihan YOLOv8**
4. **Tabel 3.4. Metrik evaluasi model**
5. **Tabel 4.1. Hasil metrik akhir training**
6. **Tabel 4.2. Ringkasan hasil implementasi sistem**

## Tabel Opsional

1. Tabel tambahan perbandingan jika Anda ingin membandingkan hasil dengan model lain.
2. Tabel ringkasan error atau contoh kasus jika dosen meminta analisis lebih rinci.

---

# Catatan Revisi Cepat

- Jika Anda ingin jurnal lebih formal, ubah istilah seperti "pothole" menjadi "jalan berlubang" pada bagian narasi, tetapi pertahankan istilah teknis saat menyebut kelas model.
- Jika dosen atau kampus meminta gaya ilmiah yang lebih kaku, kalimat pada bagian pembahasan dapat dipadatkan lagi.
- Jika Anda punya screenshot asli dari aplikasi, letakkan sesuai nomor gambar di atas agar bab hasil lebih kuat.
