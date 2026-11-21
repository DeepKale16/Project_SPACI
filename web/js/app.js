/**
 * SPACI 3.0 - Aerospace Mission Control & Closed-Form Ballistic GNC HUD
 * Pure Vanilla JavaScript: Atomic WebSocket (/ws/live), Ray-Cast LiDAR, Tactical Radar, Dual-Mode Engine
 */

// ============================================================================
// State Management
// ============================================================================
const state = {
  // Navigation & Mission Mode
  activeTab: "tabLive",
  missionMode: "GROUND_DEMONSTRATOR", // 'ORBITAL_SURVEILLANCE' or 'GROUND_DEMONSTRATOR'

  // Live Engine & WebSocket
  ws: null,
  liveSource: "TESTBENCH",
  vNet: 9.0,
  tLat: 0.08,
  dNet: 1.2,
  magneticAssist: false,
  autoFire: false,
  lastGncCommand: null,

  // Global Telemetry Data (Displayed in Table & Exported)
  currentTelemetry: [],
  currentSummary: null,
  tableFilter: "all",

  // Video Mode State
  isVideoMode: false,
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
  tiledInspection: false,
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
  initModeSwitcher();
  initLiveWebSocket();
  initLiveControls();
  initViewToggles();
  initVideoControls();
  initGalleryControls();
  initTelemetryFilters();
  initExports();
  initFileUploads();
  initGallery();
  loadBenchmarks();
  updateKpiSummary();
});

// ============================================================================
// 1. Mission Mode Switcher & Tab Navigation
// ============================================================================
function initModeSwitcher() {
  const btnOrbital = document.getElementById("btnModeOrbital");
  const btnGround = document.getElementById("btnModeGround");

  const setMode = async (mode) => {
    state.missionMode = mode;
    btnOrbital.classList.toggle("active", mode === "ORBITAL_SURVEILLANCE");
    btnGround.classList.toggle("active", mode === "GROUND_DEMONSTRATOR");

    try {
      await fetch("/api/mode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode }),
      });
    } catch (e) {
      console.warn("Mode sync notice:", e);
    }

    // Adapt top KPI labels based on mode
    updateTopKpiLabels();
  };

  if (btnOrbital) btnOrbital.addEventListener("click", () => setMode("ORBITAL_SURVEILLANCE"));
  if (btnGround) btnGround.addEventListener("click", () => setMode("GROUND_DEMONSTRATOR"));
}

function updateTopKpiLabels() {
  const isGround = state.missionMode === "GROUND_DEMONSTRATOR";
  const c1 = document.querySelector("#kpiCardTotal .kpi-label");
  const c2 = document.querySelector("#kpiCardHazardous .kpi-label");
  const c3 = document.querySelector("#kpiCardReusable .kpi-label");
  const c4 = document.querySelector("#kpiCardActive .kpi-label");
  const c5 = document.querySelector("#kpiCardRisk .kpi-label");

  if (isGround) {
    if (c1) c1.textContent = "Tracked Targets";
    if (c2) c2.textContent = "GNC Gate Status";
    if (c3) c3.textContent = "Deployment Distance";
    if (c4) c4.textContent = "Capture Success Rate";
    if (c5) c5.textContent = "3D Miss Error";
  } else {
    if (c1) c1.textContent = "Field of View Targets";
    if (c2) c2.textContent = "Hazardous Threat";
    if (c3) c3.textContent = "Reusable / Salvage";
    if (c4) c4.textContent = "Useful / Active";
    if (c5) c5.textContent = "Mean Risk Index";
  }
}

function initTabs() {
  const tabBtns = document.querySelectorAll(".tab-btn");

  tabBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");
      if (targetId) switchTab(targetId);
    });
  });

  const btnGoToTelemetry = document.getElementById("btnGoToTelemetry");
  if (btnGoToTelemetry) {
    btnGoToTelemetry.addEventListener("click", () => switchTab("tabTelemetry"));
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

  if (tabId === "tabVideo") {
    const hudVideo = document.getElementById("hudVideo");
    if (hudVideo && hudVideo.style.display !== "none" && hudVideo.src) {
      hudVideo.play().catch(() => {});
    }
  }
}

