/**
 * Sakshi ALPR India - Frontend Application Engine (Light Minimal)
 * Supports Photo & Video Upload with Multi-Vehicle / Bike License Plate extraction
 */

function getBackendUrl() {
  if (window.BACKEND_API_URL && window.BACKEND_API_URL.trim()) {
    return window.BACKEND_API_URL.trim().replace(/\/+$/, "");
  }
  const saved = localStorage.getItem("SAKSHI_BACKEND_URL");
  if (saved && saved.trim()) {
    return saved.trim().replace(/\/+$/, "");
  }
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://localhost:8000";
  }
  // Default Render production URL
  return "https://sakshi-alpr.onrender.com";
}

let BACKEND_URL = getBackendUrl();

let webcamStream = null;
let isStreaming = false;
let streamAnimationId = null;
let lastFrameTime = performance.now();
let frameCount = 0;

document.addEventListener("DOMContentLoaded", () => {
  updateBackendPill();
  loadStats();
  setupDropZone();
  setInterval(() => {
    if (BACKEND_URL) loadStats();
  }, 8000);
});

function updateBackendPill() {
  const label = document.getElementById("backendStatusLabel");
  const dot = document.getElementById("backendStatusDot");
  if (!label || !dot) return;

  if (!BACKEND_URL) {
    label.innerText = "Connect Render API";
    dot.className = "w-2 h-2 rounded-full bg-amber-500 animate-pulse";
    return;
  }

  try {
    const parsed = new URL(BACKEND_URL);
    const host = parsed.hostname;
    label.innerText = host.includes("onrender.com") ? "Render Active" : host;
    dot.className = "w-2 h-2 rounded-full bg-emerald-500";
  } catch (e) {
    label.innerText = "API Connected";
    dot.className = "w-2 h-2 rounded-full bg-emerald-500";
  }
}

function promptBackendUrl() {
  const input = document.getElementById("backendUrlInput");
  if (input) input.value = BACKEND_URL || "";
  document.getElementById("backendUrlModal").classList.remove("hidden");
}

function closeBackendModal() {
  document.getElementById("backendUrlModal").classList.add("hidden");
}

function saveBackendUrl() {
  const input = document.getElementById("backendUrlInput");
  let val = (input.value || "").trim().replace(/\/+$/, "");
  if (!val) {
    alert("Please enter a valid backend URL.");
    return;
  }
  if (!val.startsWith("http://") && !val.startsWith("https://")) {
    val = "https://" + val;
  }
  localStorage.setItem("SAKSHI_BACKEND_URL", val);
  BACKEND_URL = val;
  closeBackendModal();
  updateBackendPill();
  loadStats();
  if (document.getElementById("tab-database") && !document.getElementById("tab-database").classList.contains("hidden")) {
    loadDatabaseRecords();
  }
}

function resetLocalBackendUrl() {
  localStorage.removeItem("SAKSHI_BACKEND_URL");
  BACKEND_URL = "http://localhost:8000";
  closeBackendModal();
  updateBackendPill();
  loadStats();
}

// ================= TAB NAVIGATION =================
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  document.querySelectorAll(".tab-btn").forEach(el => {
    el.classList.remove("active", "border-blue-600", "text-blue-600", "font-semibold");
    el.classList.add("border-transparent", "text-slate-500", "font-medium");
  });

  const targetTab = document.getElementById(`tab-${tabId}`);
  const targetBtn = document.getElementById(`tabBtn-${tabId}`);

  if (targetTab) targetTab.classList.remove("hidden");
  if (targetBtn) {
    targetBtn.classList.add("active", "border-blue-600", "text-blue-600", "font-semibold");
    targetBtn.classList.remove("border-transparent", "text-slate-500");
  }

  if (tabId === "database") {
    loadDatabaseRecords();
  }
}

