/**
 * SPACI 2.0 - Aerospace Mission Control HUD Controller
 * Pure Vanilla JavaScript: Multi-Workspace HUD, Video Kinematics, Live Telemetry
 */

// ============================================================================
// State Management
// ============================================================================
const state = {
  // Navigation
  activeTab: "tabVideo",

  // Global Telemetry Data (Displayed in Dedicated Table & Exported)
  currentTelemetry: [],
  currentSummary: null,
  tableFilter: "all",

  // Video Mode State
  isVideoMode: true,
  videoFile: null,
  videoTracks: [],
  videoSummary: null,
  videoConf: 0.25,
  videoIou: 0.45,
  telemetrySpeed: 7500,
  telemetryAltitude: 650,

  // Gallery / Single-Frame Inspection State
  activeSample: null,
  activeImageData: null,
  uploadedImageFile: null,
  imageDetections: [],
  imageSummary: null,
  galleryConf: 0.50,
  galleryIou: 0.45,
  augment: false,
};

// State Color Mapping
const STATE_COLORS = {
  "Hazardous": "#ef4444",
  "Reusable / Salvageable": "#0ea5e9",
  "Useful / Active": "#10b981",
  "Inert Fragment": "#f59e0b",
};

// Debounce helper to prevent rapid HTTP request queuing
function debounce(fn, delay = 220) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// ============================================================================
// Lifecycle Initialization
// ============================================================================
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initViewToggles();
  initVideoControls();
  initGalleryControls();
  initTelemetryFilters();
  initExports();
  initFileUploads();
  initGallery();
  loadBenchmarks();

  // Auto-run video tracking on initial load for instant mission intelligence
  setTimeout(() => {
    runDemoVideo();
  }, 300);
});

// ============================================================================
// 1. Tab Navigation & Workspace Switching
// ============================================================================
function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      if (targetId) switchTab(targetId);
    });
  });

  // Shortcut button inside Video Control panel to navigate to Telemetry table
  const btnGoToTelemetry = document.getElementById("btnGoToTelemetry");
  if (btnGoToTelemetry) {
    btnGoToTelemetry.addEventListener("click", () => {
      switchTab("tabTelemetry");
    });
  }
}

function switchTab(tabId) {
  state.activeTab = tabId;

  document.querySelectorAll(".tab-btn").forEach((b) => {
    b.classList.toggle("active", b.getAttribute("data-tab") === tabId);
  });

  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("hidden", panel.id !== tabId);
  });

  // Resume video playback when returning to Video workspace
  if (tabId === "tabVideo") {
    const hudVideo = document.getElementById("hudVideo");
    if (hudVideo && hudVideo.style.display !== "none" && hudVideo.src) {
      hudVideo.play().catch(() => {});
    }
  }
}

// ============================================================================
// 2. Viewport Stream / Keyframe Toggles (Video HUD)
// ============================================================================
function initViewToggles() {
  const btnVideo = document.getElementById("btnViewVideo");
  const btnCanvas = document.getElementById("btnViewCanvas");
  const hudVideo = document.getElementById("hudVideo");
  const hudCanvas = document.getElementById("hudCanvas");

  if (btnVideo && btnCanvas) {
    btnVideo.addEventListener("click", () => {
      btnVideo.style.background = "rgba(56, 189, 248, 0.35)";
      btnVideo.style.borderColor = "var(--accent-cyan)";
      btnCanvas.style.background = "rgba(15, 23, 42, 0.6)";
      btnCanvas.style.borderColor = "var(--border-subtle)";

      if (hudVideo) {
        hudVideo.style.display = "block";
        hudVideo.play().catch(() => {});
      }
      if (hudCanvas) hudCanvas.style.display = "none";
    });

    btnCanvas.addEventListener("click", () => {
      btnCanvas.style.background = "rgba(56, 189, 248, 0.35)";
      btnCanvas.style.borderColor = "var(--accent-cyan)";
      btnVideo.style.background = "rgba(15, 23, 42, 0.6)";
      btnVideo.style.borderColor = "var(--border-subtle)";

      if (hudVideo) hudVideo.style.display = "none";
      if (hudCanvas) hudCanvas.style.display = "block";
    });
  }
}