// ============================================================================
// 2. Real-Time Atomic WebSocket Engine (/ws/live) & Tactical Radar
// ============================================================================
function initLiveWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws/live`;

  function connect() {
    state.ws = new WebSocket(wsUrl);

    state.ws.onopen = () => {
      console.log("[SPACI 3.0] WebSocket Live Stream connected.");
      const reticle = document.getElementById("liveReticleText");
      if (reticle) reticle.textContent = "LIVE ATOMIC WS // FOV: 640×640 // LOCK: ACTIVE";
    };

    state.ws.onmessage = (event) => {
      try {
        const packet = JSON.parse(event.data);
        handleLivePacket(packet);
      } catch (err) {
        console.warn("WebSocket parse error:", err);
      }
    };

    state.ws.onclose = () => {
      console.warn("[SPACI 3.0] WebSocket disconnected. Reconnecting in 1.5s...");
      setTimeout(connect, 1500);
    };

    state.ws.onerror = (err) => {
      console.error("[SPACI 3.0] WebSocket error:", err);
    };
  }

  connect();
}

function handleLivePacket(packet) {
  // 1. Update Video Frame
  const streamImg = document.getElementById("liveStreamImg");
  if (streamImg && packet.frame_b64) {
    streamImg.src = packet.frame_b64;
  }

  // 2. Update Performance Badges
  const fpsPill = document.getElementById("liveFpsPill");
  if (fpsPill) {
    fpsPill.textContent = `LIVE: ${packet.fps} FPS // ${packet.latency_ms} ms`;
  }

  const depthBadge = document.getElementById("liveDepthBadge");
  if (depthBadge) {
    depthBadge.textContent = `${packet.depth_source} (3D FUSION)`;
  }

  // 3. Update GNC Verdict Banner
  const gnc = packet.gnc_command;
  state.lastGncCommand = gnc;

  const stateBadge = document.getElementById("gncStateBadge");
  const lockText = document.getElementById("gncTargetLockText");
  const anglesText = document.getElementById("gncAnglesText");
  const directive = document.getElementById("gncActionDirective");

  if (gnc) {
    const isReady = gnc.state === "FIRE_READY";
    const isAbort = gnc.state.startsWith("ABORT");

    if (stateBadge) {
      stateBadge.className = `badge-pill ${isReady ? 'badge-ready' : (isAbort ? 'badge-abort' : 'badge-reusable')}`;
      stateBadge.textContent = gnc.state;
    }

    if (lockText) {
      const lockedTid = packet.locked_track_id || gnc.track_id;
      const targetObj = packet.tracks?.find(t => t.track_id === lockedTid);
      const cname = targetObj?.class_name || "debris";
      const zInt = gnc.intercept_pos ? gnc.intercept_pos[2].toFixed(2) : "N/A";
      lockText.textContent = `Target #${lockedTid} (${cname}) — Intercept Range: ${zInt}m`;
    }

    if (anglesText) {
      anglesText.textContent = `Pan: ${gnc.pan_deg > 0 ? '+' : ''}${gnc.pan_deg}° | Tilt: ${gnc.tilt_deg > 0 ? '+' : ''}${gnc.tilt_deg}° | Flight: ${gnc.t_flight_s}s | Aperture: ${gnc.net_open_pct}%`;
    }

    if (directive) {
      if (isReady) {
        directive.style.color = "#34d399";
        directive.textContent = "🟢 READY: All 6 Go/No-Go Safety Conditions Cleared";
      } else if (isAbort) {
        directive.style.color = "#f87171";
        directive.textContent = `⚠️ ${gnc.state}: ${gnc.abort_reason || gnc.status_message}`;
      } else {
        directive.style.color = "var(--accent-cyan)";
        directive.textContent = `🔵 ${gnc.status_message}`;
      }
    }
  }

  // 4. Update Hardware Bus Monitor
  const hwMon = document.getElementById("hwMonitorJson");
  if (hwMon && gnc) {
    hwMon.textContent = JSON.stringify(gnc, null, 2);
  }

  // 5. Draw Tactical Trajectory Radar
  if (packet.radar_state) {
    renderTacticalRadar(packet.radar_state);
  }

  // 6. Update Top KPIs if in Ground Mode
  if (state.missionMode === "GROUND_DEMONSTRATOR") {
    const tCount = packet.tracks?.length || 0;
    const k1 = document.getElementById("kpiTotal");
    const k2 = document.getElementById("kpiHazardous");
    const k3 = document.getElementById("kpiReusable");

    if (k1) k1.textContent = tCount;
    if (k2) {
      k2.textContent = gnc ? gnc.state : "SEARCHING";
      k2.style.color = gnc?.state === "FIRE_READY" ? "var(--state-active)" : (gnc?.state?.startsWith("ABORT") ? "var(--state-hazardous)" : "var(--accent-cyan)");
    }
    if (k3) {
      const zVal = gnc?.intercept_pos ? `${gnc.intercept_pos[2].toFixed(2)} m` : "—";
      k3.textContent = zVal;
      k3.style.color = "var(--accent-cyan)";
    }
  }
}

