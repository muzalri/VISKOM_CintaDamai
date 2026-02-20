/**
 * POTHOLE DETECTOR - VISKOM Cinta Damai
 * Frontend JavaScript Application
 *
 * Fitur:
 * - Akses kamera HP (rear camera)
 * - Upload gambar
 * - Kirim gambar ke server untuk deteksi
 * - Real-time notification via WebSocket
 */

// ============================================================
// Global Variables
// ============================================================
let cameraStream = null;
let capturedBlob = null;
let isCameraActive = false;

// ============================================================
// WebSocket Connection
// ============================================================
const socket = io();

socket.on("connect", () => {
  console.log("[WS] Terhubung ke server");
  updateConnectionStatus("connected", "Terhubung");
});

socket.on("disconnect", () => {
  console.log("[WS] Terputus dari server");
  updateConnectionStatus("disconnected", "Terputus");
});

socket.on("connected", (data) => {
  console.log("[WS] Server:", data.message);
});

// Real-time pothole alert dari server
socket.on("pothole_alert", (data) => {
  console.log("[WS] ALERT:", data);
  showAlert(data.message);
  playAlertSound();
  showDesktopNotification(data);
});

socket.on("server_status", (data) => {
  console.log("[WS] Server status:", data);
});

// ============================================================
// Connection Status
// ============================================================
function updateConnectionStatus(status, text) {
  const el = document.getElementById("connectionStatus");
  const dot = el.querySelector(".status-dot");
  const textEl = el.querySelector(".status-text");

  dot.className = "status-dot " + status;
  textEl.textContent = text;
}

// ============================================================
// Alert Functions
// ============================================================
function showAlert(message) {
  const banner = document.getElementById("alertBanner");
  const msgEl = document.getElementById("alertMessage");
  msgEl.textContent = message;
  banner.classList.add("active");

  // Auto hide after 10 seconds
  setTimeout(() => closeAlert(), 10000);
}

function closeAlert() {
  document.getElementById("alertBanner").classList.remove("active");
}

function playAlertSound() {
  try {
    const audio = document.getElementById("alertSound");
    if (audio) {
      audio.currentTime = 0;
      audio.play().catch(() => {});
    }
  } catch (e) {
    console.log("Audio not supported");
  }
}

function showDesktopNotification(data) {
  if ("Notification" in window && Notification.permission === "granted") {
    new Notification("⚠️ Jalan Berlubang Terdeteksi!", {
      body: `Ditemukan ${data.num_potholes} lubang jalan (Confidence: ${(data.confidence * 100).toFixed(0)}%)`,
      icon: "/static/img/pothole-icon.png",
      vibrate: [200, 100, 200],
    });
  }
}

// Request notification permission
if ("Notification" in window && Notification.permission === "default") {
  Notification.requestPermission();
}

// ============================================================
// Camera Functions
// ============================================================
async function toggleCamera() {
  if (isCameraActive) {
    stopCamera();
  } else {
    await startCamera();
  }
}

async function startCamera() {
  const video = document.getElementById("cameraPreview");
  const overlay = document.getElementById("cameraOverlay");
  const btnCamera = document.getElementById("btnCamera");
  const btnCapture = document.getElementById("btnCapture");
  const cameraContainer = document.getElementById("cameraContainer");
  const imagePreview = document.getElementById("imagePreview");

  try {
    // Sembunyikan image preview jika ada
    imagePreview.style.display = "none";
    cameraContainer.style.display = "block";

    // Request camera - preferensi kamera belakang (environment)
    const constraints = {
      video: {
        facingMode: { ideal: "environment" },
        width: { ideal: 1280 },
        height: { ideal: 720 },
      },
    };

    cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = cameraStream;
    await video.play();

    overlay.classList.add("hidden");
    btnCamera.innerHTML =
      '<i class="fas fa-stop"></i><span>Tutup Kamera</span>';
    btnCamera.classList.add("active");
    btnCapture.style.display = "inline-flex";
    isCameraActive = true;
  } catch (err) {
    console.error("Gagal akses kamera:", err);
    alert(
      "Tidak dapat mengakses kamera.\nPastikan:\n1. Browser memiliki izin kamera\n2. Menggunakan HTTPS atau localhost\n3. Kamera tidak digunakan aplikasi lain",
    );
  }
}