// ============================================================================
// 3. Video Workspace Tactical Controls & Sliders
// ============================================================================
function initVideoControls() {
  const debouncedRerunVideo = debounce(() => {
    if (state.videoFile) {
      handleVideoFile(state.videoFile);
    } else {
      runDemoVideo();
    }
  }, 250);

  const confSlider = document.getElementById("confSlider");
  const confVal = document.getElementById("confVal");
  if (confSlider && confVal) {
    confSlider.addEventListener("input", (e) => {
      state.videoConf = parseFloat(e.target.value);
      confVal.textContent = `${Math.round(state.videoConf * 100)}%`;
      debouncedRerunVideo();
    });
  }

  const iouSlider = document.getElementById("iouSlider");
  const iouVal = document.getElementById("iouVal");
  if (iouSlider && iouVal) {
    iouSlider.addEventListener("input", (e) => {
      state.videoIou = parseFloat(e.target.value);
      iouVal.textContent = state.videoIou.toFixed(2);
      debouncedRerunVideo();
    });
  }

  const speedSlider = document.getElementById("speedSlider");
  const speedVal = document.getElementById("speedVal");
  if (speedSlider && speedVal) {
    speedSlider.addEventListener("input", (e) => {
      state.telemetrySpeed = parseFloat(e.target.value);
      speedVal.textContent = `${state.telemetrySpeed.toLocaleString()} m/s`;
      debouncedRerunVideo();
    });
  }

  const altSlider = document.getElementById("altSlider");
  const altVal = document.getElementById("altVal");
  if (altSlider && altVal) {
    altSlider.addEventListener("input", (e) => {
      state.telemetryAltitude = parseFloat(e.target.value);
      altVal.textContent = `${state.telemetryAltitude} km`;
      debouncedRerunVideo();
    });
  }

  const btnDemoVideo = document.getElementById("btnDemoVideo");
  if (btnDemoVideo) {
    btnDemoVideo.addEventListener("click", () => {
      state.videoFile = null;
      runDemoVideo();
    });
  }
}

// ============================================================================
// 4. Space Object Gallery Controls & Sliders
// ============================================================================
function initGalleryControls() {
  const debouncedRerunGallery = debounce(() => {
    if (state.activeImageData || state.uploadedImageFile) {
      runGalleryDetection();
    }
  }, 220);

  const galleryConfSlider = document.getElementById("galleryConfSlider");
  const galleryConfVal = document.getElementById("galleryConfVal");
  if (galleryConfSlider && galleryConfVal) {
    galleryConfSlider.addEventListener("input", (e) => {
      state.galleryConf = parseFloat(e.target.value);
      galleryConfVal.textContent = `${Math.round(state.galleryConf * 100)}%`;
      debouncedRerunGallery();
    });
  }

  const galleryIouSlider = document.getElementById("galleryIouSlider");
  const galleryIouVal = document.getElementById("galleryIouVal");
  if (galleryIouSlider && galleryIouVal) {
    galleryIouSlider.addEventListener("input", (e) => {
      state.galleryIou = parseFloat(e.target.value);
      galleryIouVal.textContent = state.galleryIou.toFixed(2);
      debouncedRerunGallery();
    });
  }

  const ttaToggle = document.getElementById("ttaToggle");
  if (ttaToggle) {
    ttaToggle.addEventListener("change", (e) => {
      state.augment = e.target.checked;
      debouncedRerunGallery();
    });
  }
}

// ============================================================================
// 5. Pre-Loaded Space Object Gallery Loader
// ============================================================================
async function initGallery() {
  const container = document.getElementById("galleryStrip");
  if (!container) return;

  try {
    const res = await fetch("/api/samples");
    const data = await res.json();
    const samples = data.samples || [];

    container.innerHTML = "";
    samples.forEach((s) => {
      const card = document.createElement("div");
      card.className = "gallery-card";
      card.innerHTML = `
        <img class="gallery-thumb" src="/api/samples/${s.filename}" alt="${s.label}">
        <div class="gallery-name" title="${s.label}">${s.label}</div>
        <div class="gallery-class">${s.class_name}</div>
      `;
      card.addEventListener("click", () => {
        document.querySelectorAll(".gallery-card").forEach((c) => c.classList.remove("active"));
        card.classList.add("active");
        loadSample(s);
      });
      container.appendChild(card);
    });

    if (samples.length > 0) {
      container.children[0]?.classList.add("active");
      loadSample(samples[0], false); // Preload image data without stealing active focus
    }
  } catch (err) {
    console.error("Failed to load sample gallery catalog:", err);
  }
}

