import torch

# Cek apakah PyTorch bisa melihat GPU
gpu_siap = torch.cuda.is_available()
print(f"GPU Terdeteksi: {gpu_siap}")

# Cek nama GPU
if gpu_siap:
    print(f"Nama GPU: {torch.cuda.get_device_name(0)}")
    print(f"Versi CUDA di PyTorch: {torch.version.cuda}")
else:
    print("PyTorch hanya menggunakan CPU. Coba install ulang versi CUDA.")
