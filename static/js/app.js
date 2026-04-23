/**
 * POTHOLE DETECTOR - VISKOM Cinta Damai
 * Frontend JavaScript Application
 *
 * Fitur:
 * - Live streaming kamera dengan deteksi real-time via WebSocket
 * - Upload gambar (mode alternatif)
 * - Real-time notification via WebSocket
 */

// ============================================================
// Global Variables
// ============================================================
let cameraStream = null;
let capturedBlob = null;
let isCameraActive = false;
let isStreaming = false;
let streamIntervalId = null;
let streamIntervalMs = 300;
let currentMode = "stream"; // 'stream' or 'upload'
let frameCount = 0;
let fpsTimer = null;
let lastAlertTime = 0;
const ALERT_COOLDOWN = 5000; // ms between alerts
let processingFrame = false;
let detectionLogEntries = [];
let sendWidth = 320; // resolusi kirim ke server
let sendHeight = 240;
let lastDetections = []; // cache deteksi terakhir untuk render bbox
let bboxAnimFrame = null;

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
  stopStreaming();
});

socket.on("connected", (data) => {
  console.log("[WS] Server:", data.message);
});

// Real-time pothole alert dari server
socket.on("pothole_alert", (data) => {
  console.log("[WS] ALERT:", data);
  const now = Date.now();
  if (now - lastAlertTime > ALERT_COOLDOWN) {
    showAlert(data.message);
    playAlertSound();
    showDesktopNotification(data);
    lastAlertTime = now;
  }
});

// Stream result dari server - sekarang hanya koordinat, bbox digambar di client
socket.on("stream_result", (data) => {
  processingFrame = false;

  if (!data.success) {
    console.warn("[STREAM] Error:", data.message);
    return;
  }

  frameCount++;

  // Simpan deteksi untuk digambar di canvas
  lastDetections = data.detections || [];

  // Update live detection info
  updateLiveDetectionInfo(data);
});

socket.on("server_status", (data) => {
  console.log("[WS] Server status:", data);
});