async function loadSample(sample, autoSwitch = true) {
  state.uploadedImageFile = null;
  state.activeSample = sample;

  const statusEl = document.getElementById("galleryStatus");
  if (statusEl) statusEl.textContent = `Source: Sample Catalog (${sample.label})`;

  const infoEl = document.getElementById("galleryTargetInfo");
  if (infoEl) infoEl.textContent = sample.label;

  const imgUrl = `/api/samples/${sample.filename}`;
  const img = new Image();
  img.crossOrigin = "anonymous";
  img.onload = () => {
    state.activeImageData = img;
    runGalleryDetection();
  };
  img.src = imgUrl;

  if (autoSwitch && state.activeTab !== "tabGallery") {
    switchTab("tabGallery");
  }
}

// ============================================================================
// 6. File Uploads (Videos & Images) & Drag-and-Drop
// ============================================================================
function initFileUploads() {
  // Video Upload
  const btnUploadVideo = document.getElementById("btnUploadVideo");
  const videoInput = document.getElementById("videoInput");
  const videoStage = document.getElementById("viewportStage");

  if (btnUploadVideo && videoInput) {
    btnUploadVideo.addEventListener("click", () => videoInput.click());
    videoInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleVideoFile(e.target.files[0]);
        videoInput.value = "";
      }
    });
  }

  // Image Upload (in Gallery Tab)
  const btnUploadImage = document.getElementById("btnUploadImage");
  const imageInput = document.getElementById("imageInput");
  if (btnUploadImage && imageInput) {
    btnUploadImage.addEventListener("click", () => imageInput.click());
    imageInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleImageFile(e.target.files[0]);
        imageInput.value = "";
      }
    });
  }

  // Video Drag-and-Drop
  if (videoStage) {
    videoStage.addEventListener("dragover", (e) => {
      e.preventDefault();
      videoStage.style.borderColor = "var(--accent-cyan)";
      videoStage.style.boxShadow = "0 0 24px rgba(56, 189, 248, 0.4)";
    });

    videoStage.addEventListener("dragleave", (e) => {
      e.preventDefault();
      videoStage.style.borderColor = "var(--border-subtle)";
      videoStage.style.boxShadow = "none";
    });

    videoStage.addEventListener("drop", (e) => {
      e.preventDefault();
      videoStage.style.borderColor = "var(--border-subtle)";
      videoStage.style.boxShadow = "none";
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        const file = e.dataTransfer.files[0];
        if (file.type.startsWith("video/") || /\.(mp4|webm|avi|mov|mkv)$/i.test(file.name)) {
          handleVideoFile(file);
        } else {
          handleImageFile(file);
        }
      }
    });
  }
}