// ============================================================================
// 3. Tactical Trajectory Radar Renderer (HTML5 Canvas)
// ============================================================================
function renderTacticalRadar(radarState) {
  const canvasXz = document.getElementById("radarXz");
  const canvasYz = document.getElementById("radarYz");
  if (!canvasXz || !canvasYz) return;

  const ctxXz = canvasXz.getContext("2d");
  const ctxYz = canvasYz.getContext("2d");

  const w = canvasXz.width;
  const h = canvasXz.height;

  // Scale: 7.0 meters max depth -> canvas height
  const maxRange = 7.0;
  const scaleZ = (h - 25) / maxRange;

  // --- Top-Down Radar (X - Z Plane) ---
  ctxXz.clearRect(0, 0, w, h);
  const cx = w / 2;
  const originZ = h - 15;

  // Draw Range Rings (2m, 4m, 6m)
  ctxXz.strokeStyle = "rgba(56, 189, 248, 0.18)";
  ctxXz.lineWidth = 1;
  ctxXz.fillStyle = "rgba(100, 116, 139, 0.6)";
  ctxXz.font = "9px 'JetBrains Mono', monospace";

  [2.0, 4.0, 6.0].forEach(r => {
    const rPx = r * scaleZ;
    ctxXz.beginPath();
    ctxXz.arc(cx, originZ, rPx, Math.PI, 2 * Math.PI);
    ctxXz.stroke();
    ctxXz.fillText(`${r}m`, cx + 4, originZ - rPx + 10);
  });

  // Launcher FOV Wedge (+-30 deg)
  const angleRad = (30.0 * Math.PI) / 180.0;
  const edgeLen = 6.8 * scaleZ;
  ctxXz.strokeStyle = "rgba(14, 165, 233, 0.35)";
  ctxXz.beginPath();
  ctxXz.moveTo(cx, originZ);
  ctxXz.lineTo(cx - edgeLen * Math.sin(angleRad), originZ - edgeLen * Math.cos(angleRad));
  ctxXz.moveTo(cx, originZ);
  ctxXz.lineTo(cx + edgeLen * Math.sin(angleRad), originZ - edgeLen * Math.cos(angleRad));
  ctxXz.stroke();

  // Launcher Origin
  ctxXz.fillStyle = "#38bdf8";
  ctxXz.beginPath();
  ctxXz.arc(cx, originZ, 4, 0, 2 * Math.PI);
  ctxXz.fill();

  // Plot Radar Targets (X - Z)
  (radarState.targets || []).forEach(t => {
    const px = cx + (t.x_m * scaleZ);
    const pz = originZ - (t.z_m * scaleZ);

    ctxXz.fillStyle = t.class_name === "debris" ? "#ef4444" : "#10b981";
    ctxXz.beginPath();
    ctxXz.arc(px, pz, 5, 0, 2 * Math.PI);
    ctxXz.fill();

    ctxXz.fillStyle = "#e2e8f0";
    ctxXz.fillText(`#${t.track_id} ${t.class_name.slice(0, 6)}`, px + 7, pz + 3);
  });

  // Plot Parabolic Net Arc (Top-Down projection)
  const arc = radarState.net_arc_3d || [];
  if (arc.length > 1) {
    ctxXz.strokeStyle = "rgba(52, 211, 153, 0.9)";
    ctxXz.lineWidth = 2;
    ctxXz.beginPath();
    arc.forEach((pt, idx) => {
      const ax = cx + (pt[0] * scaleZ);
      const az = originZ - (pt[2] * scaleZ);
      if (idx === 0) ctxXz.moveTo(ax, az);
      else ctxXz.lineTo(ax, az);
    });
    ctxXz.stroke();
  }

  // --- Side-Elevation Radar (Y - Z Plane) ---
  ctxYz.clearRect(0, 0, w, h);
  const groundY = h - 45; // Launcher optical height baseline

  // Range grid
  ctxYz.strokeStyle = "rgba(56, 189, 248, 0.18)";
  ctxYz.lineWidth = 1;
  [2.0, 4.0, 6.0].forEach(r => {
    const rZ = 20 + (r * scaleZ);
    ctxYz.beginPath();
    ctxYz.moveTo(rZ, 10);
    ctxYz.lineTo(rZ, h - 10);
    ctxYz.stroke();
    ctxYz.fillStyle = "rgba(100, 116, 139, 0.6)";
    ctxYz.fillText(`${r}m`, rZ + 3, h - 12);
  });

  // Ground plane
  ctxYz.strokeStyle = "rgba(100, 116, 139, 0.4)";
  ctxYz.beginPath();
  ctxYz.moveTo(10, groundY);
  ctxYz.lineTo(w - 10, groundY);
  ctxYz.stroke();

  // Launcher Origin
  ctxYz.fillStyle = "#38bdf8";
  ctxYz.beginPath();
  ctxYz.arc(20, groundY, 4, 0, 2 * Math.PI);
  ctxYz.fill();

  // Plot Radar Targets (Y - Z)
  (radarState.targets || []).forEach(t => {
    const pz = 20 + (t.z_m * scaleZ);
    const py = groundY - (t.y_m * scaleZ);

    ctxYz.fillStyle = t.class_name === "debris" ? "#ef4444" : "#10b981";
    ctxYz.beginPath();
    ctxYz.arc(pz, py, 5, 0, 2 * Math.PI);
    ctxYz.fill();

    ctxYz.fillStyle = "#e2e8f0";
    ctxYz.fillText(`#${t.track_id} (${t.y_m > 0 ? '+' : ''}${t.y_m.toFixed(1)}m)`, pz + 7, py + 3);
  });

  // Plot Parabolic Gravity-Curved Net Arc (Side Elevation: shows projectile gravity sag)
  if (arc.length > 1) {
    ctxYz.strokeStyle = "rgba(52, 211, 153, 0.9)";
    ctxYz.lineWidth = 2;
    ctxYz.beginPath();
    arc.forEach((pt, idx) => {
      const az = 20 + (pt[2] * scaleZ);
      const ay = groundY - (pt[1] * scaleZ);
      if (idx === 0) ctxYz.moveTo(az, ay);
      else ctxYz.lineTo(az, ay);
    });
    ctxYz.stroke();
  }
}