// ============================================================
// Mode Switching
// ============================================================
function setMode(mode) {
  currentMode = mode;
  const btnStream = document.getElementById("btnModeStream");
  const btnUpload = document.getElementById("btnModeUpload");
  const streamContainer = document.getElementById("streamContainer");
  const uploadContainer = document.getElementById("uploadContainer");
  const emptyState = document.getElementById("emptyState");
  const liveInfo = document.getElementById("liveDetectionInfo");
  const resultContent = document.getElementById("resultContent");

  if (mode === "stream") {
    btnStream.classList.add("active");
    btnUpload.classList.remove("active");
    streamContainer.style.display = "block";
    uploadContainer.style.display = "none";
    liveInfo.style.display = "block";
    emptyState.style.display = "none";
    resultContent.style.display = "none";
  } else {
    btnStream.classList.remove("active");
    btnUpload.classList.add("active");
    streamContainer.style.display = "none";
    uploadContainer.style.display = "block";
    liveInfo.style.display = "none";
    emptyState.style.display = "block";
    resultContent.style.display = "none";
    // Stop streaming if switching to upload mode
    if (isStreaming) stopStreaming();
  }
}

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
  const btnStream = document.getElementById("btnStream");
  const streamSettings = document.getElementById("streamSettings");

  try {
    const constraints = {
      video: {
        facingMode: { ideal: "environment" },
        width: { ideal: 640 },
        height: { ideal: 480 },
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

    if (currentMode === "stream") {
      btnStream.style.display = "inline-flex";
      streamSettings.style.display = "block";
    }

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
  const btnStream = document.getElementById("btnStream");
  const streamSettings = document.getElementById("streamSettings");

  // Stop streaming first
  if (isStreaming) stopStreaming();

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

  video.srcObject = null;
  overlay.classList.remove("hidden");
  btnCamera.innerHTML = '<i class="fas fa-video"></i><span>Buka Kamera</span>';
  btnCamera.classList.remove("active");
  btnCapture.style.display = "none";
  btnStream.style.display = "none";
  streamSettings.style.display = "none";
  isCameraActive = false;
}

function capturePhoto() {
  const video = document.getElementById("cameraPreview");
  const canvas = document.getElementById("cameraCanvas");

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0);

  canvas.toBlob(
    (blob) => {
      capturedBlob = blob;
      const previewUrl = URL.createObjectURL(blob);
      // Switch to upload mode to show preview & detect
      setMode("upload");
      showImagePreview(previewUrl);
      stopCamera();
      document.getElementById("btnDetect").disabled = false;
    },
    "image/jpeg",
    0.9,
  );
}

// ============================================================
// Streaming Functions
// ============================================================
function toggleStreaming() {
  if (isStreaming) {
    stopStreaming();
  } else {
    startStreaming();
  }
}

function startStreaming() {
  if (!isCameraActive) {
    alert("Buka kamera terlebih dahulu!");
    return;
  }

  isStreaming = true;
  processingFrame = false;
  frameCount = 0;
  lastDetections = [];

  const btnStream = document.getElementById("btnStream");
  const streamStatus = document.getElementById("streamStatus");
  const fpsCounter = document.getElementById("fpsCounter");
  const bboxCanvas = document.getElementById("bboxCanvas");

  btnStream.innerHTML = '<i class="fas fa-stop"></i><span>Stop Deteksi</span>';
  btnStream.classList.add("active");
  streamStatus.style.display = "flex";
  fpsCounter.style.display = "block";
  bboxCanvas.style.display = "block";

  // Show live detection panel
  document.getElementById("emptyState").style.display = "none";
  document.getElementById("liveDetectionInfo").style.display = "block";
  document.getElementById("resultContent").style.display = "none";
  document.getElementById("liveStreamState").textContent = "Streaming";

  // Start sending frames
  streamIntervalId = setInterval(() => {
    if (!processingFrame && isCameraActive && isStreaming) {
      sendFrame();
    }
  }, streamIntervalMs);

  // FPS counter
  fpsTimer = setInterval(() => {
    document.getElementById("fpsValue").textContent = frameCount;
    frameCount = 0;
  }, 1000);

  // Start bbox rendering loop
  startBboxRenderLoop();
}

function stopStreaming() {
  isStreaming = false;
  lastDetections = [];

  if (streamIntervalId) {
    clearInterval(streamIntervalId);
    streamIntervalId = null;
  }
  if (fpsTimer) {
    clearInterval(fpsTimer);
    fpsTimer = null;
  }
  if (bboxAnimFrame) {
    cancelAnimationFrame(bboxAnimFrame);
    bboxAnimFrame = null;
  }

  const btnStream = document.getElementById("btnStream");
  const streamStatus = document.getElementById("streamStatus");
  const fpsCounter = document.getElementById("fpsCounter");
  const bboxCanvas = document.getElementById("bboxCanvas");

  btnStream.innerHTML = '<i class="fas fa-play"></i><span>Mulai Deteksi</span>';
  btnStream.classList.remove("active");
  streamStatus.style.display = "none";
  fpsCounter.style.display = "none";
  bboxCanvas.style.display = "none";

  // Clear canvas
  const ctx = bboxCanvas.getContext("2d");
  ctx.clearRect(0, 0, bboxCanvas.width, bboxCanvas.height);

  document.getElementById("liveStreamState").textContent = "Idle";
}

function sendFrame() {
  const video = document.getElementById("cameraPreview");
  const canvas = document.getElementById("cameraCanvas");

  if (!video.videoWidth || !video.videoHeight) return;

  // Kirim resolusi kecil ke server untuk percepat proses
  canvas.width = sendWidth;
  canvas.height = sendHeight;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, sendWidth, sendHeight);

  const dataURL = canvas.toDataURL("image/jpeg", 0.5);

  processingFrame = true;
  socket.emit("stream_frame", { image: dataURL });
}