// ============================================================================
// 7. Video Kinematics Engine (1-Click Sample & Upload)
// ============================================================================
async function runDemoVideo() {
  state.isVideoMode = true;
  state.videoFile = null;

  const statusEl = document.getElementById("viewportStatus");
  if (statusEl) statusEl.textContent = "Source: Orbital Encounter (sample_encounter.mp4)";

  showVideoSpinner("PROCESSING ORBITAL FRAMES & COMPUTING TUMBLE (BoT-SORT)...");

  try {
    const formData = new FormData();
    formData.append("conf_threshold", state.videoConf);
    formData.append("iou_threshold", state.videoIou);
    formData.append("speed_mps", state.telemetrySpeed);
    formData.append("altitude_km", state.telemetryAltitude);
    formData.append("max_frames", 150);

    const res = await fetch("/api/run-sample-video", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Video processing HTTP ${res.status}`);
    const data = await res.json();
    processVideoResults(data, "sample_encounter.mp4");
  } catch (err) {
    console.error("Demo video error:", err);
    alert("Video tracking failed: " + err.message);
  } finally {
    hideVideoSpinner();
  }
}

async function handleVideoFile(file) {
  if (!file) return;
  state.isVideoMode = true;
  state.videoFile = file;

  const statusEl = document.getElementById("viewportStatus");
  if (statusEl) statusEl.textContent = `Source: Orbital Video (${file.name})`;

  showVideoSpinner("PROCESSING FRAMES & COMPUTING TUMBLE RATES...");

  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("conf_threshold", state.videoConf);
    formData.append("iou_threshold", state.videoIou);
    formData.append("speed_mps", state.telemetrySpeed);
    formData.append("altitude_km", state.telemetryAltitude);
    formData.append("max_frames", 150);

    const res = await fetch("/api/upload-video", {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error(`Video processing error: ${res.status}`);
    const data = await res.json();
    processVideoResults(data, file.name);
  } catch (err) {
    console.error("Video upload processing error:", err);
    alert("Video processing failed: " + err.message);
  } finally {
    hideVideoSpinner();
  }
}

function processVideoResults(data, filename) {
  state.videoTracks = data.tracks || [];
  state.videoSummary = data.summary || {};

  // Direct active telemetry stream to the global logger
  state.currentTelemetry = state.videoTracks;
  state.currentSummary = state.videoSummary;

  const hudVideo = document.getElementById("hudVideo");
  const hudCanvas = document.getElementById("hudCanvas");

  // Draw representative keyframe on Canvas as guaranteed fallback
  if (data.representative_frame_base64 && hudCanvas) {
    const repImg = new Image();
    repImg.onload = () => {
      hudCanvas.width = repImg.naturalWidth || repImg.width || 640;
      hudCanvas.height = repImg.naturalHeight || repImg.height || 640;
      const ctx = hudCanvas.getContext("2d");
      ctx.drawImage(repImg, 0, 0, hudCanvas.width, hudCanvas.height);
    };
    repImg.src = data.representative_frame_base64;
  }

  // Stream annotated video in HTML5 video player
  if (data.annotated_video_url && hudVideo) {
    hudVideo.pause();
    hudVideo.muted = true;
    hudVideo.playsInline = true;
    hudVideo.autoplay = true;
    hudVideo.loop = true;
    hudVideo.controls = true;

    // Cache-busting timestamp ensures freshly generated stream is fetched
    hudVideo.src = `${data.annotated_video_url}?t=${Date.now()}`;
    hudVideo.style.display = "block";
    if (hudCanvas) hudCanvas.style.display = "none";

    hudVideo.oncanplay = () => {
      hudVideo.play().catch((e) => console.warn("Autoplay notice:", e));
    };

    hudVideo.onerror = (e) => {
      console.warn("Video playback error, displaying Keyframe HUD instead", e);
      hudVideo.style.display = "none";
      if (hudCanvas) hudCanvas.style.display = "block";
    };
  } else {
    if (hudVideo) hudVideo.style.display = "none";
    if (hudCanvas) hudCanvas.style.display = "block";
  }

  // Show toggle bar
  const toggleBar = document.getElementById("viewportToggleBar");
  if (toggleBar) toggleBar.style.display = "flex";

  // Update Reticle Status
  const reticle = document.getElementById("reticleText");
  if (reticle) {
    reticle.textContent = `TRACKED ${data.processed_frames}/${data.total_frames} FRAMES // DURATION: ${data.duration_sec}s // FPS: ${data.fps} // ${state.videoTracks.length} TARGETS`;
  }

  // Update Insights, Top KPIs & Telemetry Table
  updateInsightsBanner(state.videoSummary, state.videoTracks);
  updateDashboardKPIs(state.videoSummary);
  updateTelemetryTable();
}

// ============================================================================
// 8. Space Object Gallery & Single-Frame Detection
// ============================================================================
async function handleImageFile(file) {
  if (!file) return;
  state.uploadedImageFile = file;
  state.activeSample = { label: file.name, class_name: "custom_image" };

  const statusEl = document.getElementById("galleryStatus");
  if (statusEl) statusEl.textContent = `Source: Uploaded Photo (${file.name})`;

  const infoEl = document.getElementById("galleryTargetInfo");
  if (infoEl) infoEl.textContent = file.name;

  document.querySelectorAll(".gallery-card").forEach((c) => c.classList.remove("active"));

  const reader = new FileReader();
  reader.onload = (e) => {
    const img = new Image();
    img.onload = () => {
      state.activeImageData = img;
      runGalleryDetection();
      switchTab("tabGallery");
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function runGalleryDetection() {
  if (!state.activeImageData) return;

  const canvas = document.getElementById("galleryCanvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  canvas.width = state.activeImageData.naturalWidth || state.activeImageData.width || 640;
  canvas.height = state.activeImageData.naturalHeight || state.activeImageData.height || 640;
  ctx.drawImage(state.activeImageData, 0, 0, canvas.width, canvas.height);

  showGallerySpinner("EVALUATING DEEP TRANSFER LEARNING MODEL...");

  try {
    let data;
    if (state.uploadedImageFile) {
      const formData = new FormData();
      formData.append("file", state.uploadedImageFile);
      formData.append("conf_threshold", state.galleryConf);
      formData.append("iou_threshold", state.galleryIou);
      formData.append("speed_mps", state.telemetrySpeed);
      formData.append("altitude_km", state.telemetryAltitude);
      formData.append("augment", state.augment ? "true" : "false");

      const res = await fetch("/api/upload", { method: "POST", body: formData });
      if (!res.ok) throw new Error(`Upload error: ${res.status}`);
      data = await res.json();
    } else if (state.activeSample && state.activeSample.filename) {
      const payload = {
        sample_filename: state.activeSample.filename,
        conf_threshold: state.galleryConf,
        iou_threshold: state.galleryIou,
        speed_mps: state.telemetrySpeed,
        altitude_km: state.telemetryAltitude,
        augment: state.augment || false,
      };
      const res = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Detection error: ${res.status}`);
      data = await res.json();
    } else {
      const payload = {
        image_base64: canvas.toDataURL("image/jpeg", 0.95),
        conf_threshold: state.galleryConf,
        iou_threshold: state.galleryIou,
        speed_mps: state.telemetrySpeed,
        altitude_km: state.telemetryAltitude,
        augment: state.augment || false,
      };
      const res = await fetch("/api/detect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`Detection error: ${res.status}`);
      data = await res.json();
    }

    state.imageDetections = data.detections || [];
    state.imageSummary = data.summary || {};

    // Push into active telemetry pipeline
    state.currentTelemetry = state.imageDetections;
    state.currentSummary = state.imageSummary;

    // Re-draw base image and render bounding boxes
    ctx.drawImage(state.activeImageData, 0, 0, canvas.width, canvas.height);
    renderBoundingBoxes(ctx, state.imageDetections);

    // Update Gallery Reticle
    const reticle = document.getElementById("galleryReticle");
    if (reticle) {
      reticle.textContent = `OPTICAL ACQUISITION: ${state.imageDetections.length} TARGETS IDENTIFIED // FOV ${canvas.width}×${canvas.height}`;
    }

    // Update Target State Card
    const targetStateEl = document.getElementById("galleryTargetState");
    if (targetStateEl) {
      if (state.imageDetections.length > 0) {
        const top = state.imageDetections[0];
        targetStateEl.innerHTML = `${getStateBadgeHtml(top.operational_state)} <span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-left:6px;">Conf: ${Math.round(top.confidence * 100)}%</span>`;
      } else {
        targetStateEl.innerHTML = `<span class="badge-pill" style="color:var(--text-muted);">BELOW CUTOFF</span>`;
      }
    }

    // Update Top KPIs and Telemetry Table
    updateDashboardKPIs(state.imageSummary);
    updateTelemetryTable();
  } catch (err) {
    console.error("Gallery inference failed:", err);
  } finally {
    hideGallerySpinner();
  }
}

// ============================================================================
// 9. Canvas HUD Bounding Box Overlay Renderer
// ============================================================================
function renderBoundingBoxes(ctx, detections) {
  if (!detections || detections.length === 0) return;

  detections.forEach((det) => {
    const [x1, y1, x2, y2] = det.bbox;
    const w = x2 - x1;
    const h = y2 - y1;
    const color = STATE_COLORS[det.operational_state] || "#38bdf8";

    // Bounding Box
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.strokeRect(x1, y1, w, h);

    // Aerospace Reticle Brackets
    const corner = Math.min(18, Math.max(8, w * 0.15));
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x1, y1 + corner); ctx.lineTo(x1, y1); ctx.lineTo(x1 + corner, y1);
    ctx.moveTo(x2 - corner, y1); ctx.lineTo(x2, y1); ctx.lineTo(x2, y1 + corner);
    ctx.moveTo(x1, y2 - corner); ctx.lineTo(x1, y2); ctx.lineTo(x1 + corner, y2);
    ctx.moveTo(x2 - corner, y2); ctx.lineTo(x2, y2); ctx.lineTo(x2, y2 - corner);
    ctx.stroke();

    // Telemetry Callout Pill
    const confPct = Math.round(det.confidence * 100);
    const label = `${det.display_name} | ${det.operational_state.toUpperCase()}`;
    const subLabel = `Conf: ${confPct}% | Risk: ${det.risk_score.toFixed(2)}`;

    ctx.font = "bold 12px 'Plus Jakarta Sans', sans-serif";
    const tw1 = ctx.measureText(label).width;
    ctx.font = "10px 'JetBrains Mono', monospace";
    const tw2 = ctx.measureText(subLabel).width;
    const bannerW = Math.max(tw1, tw2) + 16;
    const bannerH = 36;
    const bannerY = Math.max(0, y1 - bannerH);

    ctx.fillStyle = "rgba(6, 9, 19, 0.90)";
    ctx.fillRect(x1, bannerY, bannerW, bannerH);
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.strokeRect(x1, bannerY, bannerW, bannerH);

    ctx.fillStyle = color;
    ctx.font = "bold 12px 'Plus Jakarta Sans', sans-serif";
    ctx.fillText(label, x1 + 8, bannerY + 15);

    ctx.fillStyle = "#cbd5e1";
    ctx.font = "10px 'JetBrains Mono', monospace";
    ctx.fillText(subLabel, x1 + 8, bannerY + 29);
  });
}

// ============================================================================
// 10. Dashboard KPIs & Radial Gauge
// ============================================================================
function updateDashboardKPIs(summary) {
  if (!summary) return;

  const totalEl = document.getElementById("kpiTotal");
  const hazEl = document.getElementById("kpiHazardous");
  const reusEl = document.getElementById("kpiReusable");
  const actEl = document.getElementById("kpiActive");
  const riskEl = document.getElementById("kpiRisk");

  if (totalEl) totalEl.textContent = summary.total_objects || 0;
  if (hazEl) hazEl.textContent = summary.hazardous_count || 0;
  if (reusEl) reusEl.textContent = summary.reusable_count || 0;
  if (actEl) actEl.textContent = summary.active_count || 0;

  const meanRisk = summary.mean_risk || 0.0;
  if (riskEl) riskEl.textContent = meanRisk.toFixed(2);

  updateRadialGauge(summary.max_risk || 0.0);
}

function updateRadialGauge(score) {
  const circle = document.getElementById("gaugeFill");
  const text = document.getElementById("gaugeVal");
  if (!circle || !text) return;

  const pct = Math.round(score * 100);
  text.textContent = `${pct}%`;

  const radius = 65;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (pct / 100) * circumference;

  circle.style.strokeDasharray = `${circumference} ${circumference}`;
  circle.style.strokeDashoffset = offset;

  if (score > 0.60) {
    circle.style.stroke = "var(--state-hazardous)";
  } else if (score < 0.40) {
    circle.style.stroke = "var(--state-active)";
  } else {
    circle.style.stroke = "var(--state-fragment)";
  }
}

// ============================================================================
// 11. Real-Time Insights Banner (in Video Workspace)
// ============================================================================
function updateInsightsBanner(summary, targets) {
  const banner = document.getElementById("insightsBanner");
  if (!banner) return;

  banner.style.display = "block";
  const badge = document.getElementById("insightThreatBadge");
  const title = document.getElementById("insightThreatTitle");
  const metrics = document.getElementById("insightMetrics");
  const decision = document.getElementById("insightDecision");

  if (!targets || targets.length === 0) {
    if (badge) {
      badge.className = "badge-pill badge-active";
      badge.textContent = "CLEAR";
    }
    if (title) title.textContent = "Sensor Sweep Nominal — No Active Threats in FOV";
    if (metrics) metrics.textContent = `Cutoff: ${Math.round(state.videoConf * 100)}% | Speed: ${state.telemetrySpeed} m/s | Alt: ${state.telemetryAltitude} km`;
    if (decision) {
      decision.style.color = "var(--state-active)";
      decision.textContent = "🟢 NOMINAL TRAJECTORY: Clear Orbital Corridor";
    }
    return;
  }

  // Find target with highest collision risk score
  const topTarget = targets.reduce((max, t) => (t.risk_score > (max?.risk_score || 0) ? t : max), targets[0]);
  const maxRisk = topTarget?.risk_score || summary?.max_risk || 0.0;
  const isHazardous = topTarget?.operational_state === "Hazardous" || maxRisk >= 0.60;
  const tumbleVal = topTarget?.tumble_rate !== undefined ? Number(topTarget.tumble_rate).toFixed(4) : "0.0000";

  if (badge) {
    badge.className = `badge-pill ${isHazardous ? 'badge-hazardous' : 'badge-reusable'}`;
    badge.textContent = isHazardous ? "CRITICAL HAZARD" : topTarget.operational_state.toUpperCase();
  }

  if (title) {
    const tid = topTarget.track_id !== undefined && topTarget.track_id !== -1 ? `#${topTarget.track_id}` : "#1";
    title.textContent = `${topTarget.display_name} (${tid}) — ${topTarget.operational_state}`;
  }

  if (metrics) {
    metrics.textContent = `Tumble: ${tumbleVal} σ² | Velocity: ${state.telemetrySpeed.toLocaleString()} m/s | Collision Risk: ${Math.round(maxRisk * 100)}%`;
  }

  if (decision) {
    if (isHazardous) {
      decision.style.color = "#f87171";
      decision.textContent = "⚠️ CAM TRIGGER: Collision Avoidance Maneuver Recommended (NASA-STD-8719.14C)";
    } else if (topTarget.operational_state === "Useful / Active") {
      decision.style.color = "var(--state-active)";
      decision.textContent = "🟢 ACTIVE SATELLITE: Operational Asset — Safety Corridor Protected";
    } else {
      decision.style.color = "var(--state-reusable)";
      decision.textContent = "🔵 SALVAGEABLE BUS: Potential On-Orbit Servicing Candidate";
    }
  }
}

// ============================================================================
// 12. Dedicated Telemetry Table & State Filtering
// ============================================================================
function initTelemetryFilters() {
  const group = document.getElementById("telemetryFilterGroup");
  if (!group) return;

  const buttons = group.querySelectorAll(".filter-btn");
  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      buttons.forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      state.tableFilter = btn.getAttribute("data-filter") || "all";
      updateTelemetryTable();
    });
  });
}