// ============================================================================
// 4. Live GNC Controls & Sliders
// ============================================================================
function initLiveControls() {
  const syncParams = debounce(async () => {
    try {
      await fetch("/api/live/params", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          v_net: state.vNet,
          t_lat: state.tLat,
          d_net: state.dNet,
          magnetic_assist: state.magneticAssist,
          auto_fire: state.autoFire,
        }),
      });
    } catch (e) {
      console.warn("GNC param sync notice:", e);
    }
  }, 200);

  // Source Switcher
  const sourceButtons = document.querySelectorAll("#liveSourceGroup .source-btn");
  sourceButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      sourceButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      state.liveSource = btn.getAttribute("data-source");

      try {
        await fetch("/api/live/source", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ source: state.liveSource }),
        });
      } catch (e) {
        console.warn("Source change notice:", e);
      }
    });
  });

  // Lab Frame Capture
  const btnCapture = document.getElementById("btnCaptureLabFrame");
  if (btnCapture) {
    btnCapture.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/capture-lab-frame", { method: "POST" });
        const d = await res.json();
        alert(`Lab frame successfully queued: ${d.message}`);
      } catch (err) {
        alert("Capture failed: " + err.message);
      }
    });
  }

  // Sliders
  const vSlider = document.getElementById("vNetSlider");
  const vVal = document.getElementById("vNetVal");
  if (vSlider) {
    vSlider.addEventListener("input", (e) => {
      state.vNet = parseFloat(e.target.value);
      if (vVal) vVal.textContent = `${state.vNet.toFixed(1)} m/s`;
      syncParams();
    });
  }

  const tSlider = document.getElementById("tLatSlider");
  const tVal = document.getElementById("tLatVal");
  if (tSlider) {
    tSlider.addEventListener("input", (e) => {
      state.tLat = parseFloat(e.target.value);
      if (tVal) tVal.textContent = `${state.tLat.toFixed(2)} s`;
      syncParams();
    });
  }

  const dSlider = document.getElementById("dNetSlider");
  const dVal = document.getElementById("dNetVal");
  if (dSlider) {
    dSlider.addEventListener("input", (e) => {
      state.dNet = parseFloat(e.target.value);
      if (dVal) dVal.textContent = `${state.dNet.toFixed(1)} m`;
      syncParams();
    });
  }

  // Toggles
  const magToggle = document.getElementById("magneticToggle");
  if (magToggle) {
    magToggle.addEventListener("change", (e) => {
      state.magneticAssist = e.target.checked;
      syncParams();
    });
  }

  const autoToggle = document.getElementById("autoFireToggle");
  if (autoToggle) {
    autoToggle.addEventListener("change", (e) => {
      state.autoFire = e.target.checked;
      syncParams();
    });
  }

  // Manual Fire Button
  const btnFire = document.getElementById("btnFireNet");
  if (btnFire) {
    btnFire.addEventListener("click", async () => {
      try {
        const res = await fetch("/api/kpi/fire", { method: "POST" });
        const data = await res.json();
        if (data.status === "fired") {
          updateKpiSummary();
          const trial = data.trial;
          alert(`🎯 PNEUMATIC NET FIRED!\n\nTarget: ${trial.target_class}\nOutcome: ${trial.capture_success ? "✅ CAPTURED" : "❌ MISSED"}\n3D Miss Error: ${trial.miss_error_cm} cm\nEffective Net Radius: ${trial.effective_radius_cm} cm`);
        } else {
          alert(`Launch Notice: ${data.message}`);
        }
      } catch (err) {
        alert("Launch command failed: " + err.message);
      }
    });
  }
}