// ============================================================
// Bounding Box Canvas Rendering (client-side)
// ============================================================
function startBboxRenderLoop() {
  function renderBbox() {
    if (!isStreaming) return;
    drawBboxOnCanvas();
    bboxAnimFrame = requestAnimationFrame(renderBbox);
  }
  bboxAnimFrame = requestAnimationFrame(renderBbox);
}

function drawBboxOnCanvas() {
  const video = document.getElementById("cameraPreview");
  const bboxCanvas = document.getElementById("bboxCanvas");
  if (!video || !bboxCanvas) return;

  const displayW = bboxCanvas.clientWidth;
  const displayH = bboxCanvas.clientHeight;

  // Set canvas resolution to match display size
  if (bboxCanvas.width !== displayW || bboxCanvas.height !== displayH) {
    bboxCanvas.width = displayW;
    bboxCanvas.height = displayH;
  }

  const ctx = bboxCanvas.getContext("2d");
  ctx.clearRect(0, 0, displayW, displayH);

  if (!lastDetections || lastDetections.length === 0) return;

  const videoW = video.videoWidth || sendWidth;
  const videoH = video.videoHeight || sendHeight;

  // Scale factors: server coords are based on sendWidth x sendHeight
  const scaleX = displayW / sendWidth;
  const scaleY = displayH / sendHeight;

  for (const det of lastDetections) {
    const [x1, y1, x2, y2] = det.bbox;
    const conf = det.confidence;

    // Scale coordinates to canvas display
    const dx1 = x1 * scaleX;
    const dy1 = y1 * scaleY;
    const dx2 = x2 * scaleX;
    const dy2 = y2 * scaleY;
    const dw = dx2 - dx1;
    const dh = dy2 - dy1;

    // Color based on confidence
    let color;
    if (conf > 0.7) color = "#ef4444";
    else if (conf > 0.5) color = "#f97316";
    else color = "#eab308";

    // Draw filled semi-transparent rectangle
    ctx.fillStyle = color + "30"; // alpha
    ctx.fillRect(dx1, dy1, dw, dh);

    // Draw border
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.strokeRect(dx1, dy1, dw, dh);

    // Label background
    const label = `Lubang ${Math.round(conf * 100)}%`;
    ctx.font = "bold 14px sans-serif";
    const textW = ctx.measureText(label).width;
    const labelH = 22;
    ctx.fillStyle = color;
    ctx.fillRect(dx1, dy1 - labelH, textW + 8, labelH);

    // Label text
    ctx.fillStyle = "#ffffff";
    ctx.fillText(label, dx1 + 4, dy1 - 6);
  }
}

function updateStreamInterval() {
  streamIntervalMs = parseInt(document.getElementById("streamInterval").value);
  if (isStreaming) {
    clearInterval(streamIntervalId);
    streamIntervalId = setInterval(() => {
      if (!processingFrame && isCameraActive && isStreaming) {
        sendFrame();
      }
    }, streamIntervalMs);
  }
}

function updateStreamResolution() {
  const val = document.getElementById("streamResolution").value;
  const [w, h] = val.split("x").map(Number);
  sendWidth = w;
  sendHeight = h;
}

// ============================================================
// Live Detection Info Update
// ============================================================
function updateLiveDetectionInfo(data) {
  const statusEl = document.getElementById("liveResultStatus");
  const iconEl = document.getElementById("liveStatusIcon");
  const titleEl = document.getElementById("liveStatusTitle");
  const msgEl = document.getElementById("liveStatusMessage");

  if (data.detected) {
    statusEl.className = "result-status danger";
    iconEl.innerHTML = '<i class="fas fa-exclamation-triangle"></i>';
    titleEl.textContent = "⚠️ Jalan Berlubang Terdeteksi!";
    msgEl.textContent = data.message;
  } else {
    statusEl.className = "result-status safe";
    iconEl.innerHTML = '<i class="fas fa-check-circle"></i>';
    titleEl.textContent = "✅ Jalan Aman";
    msgEl.textContent = data.message;
  }

  document.getElementById("liveNumPotholes").textContent = data.num_potholes;
  document.getElementById("liveConfidence").textContent =
    data.confidence > 0 ? (data.confidence * 100).toFixed(1) + "%" : "-";
  document.getElementById("liveMethod").textContent = data.method || "AI";

  // Add to detection log if pothole detected
  if (data.detected) {
    addDetectionLog(data);
  }
}