// ================= STATS LOADER =================
async function loadStats() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/stats`);
    if (!res.ok) return;
    const data = await res.json();
    const s = data.stats;

    document.getElementById("statTotalScans").innerText = s.total_scans;
    document.getElementById("statUniquePlates").innerText = s.unique_plates;
    document.getElementById("statValidPlates").innerText = s.valid_plates;
    document.getElementById("statAvgConf").innerText = `${s.avg_confidence}%`;
  } catch (err) {
    console.warn("Backend not reachable yet:", err);
  }
}

// ================= UPLOAD HANDLING (PHOTO & VIDEO) =================
function setupDropZone() {
  const dropZone = document.getElementById("dropZone");
  const fileInput = document.getElementById("fileInput");

  dropZone.addEventListener("click", () => fileInput.click());

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("border-blue-500", "bg-blue-50/50");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("border-blue-500", "bg-blue-50/50");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  });
}

async function handleFileUpload(file) {
  const isVideo = file.type.startsWith("video/") || /\.(mp4|avi|mov|mkv|webm)$/i.test(file.name);

  if (isVideo) {
    uploadVideo(file);
  } else {
    uploadPhoto(file);
  }
}

let currentEngine = "ai";

function setEngineMode(mode) {
  currentEngine = mode;
  const btnAI = document.getElementById("btnEngineAI");
  const btnLocal = document.getElementById("btnEngineLocal");

  if (mode === "ai") {
    btnAI.className = "py-2 px-3 text-xs font-bold rounded-lg transition flex items-center justify-center space-x-1.5 bg-white text-indigo-700 shadow-sm border border-slate-200";
    btnLocal.className = "py-2 px-3 text-xs font-semibold rounded-lg transition flex items-center justify-center space-x-1.5 text-slate-600 hover:text-slate-900";
  } else {
    btnLocal.className = "py-2 px-3 text-xs font-bold rounded-lg transition flex items-center justify-center space-x-1.5 bg-white text-blue-700 shadow-sm border border-slate-200";
    btnAI.className = "py-2 px-3 text-xs font-semibold rounded-lg transition flex items-center justify-center space-x-1.5 text-slate-600 hover:text-slate-900";
  }
}

async function uploadPhoto(file) {
  if (!BACKEND_URL) {
    promptBackendUrl();
    return;
  }
  const engineLabel = currentEngine === "ai" ? "Gemini Vision AI (100% Accuracy)" : "Local YOLOv8 Engine";
  showUploadLoading(true, `Processing photo with ${engineLabel}...`);
  document.getElementById("annotatedImageWrapper").classList.remove("hidden");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("engine", currentEngine);

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/detect/upload`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    showUploadLoading(false);

    if (data.success) {
      renderPhotoResults(data);
      loadStats();
    } else {
      alert("Detection failed: " + (data.detail || "Unknown error"));
    }
  } catch (err) {
    showUploadLoading(false);
    alert("Could not reach backend server at " + BACKEND_URL);
  }
}