function stopCamera() {
  const video = document.getElementById("cameraPreview");
  const overlay = document.getElementById("cameraOverlay");
  const btnCamera = document.getElementById("btnCamera");
  const btnCapture = document.getElementById("btnCapture");

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

  video.srcObject = null;
  overlay.classList.remove("hidden");
  btnCamera.innerHTML = '<i class="fas fa-camera"></i><span>Buka Kamera</span>';
  btnCamera.classList.remove("active");
  btnCapture.style.display = "none";
  isCameraActive = false;
}

function capturePhoto() {
  const video = document.getElementById("cameraPreview");
  const canvas = document.getElementById("cameraCanvas");

  // Set ukuran canvas sesuai video
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  // Gambar frame ke canvas
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);

  // Convert canvas ke blob
  canvas.toBlob(
    (blob) => {
      capturedBlob = blob;

      // Tampilkan preview
      const previewUrl = URL.createObjectURL(blob);
      showImagePreview(previewUrl);

      // Matikan kamera
      stopCamera();

      // Enable tombol detect
      document.getElementById("btnDetect").disabled = false;
    },
    "image/jpeg",
    0.9,
  );
}

// ============================================================
// File Upload Functions
// ============================================================
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  // Validasi tipe file
  const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/bmp"];
  if (!allowedTypes.includes(file.type)) {
    alert("Format file tidak didukung!\nGunakan: JPG, PNG, WEBP, atau BMP");
    return;
  }

  // Validasi ukuran (max 16MB)
  if (file.size > 16 * 1024 * 1024) {
    alert("Ukuran file terlalu besar! Maksimal 16MB.");
    return;
  }

  capturedBlob = file;

  // Preview gambar
  const reader = new FileReader();
  reader.onload = (e) => {
    showImagePreview(e.target.result);
  };
  reader.readAsDataURL(file);

  // Matikan kamera jika aktif
  if (isCameraActive) {
    stopCamera();
  }

  // Enable tombol detect
  document.getElementById("btnDetect").disabled = false;
}

function showImagePreview(src) {
  const cameraContainer = document.getElementById("cameraContainer");
  const imagePreview = document.getElementById("imagePreview");
  const previewImage = document.getElementById("previewImage");

  cameraContainer.style.display = "none";
  imagePreview.style.display = "block";
  previewImage.src = src;
}

function removePreview() {
  const cameraContainer = document.getElementById("cameraContainer");
  const imagePreview = document.getElementById("imagePreview");

  imagePreview.style.display = "none";
  cameraContainer.style.display = "block";
  capturedBlob = null;
  document.getElementById("btnDetect").disabled = true;
  document.getElementById("fileInput").value = "";
}