function addDetectionLog(data) {
  const logContainer = document.getElementById("detectionLog");
  const now = new Date().toLocaleTimeString("id-ID");

  detectionLogEntries.unshift({
    time: now,
    num: data.num_potholes,
    confidence: data.confidence,
  });

  // Keep only last 10 entries
  if (detectionLogEntries.length > 10) {
    detectionLogEntries = detectionLogEntries.slice(0, 10);
  }

  logContainer.innerHTML = detectionLogEntries
    .map(
      (entry) => `
      <div class="log-entry danger">
        <span class="log-time">${entry.time}</span>
        <span class="log-info">${entry.num} lubang (${(entry.confidence * 100).toFixed(0)}%)</span>
      </div>
    `,
    )
    .join("");
}

// ============================================================
// File Upload Functions
// ============================================================
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (!file) return;

  const allowedTypes = ["image/jpeg", "image/png", "image/webp", "image/bmp"];
  if (!allowedTypes.includes(file.type)) {
    alert("Format file tidak didukung!\nGunakan: JPG, PNG, WEBP, atau BMP");
    return;
  }

  if (file.size > 16 * 1024 * 1024) {
    alert("Ukuran file terlalu besar! Maksimal 16MB.");
    return;
  }

  capturedBlob = file;

  const reader = new FileReader();
  reader.onload = (e) => {
    showImagePreview(e.target.result);
  };
  reader.readAsDataURL(file);

  document.getElementById("btnDetect").disabled = false;
}

function showImagePreview(src) {
  const imagePreview = document.getElementById("imagePreview");
  const previewImage = document.getElementById("previewImage");
  const uploadZone = document.getElementById("uploadZone");

  uploadZone.style.display = "none";
  imagePreview.style.display = "block";
  previewImage.src = src;
}

function removePreview() {
  const imagePreview = document.getElementById("imagePreview");
  const uploadZone = document.getElementById("uploadZone");

  imagePreview.style.display = "none";
  uploadZone.style.display = "flex";
  capturedBlob = null;
  document.getElementById("btnDetect").disabled = true;
  document.getElementById("fileInput").value = "";
}

// ============================================================
// Detection Function (Upload Mode)
// ============================================================
async function detectPothole() {
  if (!capturedBlob) {
    alert("Silakan ambil foto atau upload gambar terlebih dahulu!");
    return;
  }

  showLoading(true);
  document.getElementById("btnDetect").disabled = true;

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
// Display Results (Upload Mode)
// ============================================================
function displayResult(result) {
  const emptyState = document.getElementById("emptyState");
  const resultContent = document.getElementById("resultContent");
  const liveInfo = document.getElementById("liveDetectionInfo");
  const resultStatus = document.getElementById("resultStatus");
  const statusIcon = document.getElementById("statusIcon");
  const statusTitle = document.getElementById("statusTitle");
  const statusMessage = document.getElementById("statusMessage");
  const resultImage = document.getElementById("resultImage");
  const detailGrid = document.getElementById("detailGrid");
  const detectionList = document.getElementById("detectionList");
  const potholeList = document.getElementById("potholeList");

  emptyState.style.display = "none";
  liveInfo.style.display = "none";
  resultContent.style.display = "block";

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

  resultImage.src = result.result_image;

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
  socket.emit("request_status");
  // Default to stream mode
  setMode("stream");
});
