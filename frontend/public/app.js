/**
 * Sakshi ALPR India - Frontend Application Engine (Light Minimal)
 * Supports Photo & Video Upload with Multi-Vehicle / Bike License Plate extraction
 */

const BACKEND_URL = window.BACKEND_API_URL || "http://localhost:8000";

let webcamStream = null;
let isStreaming = false;
let streamAnimationId = null;
let lastFrameTime = performance.now();
let frameCount = 0;

document.addEventListener("DOMContentLoaded", () => {
  loadStats();
  setupDropZone();
  setInterval(loadStats, 8000);
});

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

async function uploadPhoto(file) {
  showUploadLoading(true, "Processing vehicle photo & analyzing license plates...");
  document.getElementById("annotatedImageWrapper").classList.remove("hidden");

  const formData = new FormData();
  formData.append("file", file);

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
  showUploadLoading(true, "Scanning video frames for all car & bike license plates...");
  document.getElementById("annotatedImageWrapper").classList.add("hidden");

  const formData = new FormData();
  formData.append("file", file);

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
  document.getElementById("uploadSuccessMessage").innerHTML = `
    <i class="fa-solid fa-circle-check text-emerald-600"></i>
    <span>Photo processed & stored in Database!</span>
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
  const badgeClass = p.is_valid ? "bg-emerald-100 text-emerald-800 border-emerald-300" : "bg-slate-100 text-slate-700 border-slate-300";
  const badgeText = p.is_valid ? "Verified Indian HSRP" : "Standard Plate";
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

      <!-- Authentic HSRP Plate Graphic -->
      <div class="flex items-center justify-center my-1.5">
        <div class="hsrp-plate">
          <div class="hsrp-strip">
            <div class="hsrp-chakra"></div>
            <span class="text-[9px] font-black tracking-widest mt-1">IND</span>
          </div>
          <div class="hsrp-text">
            ${p.plate_number}
          </div>
        </div>
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
  const search = document.getElementById("dbSearchInput").value;
  const state = document.getElementById("dbStateFilter").value;
  const tbody = document.getElementById("dbTableBody");

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
      const hsrpPill = r.is_valid_format
        ? `<span class="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded text-[10px] font-bold">YES</span>`
        : `<span class="px-2 py-0.5 bg-slate-100 text-slate-600 border border-slate-200 rounded text-[10px] font-bold">NO</span>`;

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

function viewEvidence(cropUrl, fullUrl, plateNumber) {
  document.getElementById("modalPlateTitle").innerText = `Evidence: ${plateNumber}`;
  const cropImg = document.getElementById("modalCropImg");
  const fullImg = document.getElementById("modalFullImg");

  cropImg.src = cropUrl ? `${BACKEND_URL}${cropUrl}` : "";
  fullImg.src = fullUrl ? `${BACKEND_URL}${fullUrl}` : "";

  document.getElementById("evidenceModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("evidenceModal").classList.add("hidden");
}

function exportCSV() {
  window.open(`${BACKEND_URL}/api/v1/records/export/csv`, "_blank");
}
