"""
Training Script untuk Model Deteksi Jalan Berlubang (Pothole)
Menggunakan YOLOv8 dengan dataset dari Roboflow
"""

import os
import shutil
import yaml
from ultralytics import YOLO


def setup_data_yaml():
    """Buat data.yaml dengan path absolut dan nama kelas yang benar."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "pothole.v1i.yolov8")

    data_config = {
        "path": dataset_dir,
        "train": "train/images",
        "val": "valid/images",
        "test": "test/images",
        "nc": 1,
        "names": {0: "pothole"},
    }

    # Simpan data.yaml yang sudah diperbaiki
    config_path = os.path.join(dataset_dir, "data_train.yaml")
    with open(config_path, "w") as f:
        yaml.dump(data_config, f, default_flow_style=False)

    print(f"[INFO] data_train.yaml disimpan di: {config_path}")
    return config_path


def count_dataset(dataset_dir):
    """Hitung jumlah data di setiap split."""
    splits = ["train", "valid", "test"]
    for split in splits:
        img_dir = os.path.join(dataset_dir, split, "images")
        lbl_dir = os.path.join(dataset_dir, split, "labels")
        n_img = len([f for f in os.listdir(img_dir) if f.endswith(('.jpg', '.jpeg', '.png'))])
        n_lbl = len([f for f in os.listdir(lbl_dir) if f.endswith('.txt')])
        print(f"  {split:>6}: {n_img} gambar, {n_lbl} label")


def train():
    """Jalankan training YOLOv8."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "pothole.v1i.yolov8")
    model_dir = os.path.join(base_dir, "model")

    # Pastikan folder model ada
    os.makedirs(model_dir, exist_ok=True)

    print("=" * 60)
    print("  TRAINING MODEL DETEKSI JALAN BERLUBANG (POTHOLE)")
    print("=" * 60)

    # Tampilkan info dataset
    print("\n[INFO] Dataset Info:")
    count_dataset(dataset_dir)

    # Setup data.yaml
    data_yaml_path = setup_data_yaml()

    # ============================================================
    # KONFIGURASI TRAINING - Sesuaikan sesuai kebutuhan
    # ============================================================
    MODEL_SIZE = "yolov8n.pt"  # Pilihan: yolov8n.pt (nano/cepat), yolov8s.pt (small), yolov8m.pt (medium)
    EPOCHS = 100               # Jumlah epoch training
    IMG_SIZE = 640             # Ukuran gambar input
    BATCH_SIZE = 16            # Batch size (turunkan jika GPU memory tidak cukup)
    PATIENCE = 20              # Early stopping patience
    DEVICE = ""                # Kosong = auto (GPU jika ada, CPU jika tidak)
    PROJECT = os.path.join(base_dir, "runs")  # Folder output training
    NAME = "pothole_detection"  # Nama experiment

    print(f"\n[INFO] Konfigurasi Training:")
    print(f"  Model      : {MODEL_SIZE}")
    print(f"  Epochs     : {EPOCHS}")
    print(f"  Image Size : {IMG_SIZE}")
    print(f"  Batch Size : {BATCH_SIZE}")
    print(f"  Patience   : {PATIENCE}")
    print(f"  Device     : {'auto' if DEVICE == '' else DEVICE}")
    print(f"  Output     : {PROJECT}/{NAME}")

    # Load model pretrained
    print(f"\n[INFO] Loading model {MODEL_SIZE}...")
    model = YOLO(MODEL_SIZE)

    # Mulai training
    print("\n[INFO] Memulai training...\n")
    train_args = {
        "data": data_yaml_path,
        "epochs": EPOCHS,
        "imgsz": IMG_SIZE,
        "batch": BATCH_SIZE,
        "patience": PATIENCE,
        "project": PROJECT,
        "name": NAME,
        "exist_ok": True,
        "pretrained": True,
        "optimizer": "auto",
        "verbose": True,
        "seed": 42,
        "deterministic": True,
        "plots": True,
        "save": True,
        "save_period": -1,  # Simpan setiap epoch terakhir saja
        "val": True,
    }

    # Tambahkan device jika ditentukan
    if DEVICE:
        train_args["device"] = DEVICE

    results = model.train(**train_args)

    # ============================================================
    # POST-TRAINING
    # ============================================================

    # Copy model terbaik ke folder model/
    best_model_src = os.path.join(PROJECT, NAME, "weights", "best.pt")
    best_model_dst = os.path.join(model_dir, "pothole_best.pt")

    if os.path.exists(best_model_src):
        shutil.copy2(best_model_src, best_model_dst)
        print(f"\n[SUCCESS] Model terbaik disalin ke: {best_model_dst}")
    else:
        print(f"\n[WARNING] Model terbaik tidak ditemukan di: {best_model_src}")
        # Coba cari di tempat lain
        last_model_src = os.path.join(PROJECT, NAME, "weights", "last.pt")
        if os.path.exists(last_model_src):
            shutil.copy2(last_model_src, best_model_dst)
            print(f"[INFO] Model terakhir disalin ke: {best_model_dst}")

    # Validasi model
    print("\n[INFO] Menjalankan validasi pada test set...")
    best_model = YOLO(best_model_dst)
    metrics = best_model.val(
        data=data_yaml_path,
        split="test",
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        project=PROJECT,
        name="pothole_test",
        exist_ok=True,
    )

    print("\n" + "=" * 60)
    print("  HASIL TRAINING")
    print("=" * 60)
    print(f"  mAP50     : {metrics.box.map50:.4f}")
    print(f"  mAP50-95  : {metrics.box.map:.4f}")
    print(f"  Precision : {metrics.box.mp:.4f}")
    print(f"  Recall    : {metrics.box.mr:.4f}")
    print("=" * 60)
    print(f"\n  Model tersimpan di: {best_model_dst}")
    print(f"  Hasil training di : {os.path.join(PROJECT, NAME)}")
    print(f"\n  Jalankan aplikasi dengan: python app.py")
    print("=" * 60)


if __name__ == "__main__":
    train()