async function updateKpiSummary() {
  try {
    const res = await fetch("/api/kpi/summary");
    const data = await res.json();

    const k4 = document.getElementById("kpiActive");
    const k5 = document.getElementById("kpiRisk");

    if (state.missionMode === "GROUND_DEMONSTRATOR") {
      if (k4) k4.textContent = `${data.capture_success_rate_pct}%`;
      if (k5) k5.textContent = `${data.mean_miss_error_cm} cm`;
    }
  } catch (e) {
    console.warn("KPI fetch notice:", e);
  }
}

// ============================================================================
// 5. Viewport Stream / Keyframe Toggles (Orbital Video)
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
// 6. Video Workspace Controls & Kinematics Engine
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

  state.currentTelemetry = state.videoTracks;
  state.currentSummary = state.videoSummary;

  const hudVideo = document.getElementById("hudVideo");
  const hudCanvas = document.getElementById("hudCanvas");

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

  if (data.annotated_video_url && hudVideo) {
    hudVideo.pause();
    hudVideo.muted = true;
    hudVideo.playsInline = true;
    hudVideo.autoplay = true;
    hudVideo.loop = true;
    hudVideo.controls = true;

    hudVideo.src = `${data.annotated_video_url}?t=${Date.now()}`;
    hudVideo.style.display = "block";
    if (hudCanvas) hudCanvas.style.display = "none";

    hudVideo.oncanplay = () => {
      hudVideo.play().catch((e) => console.warn("Autoplay notice:", e));
    };

    hudVideo.onerror = (e) => {
      hudVideo.style.display = "none";
      if (hudCanvas) hudCanvas.style.display = "block";
    };
  }

  const toggleBar = document.getElementById("viewportToggleBar");
  if (toggleBar) toggleBar.style.display = "flex";

  const reticle = document.getElementById("reticleText");
  if (reticle) {
    reticle.textContent = `TRACKED ${data.processed_frames}/${data.total_frames} FRAMES // DURATION: ${data.duration_sec}s // FPS: ${data.fps} // ${state.videoTracks.length} TARGETS`;
  }

  updateInsightsBanner(state.videoSummary, state.videoTracks);
  if (state.missionMode === "ORBITAL_SURVEILLANCE") {
    updateDashboardKPIs(state.videoSummary);
  }
  updateTelemetryTable();
}

// ============================================================================
// 7. Space Object Gallery & 2x2 Tiled Small-Debris Inspection
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

  const tiledToggle = document.getElementById("tiledToggle");
  if (tiledToggle) {
    tiledToggle.addEventListener("change", (e) => {
      state.tiledInspection = e.target.checked;
      debouncedRerunGallery();
    });
  }
}

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
      loadSample(samples[0], false);
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