function updateTelemetryTable() {
  const tableBody = document.getElementById("telemetryTableBody");
  const countBadge = document.getElementById("tableCountBadge");
  if (!tableBody) return;

  const list = state.currentTelemetry || [];
  const filtered = state.tableFilter === "all" 
    ? list 
    : list.filter((t) => t.operational_state === state.tableFilter);

  if (countBadge) {
    countBadge.textContent = `${filtered.length} OF ${list.length} TARGETS DISPLAYED`;
  }

  tableBody.innerHTML = "";

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="9" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">
          ${list.length === 0 
            ? "No active targets detected. Run <strong>Orbital Video Tracking</strong> or select a <strong>Space Object Sample</strong>." 
            : "No targets match the active filter criteria."}
        </td>
      </tr>
    `;
    return;
  }

  filtered.forEach((t, i) => {
    const tr = document.createElement("tr");
    const stateBadge = getStateBadgeHtml(t.operational_state);
    const trackIdDisplay = t.track_id !== undefined && t.track_id !== -1 ? `#${t.track_id}` : `#${i + 1}`;
    const tumbleDisplay = t.tumble_rate !== undefined && t.tumble_rate > 0 
      ? `<code>${t.tumble_rate.toFixed(4)}</code>` 
      : `<span style="color:var(--text-muted);">Static (0.0)</span>`;
    const bboxDisplay = t.bbox ? `[${t.bbox.map((c) => Math.round(c)).join(", ")}]` : `N/A`;

    tr.innerHTML = `
      <td><strong>${trackIdDisplay}</strong></td>
      <td><strong>${t.display_name}</strong></td>
      <td><code>${t.class_name}</code></td>
      <td><strong>${Math.round(t.confidence * 100)}%</strong></td>
      <td><span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">${bboxDisplay}</span></td>
      <td>${(t.area_ratio * 100).toFixed(2)}%</td>
      <td>${tumbleDisplay}</td>
      <td><strong style="color:${t.risk_score > 0.6 ? 'var(--state-hazardous)' : 'var(--text-main)'};">${t.risk_score.toFixed(3)}</strong></td>
      <td>${stateBadge}</td>
    `;
    tableBody.appendChild(tr);
  });
}