async function uploadVideo(file) {
  if (!BACKEND_URL) {
    promptBackendUrl();
    return;
  }
  const engineLabel = currentEngine === "ai" ? "Gemini Vision AI" : "Local YOLOv8 Engine";
  showUploadLoading(true, `Scanning video frames with ${engineLabel}...`);
  document.getElementById("annotatedImageWrapper").classList.add("hidden");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("engine", currentEngine);

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/detect/upload-video`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    showUploadLoading(false);

    if (data.success) {
      renderVideoResults(data);
      loadStats();
    } else {
      alert("Video processing failed: " + (data.detail || "Unknown error"));
    }
  } catch (err) {
    showUploadLoading(false);
    alert("Could not reach backend server at " + BACKEND_URL);
  }
}

function showUploadLoading(isLoading, message = "Processing...") {
  document.getElementById("uploadPlaceholder").classList.add("hidden");
  document.getElementById("uploadResults").classList.add("hidden");
  const loader = document.getElementById("uploadLoading");
  const loaderText = document.getElementById("uploadLoadingText");
  loaderText.innerText = message;

  if (isLoading) {
    loader.classList.remove("hidden");
  } else {
    loader.classList.add("hidden");
  }
}

function renderPhotoResults(data) {
  const container = document.getElementById("uploadResults");
  container.classList.remove("hidden");

  document.getElementById("saveTimestamp").innerText = new Date().toLocaleTimeString();
  const engineText = data.engine ? `via <strong class="text-indigo-700">${data.engine}</strong>` : "processed";
  document.getElementById("uploadSuccessMessage").innerHTML = `
    <i class="fa-solid fa-circle-check text-emerald-600"></i>
    <span>Photo ${engineText} & stored in Database!</span>
  `;

  // Show annotated image
  const imgEl = document.getElementById("uploadAnnotatedImg");
  imgEl.src = data.annotated_image;

  // Render plates
  const count = data.plates ? data.plates.length : 0;
  document.getElementById("platesFoundHeading").innerText = "Recognized License Plates";
  document.getElementById("platesCountBadge").innerText = `${count} Plate(s) Found`;

  const platesList = document.getElementById("uploadPlatesList");
  platesList.innerHTML = "";

  if (count === 0) {
    platesList.innerHTML = `
      <div class="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs">
        <i class="fa-solid fa-triangle-exclamation mr-1.5 text-amber-600"></i> No license plate recognized in this image.
      </div>
    `;
    return;
  }

  data.plates.forEach((p, idx) => {
    platesList.innerHTML += createPlateHTML(p, idx + 1);
  });
}

function renderVideoResults(data) {
  const container = document.getElementById("uploadResults");
  container.classList.remove("hidden");

  document.getElementById("saveTimestamp").innerText = new Date().toLocaleTimeString();
  document.getElementById("uploadSuccessMessage").innerHTML = `
    <i class="fa-solid fa-circle-check text-emerald-600"></i>
    <span>Video processed: Scanned ${data.processed_frames} frames (${data.duration_seconds}s)</span>
  `;

  const count = data.unique_plates_count || 0;
  document.getElementById("platesFoundHeading").innerText = "Unique Vehicle & Bike Plates Found in Video";
  document.getElementById("platesCountBadge").innerText = `${count} Unique Plates Logged`;

  const platesList = document.getElementById("uploadPlatesList");
  platesList.innerHTML = "";

  if (count === 0) {
    platesList.innerHTML = `
      <div class="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-800 text-xs">
        <i class="fa-solid fa-triangle-exclamation mr-1.5 text-amber-600"></i> No license plates detected across the uploaded video.
      </div>
    `;
    return;
  }

  data.plates.forEach((p, idx) => {
    platesList.innerHTML += createPlateHTML(p, idx + 1, p.timestamp_in_video);
  });
}

function createPlateHTML(p, num, videoTimestamp = null) {
  let badgeClass, badgeText;
  if (p.is_hsrp) {
    badgeClass = "bg-blue-100 text-blue-800 border-blue-300";
    badgeText = `<i class="fa-solid fa-shield mr-1 text-blue-600"></i>Verified Indian HSRP`;
  } else if (p.is_valid) {
    badgeClass = "bg-emerald-100 text-emerald-800 border-emerald-300";
    badgeText = `<i class="fa-solid fa-file-lines mr-1 text-emerald-600"></i>Standard Non-HSRP Plate`;
  } else {
    badgeClass = "bg-amber-100 text-amber-800 border-amber-300";
    badgeText = `<i class="fa-solid fa-triangle-exclamation mr-1 text-amber-600"></i>Fancy / Non-Standard Plate`;
  }

  const recordId = p.db_record ? p.db_record.id : "Saved";

  const videoPill = videoTimestamp ? `
    <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-purple-50 text-purple-700 border border-purple-200">
      <i class="fa-solid fa-clock text-[9px] mr-1"></i>Seen at ${videoTimestamp}
    </span>
  ` : '';

  const cropPreview = p.crop_base64 ? `
    <div class="flex items-center justify-center p-2 bg-slate-50 rounded-xl border border-slate-200">
      <img src="${p.crop_base64}" class="max-h-16 rounded border border-slate-300 shadow-sm" alt="Plate Crop" />
    </div>
  ` : '';

  // Render graphic plate: authentic blue strip if verified HSRP, or clean border if standard/non-HSRP
  const plateGraphic = p.is_hsrp ? `
    <div class="hsrp-plate">
      <div class="hsrp-strip">
        <div class="hsrp-chakra"></div>
        <span class="text-[9px] font-black tracking-widest mt-1">IND</span>
      </div>
      <div class="hsrp-text">
        ${p.plate_number}
      </div>
    </div>
  ` : `
    <div class="hsrp-plate" style="padding-left: 20px;">
      <div class="hsrp-text">
        ${p.plate_number}
      </div>
    </div>
  `;

  return `
    <div class="card-clean p-4 space-y-3 border border-slate-200">
      <div class="flex items-center justify-between text-xs">
        <div class="flex items-center space-x-2">
          <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${badgeClass}">
            ${badgeText}
          </span>
          ${videoPill}
          <span class="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
            Saved in DB (#${recordId})
          </span>
        </div>
        <span class="font-medium text-slate-500">
          Accuracy: <strong class="text-blue-600">${p.confidence}%</strong>
        </span>
      </div>

      <!-- License Plate Graphic -->
      <div class="flex items-center justify-center my-1.5">
        ${plateGraphic}
      </div>

      ${cropPreview}

      <!-- Regional Breakdown Details -->
      <div class="grid grid-cols-2 gap-2.5 p-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs">
        <div>
          <span class="text-slate-500 text-[10px] uppercase font-semibold block">State:</span>
          <strong class="text-slate-800">${p.state_name} (${p.state_code})</strong>
        </div>
        <div>
          <span class="text-slate-500 text-[10px] uppercase font-semibold block">Regional RTO / District:</span>
          <strong class="text-blue-700">${p.rto_district}</strong>
        </div>
      </div>
    </div>
  `;
}

// ================= WEBCAM SNAPSHOT =================
async function startWebcam() {
  const video = document.getElementById("snapshotVideo");
  const standby = document.getElementById("cameraStandby");
  const btnSnap = document.getElementById("btnSnap");
  const btnStart = document.getElementById("btnStartCam");

  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { width: 1280, height: 720 },
      audio: false,
    });
    video.srcObject = webcamStream;
    video.classList.remove("hidden");
    standby.classList.add("hidden");
    btnSnap.disabled = false;
    btnStart.innerHTML = `<i class="fa-solid fa-check mr-1 text-[10px]"></i> Camera Active`;
    btnStart.classList.replace("bg-slate-900", "bg-emerald-600");
  } catch (err) {
    alert("Camera access denied or unavailable: " + err.message);
  }
}

async function captureSnapshot() {
  const video = document.getElementById("snapshotVideo");
  const canvas = document.getElementById("snapshotCanvas");
  const resultBox = document.getElementById("snapshotActiveResult");
  const placeholder = document.getElementById("snapshotPlaceholder");
  const loader = document.getElementById("snapshotLoading");

  if (!webcamStream) return;

  canvas.width = video.videoWidth || 1280;
  canvas.height = video.videoHeight || 720;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  const base64Data = canvas.toDataURL("image/jpeg", 0.92);

  placeholder.classList.add("hidden");
  resultBox.classList.add("hidden");
  loader.classList.remove("hidden");

  try {
    const res = await fetch(`${BACKEND_URL}/api/v1/detect/snapshot`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_base64: base64Data, detection_mode: "Live Snapshot" }),
    });

    const data = await res.json();
    loader.classList.add("hidden");
    resultBox.classList.remove("hidden");

    if (data.success) {
      resultBox.innerHTML = `
        <div class="rounded-xl overflow-hidden border border-slate-200 bg-slate-900 max-h-[220px]">
          <img src="${data.annotated_image}" class="w-full object-contain" />
        </div>
      `;
      if (data.plates && data.plates.length > 0) {
        data.plates.forEach((p, idx) => {
          resultBox.innerHTML += createPlateHTML(p, idx + 1);
        });
      } else {
        resultBox.innerHTML += `<div class="p-3 bg-amber-50 border border-amber-200 text-amber-800 text-xs rounded-xl">No plate recognized in this snapshot.</div>`;
      }
      loadStats();
    }
  } catch (err) {
    loader.classList.add("hidden");
    alert("Snapshot processing error: " + err.message);
  }
}

// ================= REAL-TIME STREAM =================
async function toggleStream() {
  const btn = document.getElementById("btnToggleStream");
  const btnText = document.getElementById("streamBtnText");
  const video = document.getElementById("streamVideo");
  const standby = document.getElementById("streamStandby");

  if (isStreaming) {
    isStreaming = false;
    if (streamAnimationId) cancelAnimationFrame(streamAnimationId);
    if (video.srcObject) {
      video.srcObject.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }
    btn.classList.replace("bg-red-600", "bg-emerald-600");
    btnText.innerText = "Start Stream";
    standby.classList.remove("hidden");
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { width: 960, height: 540 },
      audio: false,
    });
    video.srcObject = stream;
    standby.classList.add("hidden");
    isStreaming = true;

    btn.classList.replace("bg-emerald-600", "bg-red-600");
    btnText.innerText = "Stop Stream";

    runStreamLoop();
  } catch (err) {
    alert("Could not start video stream: " + err.message);
  }
}

let isProcessingFrame = false;

async function runStreamLoop() {
  if (!isStreaming) return;

  const video = document.getElementById("streamVideo");
  const canvas = document.getElementById("streamCanvas");
  const ctx = canvas.getContext("2d");

  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    frameCount++;
    const now = performance.now();
    if (now - lastFrameTime >= 1000) {
      const fps = (frameCount * 1000) / (now - lastFrameTime);
      document.getElementById("liveFps").innerText = `FPS: ${fps.toFixed(1)}`;
      frameCount = 0;
      lastFrameTime = now;
    }

    if (!isProcessingFrame) {
      isProcessingFrame = true;
      const b64 = canvas.toDataURL("image/jpeg", 0.7);

      fetch(`${BACKEND_URL}/api/v1/detect/stream-frame`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image_base64: b64, detection_mode: "Live Stream" }),
      })
        .then((res) => res.json())
        .then((data) => {
          isProcessingFrame = false;
          if (data.plates && data.plates.length > 0) {
            appendStreamTicker(data.plates[0]);
            loadStats();
          }
        })
        .catch(() => {
          isProcessingFrame = false;
        });
    }
  }

  streamAnimationId = requestAnimationFrame(runStreamLoop);
}

function appendStreamTicker(plate) {
  const ticker = document.getElementById("streamTickerList");
  const item = document.createElement("div");
  item.className = "p-3 rounded-xl bg-white border border-slate-200 shadow-sm space-y-1 text-xs animate-fade-in";
  item.innerHTML = `
    <div class="flex items-center justify-between">
      <span class="font-mono font-bold text-slate-900 text-sm">${plate.plate_number}</span>
      <span class="text-[10px] text-emerald-600 font-semibold"><i class="fa-solid fa-cloud-arrow-up mr-0.5"></i> Stored</span>
    </div>
    <div class="text-[11px] text-slate-500">${plate.rto_district} • ${new Date().toLocaleTimeString()}</div>
  `;
  ticker.prepend(item);

  if (ticker.children.length > 20) {
    ticker.removeChild(ticker.lastChild);
  }
}

// ================= DATABASE TABLE LOADER =================
async function loadDatabaseRecords() {
  const tbody = document.getElementById("dbTableBody");
  if (!BACKEND_URL) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-10 text-amber-600"><i class="fa-solid fa-plug text-lg mb-1 block text-amber-500"></i>Backend API not connected. <button onclick="promptBackendUrl()" class="underline font-bold text-blue-600">Connect your Render API</button></td></tr>`;
    return;
  }
  const search = document.getElementById("dbSearchInput").value;
  const state = document.getElementById("dbStateFilter").value;

  let url = `${BACKEND_URL}/api/v1/records?limit=100`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  if (state && state !== "All") url += `&state=${encodeURIComponent(state)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    tbody.innerHTML = "";

    if (!data.records || data.records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="9" class="text-center py-10 text-slate-400">No records found matching filters.</td></tr>`;
      return;
    }

    data.records.forEach((r) => {
      let hsrpPill;
      if (r.is_hsrp) {
        hsrpPill = `<span class="px-2 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded text-[10px] font-bold"><i class="fa-solid fa-shield mr-1"></i>HSRP</span>`;
      } else if (r.is_valid_format) {
        hsrpPill = `<span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-[10px] font-bold">Standard</span>`;
      } else {
        hsrpPill = `<span class="px-2 py-0.5 bg-slate-100 text-slate-600 border border-slate-200 rounded text-[10px] font-bold">Non-Std</span>`;
      }

      tbody.innerHTML += `
        <tr class="hover:bg-slate-50/80 transition">
          <td class="py-3 px-4 font-mono text-slate-400">#${r.id}</td>
          <td class="py-3 px-4 text-slate-500">${r.timestamp}</td>
          <td class="py-3 px-4 font-mono font-bold text-slate-900">${r.plate_number}</td>
          <td class="py-3 px-4 font-semibold text-slate-700">${r.state_code}</td>
          <td class="py-3 px-4 text-slate-600">${r.rto_district}</td>
          <td class="py-3 px-4 font-bold text-blue-600">${r.confidence}%</td>
          <td class="py-3 px-4 text-slate-500">${r.detection_mode}</td>
          <td class="py-3 px-4">${hsrpPill}</td>
          <td class="py-3 px-4 text-right">
            <button onclick="viewEvidence('${r.crop_image_url || ''}', '${r.full_image_url || ''}', '${r.plate_number}')" class="px-2.5 py-1 bg-white hover:bg-slate-100 text-slate-700 rounded-lg text-[11px] font-semibold border border-slate-200 shadow-sm transition">
              <i class="fa-solid fa-eye mr-1 text-slate-400"></i> View
            </button>
          </td>
        </tr>
      `;
    });
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="9" class="text-center py-10 text-red-500">Failed to load records from ${BACKEND_URL}</td></tr>`;
  }
}

function renderEvidenceSlot(container, url, label) {
  const clean = url && url !== "null" && url !== "undefined" && url !== "None" ? url.trim() : "";
  if (!clean) {
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center p-6 text-slate-400 text-center">
        <i class="fa-solid fa-camera-slash text-2xl mb-1.5 text-slate-300"></i>
        <span class="text-xs font-medium">No ${label.toLowerCase()} logged for this scan</span>
      </div>`;
    return;
  }

  const fullUrl = clean.startsWith("http://") || clean.startsWith("https://")
    ? clean
    : `${BACKEND_URL}${clean.startsWith("/") ? "" : "/"}${clean}`;

  container.innerHTML = `
    <div class="w-full flex items-center justify-center p-1">
      <img src="${fullUrl}" class="w-full object-contain max-h-44 rounded-lg shadow-sm" alt="${label}"
           onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\\'flex flex-col items-center justify-center p-6 text-slate-400 text-center\\'><i class=\\'fa-solid fa-image-slash text-2xl mb-1.5 text-slate-300\\'></i><span class=\\'text-xs font-medium\\'>${label} file not on server</span></div>';">
    </div>`;
}

function viewEvidence(cropUrl, fullUrl, plateNumber) {
  document.getElementById("modalPlateTitle").innerText = `Evidence: ${plateNumber}`;
  const cropContainer = document.getElementById("modalCropContainer");
  const fullContainer = document.getElementById("modalFullContainer");

  renderEvidenceSlot(cropContainer, cropUrl, "Plate Crop");
  renderEvidenceSlot(fullContainer, fullUrl, "Vehicle Snapshot");

  document.getElementById("evidenceModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("evidenceModal").classList.add("hidden");
}

function exportCSV() {
  window.open(`${BACKEND_URL}/api/v1/records/export/csv`, "_blank");
}