// ============================================================
// Detection Function
// ============================================================
async function detectPothole() {
  if (!capturedBlob) {
    alert("Silakan ambil foto atau upload gambar terlebih dahulu!");
    return;
  }

  // Tampilkan loading
  showLoading(true);
  document.getElementById("btnDetect").disabled = true;

  // Kirim gambar ke server
  const formData = new FormData();
  formData.append("image", capturedBlob, "capture.jpg");

  try {
    const response = await fetch("/api/detect", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (result.success) {
      displayResult(result);
      loadStats();
      loadHistory();
    } else {
      alert("Error: " + result.message);
    }
  } catch (error) {
    console.error("Detection error:", error);
    alert("Gagal menghubungi server. Pastikan server berjalan.");
  } finally {
    showLoading(false);
    document.getElementById("btnDetect").disabled = false;
  }
}

// ============================================================
// Display Results
// ============================================================
function displayResult(result) {
  const emptyState = document.getElementById("emptyState");
  const resultContent = document.getElementById("resultContent");
  const resultStatus = document.getElementById("resultStatus");
  const statusIcon = document.getElementById("statusIcon");
  const statusTitle = document.getElementById("statusTitle");
  const statusMessage = document.getElementById("statusMessage");
  const resultImage = document.getElementById("resultImage");
  const detailGrid = document.getElementById("detailGrid");
  const detectionList = document.getElementById("detectionList");
  const potholeList = document.getElementById("potholeList");

  // Sembunyikan empty state, tampilkan hasil
  emptyState.style.display = "none";
  resultContent.style.display = "block";

  // Update status
  if (result.detected) {
    resultStatus.className = "result-status danger";
    statusIcon.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    statusTitle.textContent = "⚠️ Jalan Berlubang Terdeteksi!";
    statusMessage.textContent = result.message;
  } else {
    resultStatus.className = "result-status";
    statusIcon.innerHTML = '<i class="fas fa-check-circle"></i>';
    statusTitle.textContent = "✅ Jalan Aman";
    statusMessage.textContent = result.message;
  }

  // Tampilkan gambar hasil
  resultImage.src = result.result_image;

  // Detail grid
  detailGrid.innerHTML = `
        <div class="detail-item">
            <span class="label">Status</span>
            <span class="value" style="color: ${result.detected ? "var(--danger)" : "var(--success)"}">
                ${result.detected ? "Berlubang" : "Aman"}
            </span>
        </div>
        <div class="detail-item">
            <span class="label">Jumlah Lubang</span>
            <span class="value">${result.num_potholes}</span>
        </div>
        <div class="detail-item">
            <span class="label">Confidence</span>
            <span class="value">${(result.confidence * 100).toFixed(1)}%</span>
        </div>
        <div class="detail-item">
            <span class="label">Metode</span>
            <span class="value">${result.detections?.[0]?.method || "AI"}</span>
        </div>
    `;

  // Daftar lubang individual
  if (result.detected && result.detections && result.detections.length > 0) {
    detectionList.style.display = "block";
    potholeList.innerHTML = result.detections
      .map(
        (det, i) => `
            <div class="pothole-item">
                <div class="number">${i + 1}</div>
                <div class="info">
                    Ukuran: ${det.width}x${det.height}px
                    ${det.area ? `• Area: ${det.area}px²` : ""}
                </div>
                <div class="conf">${(det.confidence * 100).toFixed(0)}%</div>
            </div>
        `,
      )
      .join("");
  } else {
    detectionList.style.display = "none";
  }

  // Scroll ke hasil
  resultContent.scrollIntoView({ behavior: "smooth", block: "start" });
}

function showLoading(show) {
  const loading = document.getElementById("loading");
  const emptyState = document.getElementById("emptyState");
  const resultContent = document.getElementById("resultContent");

  if (show) {
    loading.style.display = "block";
    emptyState.style.display = "none";
    resultContent.style.display = "none";
  } else {
    loading.style.display = "none";
  }
}

// ============================================================
// Fullscreen Modal
// ============================================================
function openFullscreen(img) {
  const modal = document.getElementById("fullscreenModal");
  const fullImg = document.getElementById("fullscreenImage");
  fullImg.src = img.src;
  modal.classList.add("active");
}

function closeFullscreen() {
  document.getElementById("fullscreenModal").classList.remove("active");
}

// Keyboard shortcut
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeFullscreen();
});

// ============================================================
// Stats & History
// ============================================================
async function loadStats() {
  try {
    const res = await fetch("/api/stats");
    const data = await res.json();

    if (data.success) {
      document.getElementById("totalScans").textContent = data.total_scans;
      document.getElementById("totalDetected").textContent =
        data.total_detected;
      document.getElementById("totalPotholes").textContent =
        data.total_potholes;
      document.getElementById("detectionRate").textContent =
        data.detection_rate + "%";
    }
  } catch (e) {
    console.error("Failed to load stats:", e);
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();

    if (data.success && data.history.length > 0) {
      const historyList = document.getElementById("historyList");
      historyList.innerHTML = data.history
        .map(
          (item) => `
                <div class="history-item">
                    <div class="history-thumb">
                        <img src="/results/${item.result_image}" alt="Result" 
                             onerror="this.src='/uploads/${item.original_image}'">
                    </div>
                    <div class="history-info">
                        <div class="title">
                            ${item.detected ? `${item.num_potholes} lubang terdeteksi` : "Jalan aman"}
                        </div>
                        <div class="meta">
                            <i class="fas fa-clock"></i> ${item.timestamp}
                            ${item.confidence > 0 ? ` • Conf: ${(item.confidence * 100).toFixed(0)}%` : ""}
                        </div>
                    </div>
                    <span class="history-badge ${item.detected ? "danger" : "safe"}">
                        ${item.detected ? "Berlubang" : "Aman"}
                    </span>
                </div>
            `,
        )
        .join("");
    }
  } catch (e) {
    console.error("Failed to load history:", e);
  }
}

// ============================================================
// Initialize
// ============================================================
document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  loadHistory();

  // Request status
  socket.emit("request_status");
});