function getStateBadgeHtml(state) {
  switch (state) {
    case "Hazardous":
      return `<span class="badge-pill badge-hazardous">HAZARDOUS</span>`;
    case "Reusable / Salvageable":
      return `<span class="badge-pill badge-reusable">REUSABLE</span>`;
    case "Useful / Active":
      return `<span class="badge-pill badge-active">ACTIVE SAT</span>`;
    default:
      return `<span class="badge-pill badge-fragment">FRAGMENT</span>`;
  }
}

// ============================================================================
// 13. Telemetry Data Exports (CSV & JSON)
// ============================================================================
function initExports() {
  const btnCsv = document.getElementById("btnExportCsv");
  if (btnCsv) btnCsv.addEventListener("click", exportCsv);

  const btnJson = document.getElementById("btnExportJson");
  if (btnJson) btnJson.addEventListener("click", exportJson);
}

function exportCsv() {
  const list = state.currentTelemetry || [];
  if (list.length === 0) {
    alert("No active detections to export.");
    return;
  }

  const headers = ["Index,TrackID,Target,Class,OperationalState,Confidence,AreaRatio,TumbleRate,RiskScore"];
  const rows = list.map((d, i) => {
    const tid = d.track_id !== undefined && d.track_id !== -1 ? d.track_id : (i + 1);
    const name = (d.display_name || "Unknown").replace(/"/g, '""');
    const cname = (d.class_name || "unknown").replace(/"/g, '""');
    const stateName = (d.operational_state || "Unknown").replace(/"/g, '""');
    const conf = d.confidence !== undefined ? (d.confidence * 100).toFixed(1) : "0.0";
    const area = d.area_ratio !== undefined ? (d.area_ratio * 100).toFixed(2) : "0.00";
    const tumble = d.tumble_rate !== undefined ? Number(d.tumble_rate).toFixed(4) : "0.0000";
    const risk = d.risk_score !== undefined ? Number(d.risk_score).toFixed(3) : "0.000";
    return `${i + 1},${tid},"${name}","${cname}","${stateName}",${conf}%,${area}%,${tumble},${risk}`;
  });

  const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
  const link = document.createElement("a");
  link.setAttribute("href", encodeURI(csvContent));
  link.setAttribute("download", `spaci_mission_telemetry_${Date.now()}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportJson() {
  const list = state.currentTelemetry || [];
  if (list.length === 0) {
    alert("No active detections to export.");
    return;
  }

  const payload = {
    timestamp: new Date().toISOString(),
    media_mode: state.isVideoMode ? "video_kinematics" : "single_frame_image",
    summary: state.currentSummary,
    telemetry: list,
  };

  const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(payload, null, 2));
  const link = document.createElement("a");
  link.setAttribute("href", jsonStr);
  link.setAttribute("download", `spaci_mission_payload_${Date.now()}.json`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ============================================================================
// 14. Spinners & Utilities
// ============================================================================
function showVideoSpinner(msg = "PROCESSING ORBITAL TELEMETRY...") {
  const sp = document.getElementById("hudSpinner");
  const txt = document.getElementById("spinnerText");
  if (sp) sp.style.display = "flex";
  if (txt) txt.textContent = msg;
}

function hideVideoSpinner() {
  const sp = document.getElementById("hudSpinner");
  if (sp) sp.style.display = "none";
}

function showGallerySpinner(msg = "ANALYZING TARGET...") {
  const sp = document.getElementById("gallerySpinner");
  const txt = document.getElementById("gallerySpinnerText");
  if (sp) sp.style.display = "flex";
  if (txt) txt.textContent = msg;
}

function hideGallerySpinner() {
  const sp = document.getElementById("gallerySpinner");
  if (sp) sp.style.display = "none";
}

async function loadBenchmarks() {
  try {
    const res = await fetch("/api/benchmarks");
    const data = await res.json();
    const std = data.test_standard?.overall;
    if (std) {
      const pEl = document.getElementById("benchPrecision");
      if (pEl) pEl.textContent = `${(std.precision * 100).toFixed(2)}%`;
    }
  } catch (err) {
    console.error("Could not load dynamic benchmarks:", err);
  }
}