function initFileUploads() {
  const btnUploadVideo = document.getElementById("btnUploadVideo");
  const videoInput = document.getElementById("videoInput");
  if (btnUploadVideo && videoInput) {
    btnUploadVideo.addEventListener("click", () => videoInput.click());
    videoInput.addEventListener("change", (e) => {
      if (e.target.files && e.target.files.length > 0) {
        handleVideoFile(e.target.files[0]);
        videoInput.value = "";
      }
    });
  }

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
}

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

  showGallerySpinner(state.tiledInspection ? "EVALUATING 2×2 TILED CROPS..." : "EVALUATING YOLO11s INFERENCE...");

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
    }

    state.imageDetections = data.detections || [];
    state.imageSummary = data.summary || {};

    state.currentTelemetry = state.imageDetections;
    state.currentSummary = state.imageSummary;

    // Draw image and bounding boxes
    ctx.drawImage(state.activeImageData, 0, 0, canvas.width, canvas.height);
    renderBoundingBoxes(ctx, state.imageDetections);

    const reticle = document.getElementById("galleryReticle");
    if (reticle) {
      reticle.textContent = `OPTICAL ACQUISITION: ${state.imageDetections.length} TARGETS IDENTIFIED // FOV ${canvas.width}×${canvas.height}`;
    }

    const targetStateEl = document.getElementById("galleryTargetState");
    if (targetStateEl) {
      if (state.imageDetections.length > 0) {
        const top = state.imageDetections[0];
        targetStateEl.innerHTML = `${getStateBadgeHtml(top.operational_state)} <span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono); margin-left:6px;">Conf: ${Math.round(top.confidence * 100)}%</span>`;
      } else {
        targetStateEl.innerHTML = `<span class="badge-pill" style="color:var(--text-muted);">BELOW CUTOFF</span>`;
      }
    }

    if (state.missionMode === "ORBITAL_SURVEILLANCE") {
      updateDashboardKPIs(state.imageSummary);
    }
    updateTelemetryTable();
  } catch (err) {
    console.error("Gallery inference failed:", err);
  } finally {
    hideGallerySpinner();
  }
}

// ============================================================================
// 8. Canvas Overlay Renderers
// ============================================================================
function renderBoundingBoxes(ctx, detections) {
  if (!detections || detections.length === 0) return;

  detections.forEach((det) => {
    const [x1, y1, x2, y2] = det.bbox;
    const w = x2 - x1;
    const h = y2 - y1;
    const color = STATE_COLORS[det.operational_state] || "#38bdf8";

    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.strokeRect(x1, y1, w, h);

    const corner = Math.min(18, Math.max(8, w * 0.15));
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(x1, y1 + corner); ctx.lineTo(x1, y1); ctx.lineTo(x1 + corner, y1);
    ctx.moveTo(x2 - corner, y1); ctx.lineTo(x2, y1); ctx.lineTo(x2, y1 + corner);
    ctx.moveTo(x1, y2 - corner); ctx.lineTo(x1, y2); ctx.lineTo(x1 + corner, y2);
    ctx.moveTo(x2 - corner, y2); ctx.lineTo(x2, y2); ctx.lineTo(x2, y2 - corner);
    ctx.stroke();

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
// 9. Dedicated Telemetry Table & Exports
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
    const riskVal = t.risk_score !== undefined ? t.risk_score.toFixed(3) : "0.000";

    tr.innerHTML = `
      <td><strong>${trackIdDisplay}</strong></td>
      <td><strong>${t.display_name}</strong></td>
      <td><code>${t.class_name}</code></td>
      <td><strong>${Math.round(t.confidence * 100)}%</strong></td>
      <td><span style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">${bboxDisplay}</span></td>
      <td>${(t.area_ratio * 100).toFixed(2)}%</td>
      <td>${tumbleDisplay}</td>
      <td><strong style="color:${t.risk_score > 0.6 ? 'var(--state-hazardous)' : 'var(--text-main)'};">${riskVal}</strong></td>
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

function initExports() {
  const btnCsv = document.getElementById("btnExportCsv");
  if (btnCsv) btnCsv.addEventListener("click", exportCsv);

  const btnJson = document.getElementById("btnExportJson");
  if (btnJson) btnJson.addEventListener("click", exportJson);
}

function exportCsv() {
  if (state.missionMode === "GROUND_DEMONSTRATOR") {
    window.location.href = "/api/kpi/export-csv";
    return;
  }

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

async function exportJson() {
  if (state.missionMode === "GROUND_DEMONSTRATOR") {
    try {
      const res = await fetch("/api/kpi/export-json");
      const trials = await res.json();
      const jsonStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(trials, null, 2));
      const link = document.createElement("a");
      link.setAttribute("href", jsonStr);
      link.setAttribute("download", `spaci_capture_trials_${Date.now()}.json`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      return;
    } catch (e) {
      console.warn("Export JSON error:", e);
    }
  }

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
// 10. Spinners & Benchmarks
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
