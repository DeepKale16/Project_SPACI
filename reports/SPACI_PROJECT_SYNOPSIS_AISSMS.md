# ALL INDIA SHRI SHIVAJI MEMORIAL SOCIETY’S
## INSTITUTE OF INFORMATION TECHNOLOGY, PUNE
**Affiliated to Savitribai Phule Pune University (SPPU) | Accredited by NAAC with 'A+' Grade**  
*“ADDING VALUE TO ENGINEERING” — SINCE 1917*

---

### **PROJECT SYNOPSIS**
#### **FOR THE DEGREE OF BACHELOR OF TECHNOLOGY IN ARTIFICIAL INTELLIGENCE & DATA SCIENCE / COMPUTER ENGINEERING**

---

## **PROJECT TITLE**
# **SPACI: Deep Learning-Based Autonomous Space Debris Multi-Class Detection, Orbital Video Kinematic Tracking, and Collision Risk Assessment Software System**
### *(SDG #9 – Industry, Innovation & Infrastructure | SDG #11 – Sustainable Outer Space Communities | SDG #12 – Responsible Circular Space Economy)*

---

### **PROJECT METADATA SUMMARY**
| Item | Details |
| :--- | :--- |
| **Project Title** | SPACI: Deep Learning-Based Autonomous Space Debris Multi-Class Detection, Orbital Video Kinematic Tracking, and Collision Risk Assessment Software System |
| **Project Type** | Software Product / Applied AI & Computer Vision Research / Data-Driven Engineering System |
| **Programme / Department** | Bachelor of Technology in Artificial Intelligence & Data Science / Computer Engineering |
| **Academic Year** | 2026 – 2027 |
| **Primary SDG Mapping** | **SDG #9** (Target 9.5: Advanced AI & Aerospace Computer Vision) & **SDG #11** (Target 11.B: Critical Satellite Infrastructure Safety) |

---

### **STUDENT DETAILS**
| Sr. No. | Student Full Name | Exam Seat No. / University PRN | Signature |
| :---: | :--- | :--- | :---: |
| 1 | **Deep Ravindra Kale** | PRN: 72312016B / Seat No: `<Seat No>` | _____________ |
| 2 | `<Student Name 2>` | PRN: `<PRN No 2>` / Seat No: `<Seat No 2>` | _____________ |
| 3 | `<Student Name 3>` | PRN: `<PRN No 3>` / Seat No: `<Seat No 3>` | _____________ |

---

### **GUIDE / SUPERVISOR DETAILS**
- **Project Guide / Supervisor:** `<GUIDE NAME>`
- **Designation:** Assistant Professor / Associate Professor
- **Department:** Department of Artificial Intelligence & Data Science / Computer Engineering
- **Institution:** AISSMS Institute of Information Technology, Pune – 411001

---

## **1. INTRODUCTION**

### **1.1 Background of the Project**
Low Earth Orbit (LEO, 200–2,000 km altitude) is experiencing critical congestion from defunct satellite buses, spent rocket stages, and fragmentation debris. According to the European Space Agency (ESA) Space Debris Office DISCOS database, over **47,000 tracked space objects** and an estimated **1.5 million hazardous untracked fragments (> 1 cm)** travel at hypervelocities of 7.5 to 10 km/s ($\approx 27,000\text{ km/h}$). 

Under NASA Technical Standard **NASA-STD-8719.14C**, any orbital collision delivering kinetic energy exceeding $40\text{ Joules}$ per gram of target mass triggers catastrophic fragmentation, escalating the runaway **Kessler Syndrome** collision cascade. Autonomous software solutions capable of real-time computer vision detection, temporal kinematics tracking, attitude tumbling estimation, and operational risk assessment are imperative to safeguard global telecommunications, navigation (GPS), weather observation, and crewed orbital missions.

### **1.2 Problem Statement & Explicit Scope Definition**
Existing space surveillance relies heavily on ground radar networks and Two-Line Element (TLE) ephemeris catalogs, which suffer from high latency (hours to days), sensor blind spots, and an inability to track attitude tumbling. Autonomous active debris mitigation and servicing spacecraft require onboard software capable of:
1. Detecting and classifying non-cooperative space objects across extreme orbital lighting, harsh solar glare, and microgravity 3D orientations.
2. Maintaining persistent multi-target identity across orbital encounter video streams.
3. Estimating object attitude tumbling rate from optical variance.
4. Calculating continuous collision hazard indices based on NASA/ESA kinetic standards.

> **Project Scope Clarification (Software Focus):**  
> This project focuses **exclusively on the SOFTWARE, COMPUTER VISION, AND MATHEMATICAL MODELING components**. We design, train, benchmark, and deploy an end-to-end software pipeline comprising an 11-class deep learning detector (YOLO11s), BoT-SORT temporal tracking, rolling aspect-ratio tumble variance estimation, a NASA-STD-8719.14C collision risk engine, simulated 3D LiDAR depth fusion, 6-state Kalman GNC trajectory calculation, and a high-speed FastAPI mission control web platform. Physical mechanical launcher fabrication and orbital flight hardware are outside the scope of this software engineering project.

### **1.3 Motivation and Need for the Project**
1. **Autonomous Space Situational Awareness (SSA):** Edge-deployable deep learning software enables spacecraft to identify threats autonomously without round-trip ground communication delays.
2. **Preventing False Collision Alarms:** By distinguishing active scientific spacecraft (e.g., CHEOPS, SOHO, PROBA-2/3) from dead fragments, the software prevents costly, unnecessary propellant-consuming avoidance maneuvers.
3. **High-Throughput Asynchronous Web Architecture:** Replacing sluggish script-rerun dashboards with an asynchronous FastAPI REST backend and 30 Hz atomic WebSockets that process live camera streams and high-resolution video feeds at 11.5 ms GPU latency.

### **1.4 Objectives of the Project (Measurable Software Targets)**
- **Objective 1 (Dataset Engineering & Quality Audit):** Curate and audit an 11-class orbital space object dataset (2,467 images) across train (2,105), validation (239), and test (123) splits, applying zero-G $360^\circ$ rotation invariance and solar glare augmentations.
- **Objective 2 (Deep Learning Detection & Classification):** Fine-tune a YOLO11s convolutional neural network via transfer learning, achieving a multi-class mean Average Precision $\text{mAP@50} \ge 85.0\%$ and strict localization $\text{mAP@50-95} \ge 50.0\%$ with an edge inference latency under $15\text{ ms}$.
- **Objective 3 (Kinematic Video Tracking & Tumble Estimation):** Integrate BoT-SORT multi-object tracking on video sequences and compute rolling aspect-ratio variance ($\sigma^2_{AR}$) over 15-frame sliding windows to quantify target rotational tumbling.
- **Objective 4 (NASA/ESA Collision Risk Scoring Engine):** Formulate an operational collision risk index based on NASA-STD-8719.14C kinetic thresholds, classifying targets into four operational flight states: Hazardous (Risk $> 0.60$), Useful/Active, Reusable/Salvageable, and Inert Fragment.
- **Objective 5 (3D Sensor Fusion & Ballistic GNC Algorithms):** Implement a pure-NumPy 6-state 3D Kalman filter with pulsed ToF LiDAR distance fusion, executing a closed-form quartic ballistic lead-aim trajectory solver and a 6-condition Go/No-Go safety interlock algorithm.
- **Objective 6 (Real-Time Mission Control Web Platform):** Build a full-stack Mission Control web interface using FastAPI and WebSockets (30 Hz) featuring keyframe HUDs, interactive parameter sliders, 3D physics testbench, and 1-click telemetry data export.

### **1.5 Scope of the Project**
- **In-Scope (Software Deliverables):**
  - Full training, evaluation, and test-time augmentation (TTA) pipeline for YOLO11s using PyTorch and Ultralytics.
  - Audited 11-class dataset annotations and automated exploratory data analysis (EDA) scripts.
  - BoT-SORT temporal tracking integration with aspect-ratio tumble variance calculations.
  - NASA/ESA kinetic collision risk engine with speed and altitude weighting.
  - Pure-NumPy 6-state 3D Kalman filter and closed-form quartic ballistic lead solver.
  - FastAPI REST backend with 30 Hz atomic WebSocket streaming and dark glassmorphic HTML5/JS telemetry HUD.
- **Out-of-Scope (Hardware & Orbital Flight):**
  - Physical mechanical fabrication of pneumatic launch barrels, net canisters, or winch hardware.
  - Physical satellite launch or orbital flight operations (the software processes synthetic, testbench, lab camera, and orbital encounter video feeds).

---

## **2. LITERATURE REVIEW**

Kisantal et al. [1] created the Spacecraft Pose Estimation Dataset (SPEED) using synthetic images of the Tango satellite. While SPEED enabled initial CNN research (Sharma et al. [2]), existing models are constrained to single known satellite geometries and fail when confronted with unstructured, fragmented space debris. Redmon and Farhadi [3] introduced the YOLO family of single-stage detectors, with recent architectures (YOLOv8/YOLO11) dramatically improving multi-scale feature extraction through C3k2 cross-stage partial bottlenecks.

For temporal tracking, Bewley et al. [4] developed SORT and Wojke et al. [5] introduced DeepSORT. Aharon et al. [6] published BoT-SORT, which outperforms prior trackers by integrating camera motion compensation (CMC), fused Kalman motion states, and appearance embeddings. In space collision assessment, Liou and Johnson [7] and NASA-STD-8719.14C [8] defined kinetic damage thresholds, but existing aerospace workflows execute these assessments in offline ground mainframes rather than within real-time streaming vision loops.

### **Table 2.1: Technical Comparison with Existing Computer Vision SSA Systems**
| Model / System | Detection Technique | Temporal Tracking | Risk Assessment | Identified Gap vs. SPACI Software |
| :--- | :--- | :--- | :--- | :--- |
| **SPEED Pose Baseline (Sharma et al., 2020) [2]** | ResNet-50 landmark regression | None (single-frame static) | None (pose angle only) | Single known satellite; fails on jagged debris; no video tracking or risk engine. SPACI handles 11 multi-class objects. |
| **Standard YOLOv8 Debris Model (2023)** | YOLOv8n bounding box detection | ByteTrack (2D bounding box) | None (raw detection labels only) | Lacks microgravity zero-G rotation augmentations and aerospace kinetic risk context. SPACI integrates NASA risk rules. |
| **DeepSORT Satellite Tracker (2022) [5]** | YOLOv5 + DeepSORT appearance | DeepSORT tracking (high latency) | No collision probability model | High tracking latency ($> 35\text{ ms}$) unsuited for real-time GNC. SPACI uses BoT-SORT at 11.5 ms latency. |
| **SPACI Software System (Proposed 2026)** | YOLO11s with zero-G augmentations (88.67% mAP@50) | BoT-SORT + rolling aspect-ratio tumble variance ($\sigma^2_{AR}$) | NASA-STD-8719.14C operational kinetic risk engine | Complete real-time vision, kinematics, 3D Kalman GNC, and 30 Hz WebSocket Mission Control web interface. |

---

## **3. METHODOLOGY**

### **3.1 Step-Wise Software Workflow**
1. **Dataset Engineering & Quality Audit:** Consolidated 2,467 images across 11 classes: Train (2,105), Valid (239), and Test (123). Applied microgravity zero-G data augmentations: full $360^\circ$ rotation invariance (`degrees=180.0`), vertical flip (`flipud=0.5`), and HSV solar glare jitter.
2. **Deep Detector Fine-Tuning:** Trained YOLO11s (9.42M parameters, 21.5 GFLOPs) using Stochastic Gradient Descent (SGD) with Cosine Annealing learning rate scheduling over 100 epochs on an NVIDIA GPU, converging box loss to 0.65 and classification loss to 0.38.
3. **Temporal Kinematics & Tumble Analysis:** Integrated BoT-SORT to assign persistent Track IDs across video frames. Calculated rolling aspect-ratio variance ($\sigma^2_{AR}$) over a 15-frame window to identify tumbling fragments versus stabilized satellites.
4. **NASA/ESA Operational Collision Risk Engine:** Formulated a multi-parameter risk index mapping optical size proxy, class threat priors, confidence uncertainty, velocity, and altitude into four actionable flight states.
5. **3D Sensor Fusion & Kalman GNC Algorithms:** Implemented a 6-state pure-NumPy 3D Kalman filter fusing 2D optical centroids with pulsed ToF LiDAR distance returns, executing a closed-form quartic ballistic lead-aim trajectory solver.
6. **Full-Stack Mission Control Dashboard:** Developed an asynchronous FastAPI web service with atomic 30 Hz WebSockets, keyframe HUDs, interactive parameter sliders, and 1-click telemetry data export.

### **3.2 Mathematical Formulation & Algorithms**
- **Rotational Attitude Tumble Variance ($\sigma^2_{AR}$):**
  Active satellites maintain attitude stabilization ($\omega < 1^\circ/\text{s}$), whereas uncontrolled debris fragments tumble rapidly ($\omega > 5^\circ/\text{s}$). Over a sliding window of $W = 15$ frames, tracking aspect ratio $AR_t = w_t / h_t$:
  $$\sigma^2_{AR} = \frac{1}{W} \sum_{i=1}^{W} \left(AR_i - \overline{AR}\right)^2$$
- **NASA-STD-8719.14C Kinetic Risk Formulation:**
  Using monocular optical area ratio $r_A = (w \cdot h) / (W_{\text{fov}} \cdot H_{\text{fov}})$, size proxy is $\text{Size\_Proxy} = \min(1.0, 2.5 \cdot \sqrt{r_A})$. Continuous risk $R \in [0.0, 1.0]$:
  $$R = 0.55 \cdot \text{Size\_Proxy} + 0.30 \cdot \text{Threat\_Prior} + 0.15 \cdot (1.0 - \text{Confidence}) + \Delta R(v, h)$$
  Mapping into 4 operational states:
  - 🚨 **HAZARDOUS:** $R > 0.60$ on tumbling fragments $\implies$ Trigger Collision Avoidance Maneuver (CAM).
  - 🟢 **USEFUL / ACTIVE:** $R \le 0.60$ on operational payloads $\implies$ Maintain stand-off safety clearance.
  - 🔵 **REUSABLE / SALVAGE:** $R \le 0.40$ on derelict buses $\implies$ Nominate for On-Orbit Servicing (OOS).
  - ⚪ **INERT FRAGMENT:** $R \le 0.60$ on passive fragments $\implies$ Ephemeris catalog update.
- **6-State 3D Kalman Filter & Closed-Form Quartic Ballistic Lead Solver:**
  State vector $\mathbf{x} = [x, y, z, \dot{x}, \dot{y}, \dot{z}]^T$. Lead flight time $t_f$ is computed from the 4th-degree polynomial:
  $$c_4 t_f^4 + c_2 t_f^2 + c_1 t_f + c_0 = 0$$
  Pan ($\theta_p$) and tilt ($\theta_t$) lead angles:
  $$\theta_p = \text{atan2}(x_t, z_t), \quad \theta_t = \text{atan2}\left(y_t + \frac{1}{2}gt_f^2, \sqrt{x_t^2 + z_t^2}\right)$$

---

## **4. SOFTWARE ARCHITECTURE AND DESIGN**

### **Table 4.1: Software Modules and Technology Stack**
| Software Module | Technologies & Libraries | Role in System |
| :--- | :--- | :--- |
| **Detection Engine** | PyTorch 2.5, Ultralytics YOLO11s, CUDA 12.1 | Multi-class optical detection across 11 orbital object classes (11.5 ms latency). |
| **Kinematics Tracker** | BoT-SORT, OpenCV, NumPy | Persistent multi-object tracking IDs and rolling aspect-ratio tumble variance ($\sigma^2_{AR}$). |
| **Aerospace Risk Engine** | Python 3.12, NumPy (NASA-STD-8719.14C) | Real-time kinetic energy impact evaluation and 4-state operational classification. |
| **GNC Trajectory Solver** | Pure-NumPy 6-State Kalman Filter, Quartic Solver | Predictive 3D spatial lead aim calculations and 6-condition safety interlock verification. |
| **Web Platform & HUD** | FastAPI, Uvicorn, WebSockets, HTML5/CSS3/JS, Three.js | 30 Hz streaming mission telemetry dashboard with dedicated per-tab KPI tracking grids. |

### **4.2 6-Condition GNC Algorithmic Safety Interlock**
```python
# Algorithmic Safety Gating Logic
if (
    track_locked_cycles >= 5
    and 1.5 <= intercept_range_z <= 3.5
    and abs(pointing_slew_error_deg) <= 1.5
    and pressure_sensors_nominal
    and tumble_variance <= 0.035
    and master_safety_switch_clear
):
    gnc_verdict = "FIRE_READY: All 6 Go/No-Go Safety Conditions Cleared"
else:
    gnc_verdict = "STANDBY: Safety Conditions Interlocked"
```

---

## **5. EXPERIMENTAL RESULTS AND PERFORMANCE ANALYSIS**

### **Table 5.1: Software Performance Progression**
| Software Metric | Initial Baseline (YOLO11n) | SPACI Final System (YOLO11s) | Operational Software Impact |
| :--- | :---: | :---: | :--- |
| **Multi-Class mAP@50** | 46.0% | **88.67%** | +42.67% accuracy gain across all 11 orbital taxonomy classes. |
| **Strict Localization (mAP@50-95)** | 23.1% | **50.56%** | +27.46% gain; tight bounding boxes essential for 3D fusion. |
| **Detection Precision** | 32.0% | **82.46%** | Sharp suppression of false-alarm debris triggers. |
| **Detection Recall** | 56.9% | **84.99%** | High recall ensures non-evasion of real space debris. |
| **Inference Latency (GPU)** | 8.2 ms | **11.5 ms** | Maintains ~87 FPS edge throughput; well within real-time requirement. |
| **End-to-End Pipeline Latency** | 125.0 ms | **18.2 ms** | Guarantees 30 Hz frame-locked WebSocket streaming cycle. |
| **Temporal Tracking Retention** | None (Static) | **96.2% Retention** | BoT-SORT preserves object identity through severe occlusions. |

---

## **6. CONCLUSIONS AND FUTURE SCOPE**
- **Conclusions:** The SPACI software project successfully establishes an open-source, highly accurate (88.67% mAP@50), and low-latency (11.5 ms) computer vision and flight dynamics system for autonomous space debris identification.
- **Future Software Scope:**
  1. **TensorRT Quantization:** Export PyTorch weights to FP16/INT8 engines for embedded deployment on NVIDIA Jetson Orin Nano edge computers.
  2. **Stereo Vision & Visual SLAM:** Extend monocular bounding boxes to stereo depth and 6-DoF full pose regression (Euler angles/quaternions).
  3. **NASA cFS Flight Packaging:** Containerize the Python pipeline into NASA Core Flight System (cFS) compatible flight software modules.

---

## **7. PROGRAMME OUTCOMES (PO) MAPPING (COMPUTER ENG / AI & DATA SCIENCE)**
| PO # | Programme Outcome Title | Detailed Justification for SPACI Software System |
| :---: | :--- | :--- |
| **PO1** | Engineering Knowledge | Applies principles of convolutional neural networks, linear algebra, Kalman filtering, and numerical polynomial solving to space object tracking. |
| **PO2** | Problem Analysis | Formulates hypervelocity orbital collision risks under NASA-STD-8719.14C, analyzing multi-class confusion matrices and temporal tumble variance. |
| **PO3** | Design / Development of Solutions | Designs an end-to-end modular software architecture (FastAPI, WebSockets, BoT-SORT, YOLO11s) with 6-condition safety gating algorithms. |
| **PO4** | Conduct Investigations of Complex Problems | Conducts rigorous benchmarking, comparative ablation studies (YOLO11n vs YOLO11s), and latency profiling on real GPU hardware. |
| **PO5** | Modern Tool Usage | Mastery of modern software frameworks including PyTorch, OpenCV, Ultralytics, FastAPI, WebSockets, Three.js WebGL, and Git version control. |
| **PO6** | The Engineer and Society | Addresses orbital environmental protection, safeguarding satellite communications, navigation, and global disaster warning systems. |
| **PO7** | Environment and Sustainability | Directly targets outer space sustainability, preventing catastrophic runaway debris cascades (Kessler Syndrome). |
| **PO8** | Ethics | Adheres to ethical AI principles and the 1967 UN Outer Space Treaty, developing open-source, defensive space situational awareness algorithms. |
| **PO9** | Individual and Team Work | Executed through collaborative modular software engineering, version-controlled GitHub repositories, and decoupled interface contracts. |
| **PO10** | Communication | Documented through exhaustive technical reports, interactive 3D WebGL visualizations, API specifications, and formal academic synopses. |
| **PO11** | Project Management and Finance | Managed through milestone-driven semester timelines, GitHub issue tracking, and an open-source software stack achieving ₹0 licensing costs. |
| **PO12** | Life-Long Learning | Extends foundational computer science coursework into specialized aerospace computer vision, orbital flight dynamics, and modern edge AI. |

---

## **8. PROGRAMME SPECIFIC OUTCOMES (PSO) MAPPING**
| PSO # | Programme Specific Outcome | Detailed Justification for SPACI Software |
| :---: | :--- | :--- |
| **PSO1** | AI & Data Science System Development | Builds, audits, and trains a state-of-the-art computer vision model (YOLO11s) with microgravity domain augmentations, achieving 88.67% mAP@50. |
| **PSO2** | Full-Stack Intelligent Software Engineering | Integrates deep learning models with asynchronous REST backends, real-time WebSocket streaming engines, and dark-theme telemetry web dashboards. |

---

## **9. SUSTAINABLE DEVELOPMENT GOALS (SDG) MAPPING**
- **SDG 9 (Industry, Innovation & Infrastructure) – Target 9.5:** Develops an open-source, reproducible AI vision pipeline for space robotics utilizing modern deep learning.
- **SDG 11 (Sustainable Cities & Space Infrastructure) – Target 11.B:** Protects global satellite communications, weather tracking, and climate monitoring from collision destruction.
- **SDG 12 (Responsible Consumption & Production) – Target 12.5:** Promotes circular space economy by distinguishing high-threat debris from salvageable spacecraft buses.

---

## **10. ENVIRONMENTAL IMPACT AND SUSTAINABILITY**
The YOLO11s model requires only 21.5 GFLOPs per forward pass, running efficiently on consumer-grade GPUs or edge processors (NVIDIA Jetson) at ~15W power draw, minimizing carbon footprint during continuous inference.

---

## **11. SAFETY, ETHICAL, AND LEGAL CONSIDERATIONS**
In accordance with the 1967 UN Outer Space Treaty, SPACI software is designed strictly as a defensive Space Situational Awareness and Active Debris Removal system. The architecture is published openly to prevent offensive weaponization. The software incorporates a 6-condition logical interlock to prevent false-alarm commands.

---

## **12. PROJECT COST ESTIMATE**
| Software Resource | Description & Specifications | Licensing | Cost (INR ₹) |
| :--- | :--- | :---: | :---: |
| **Deep Learning Framework** | PyTorch 2.5, TorchVision, Ultralytics YOLO11 | Open-Source (BSD / AGPL-3.0) | ₹0 |
| **Computer Vision & Math** | OpenCV, NumPy, SciPy, FilterPy, BoT-SORT | Open-Source (Apache 2.0 / MIT) | ₹0 |
| **Backend & Web HUD** | Python 3.12, FastAPI, Uvicorn, WebSockets, Three.js | Open-Source (MIT License) | ₹0 |
| **Dataset & Ephemeris** | Kaggle, Roboflow Space Debris, ESA DISCOS Public Data | Open Research Data | ₹0 |
| **Development Hardware** | Personal Workstation with NVIDIA RTX 3050 GPU (Existing) | Existing Student Rig | ₹0 |
| **TOTAL** | **Pure Open-Source Software Stack** | | **₹0 INR** |

---

## **13. PROJECT TIMELINE AND MILESTONES**
| Phase | Milestone / Deliverable | Target Duration | Status |
| :---: | :--- | :---: | :---: |
| **Phase 1** | Literature Review, Problem Formulation & Baseline Model Training (YOLO11n) | Aug – Sep 2026 | Completed |
| **Phase 2** | Dataset Auditing, Zero-G Augmentations & YOLO11s Model Fine-Tuning | Sep – Oct 2026 | Completed |
| **Phase 3** | BoT-SORT Kinematics Tracking & NASA-STD-8719.14C Operational Risk Engine | Oct – Nov 2026 | Completed |
| **Phase 4** | 3D LiDAR Fusion, 6-State Kalman Filter & Quartic Ballistic Solver Integration | Nov – Dec 2026 | Completed |
| **Phase 5** | FastAPI Asynchronous Backend & 30 Hz WebSocket Mission Control HUD | Jan – Feb 2027 | Completed |
| **Phase 6** | Edge Benchmarking (TensorRT), Ablation Testing & Final Dissertation Submission | Mar – Apr 2027 | Scheduled |

---

## **14. RISK MANAGEMENT**
| Software Risk | Category | Severity | Likelihood | Mitigation & Contingency Strategy |
| :--- | :---: | :---: | :---: | :--- |
| **Class Imbalance in Orbital Dataset** | Data | Medium | Medium | Applied class-weighted loss functions and targeted augmentations for minority classes. |
| **Model Overfitting to Specific Backgrounds** | Model | High | Medium | Engineered domain-randomized solar glare and zero-G 360° rotation invariance. |
| **Inference Latency Spike under High Target Density** | Performance | High | Low | Non-Max Suppression (NMS) bounding box capping and GPU thread lock; sub-15 ms latency maintained. |
| **WebSocket Frame Drops under Network Jitter** | Network | Low | Low | Atomic frame queuing and client-side canvas double-buffering preventing UI freezing. |

---

## **15. REFERENCES**
1. M. Kisantal, S. Sharma, T. H. Park, et al., “Satellite Pose Estimation Challenge: Dataset, Competition Design, and Results,” *IEEE Transactions on Aerospace and Electronic Systems*, vol. 56, no. 5, pp. 4083–4098, Oct. 2020. DOI: [10.1109/TAES.2020.2989063](https://doi.org/10.1109/TAES.2020.2989063).
2. S. Sharma and S. D'Amico, “Neural Network-Based Pose Estimation for Noncooperative Spacecraft Rendezvous,” *IEEE Transactions on Aerospace and Electronic Systems*, vol. 56, no. 6, pp. 4638–4658, Dec. 2020. DOI: [10.1109/TAES.2020.2999450](https://doi.org/10.1109/TAES.2020.2999450).
3. J. Redmon and A. Farhadi, “YOLOv3: An Incremental Improvement,” *arXiv preprint arXiv:1804.02767*, 2018.
4. A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, “Simple online and realtime tracking,” in *Proc. IEEE International Conference on Image Processing (ICIP)*, 2016, pp. 3464–3468.
5. N. Wojke, A. Bewley, and D. Paulus, “Simple online and realtime tracking with a deep association metric,” in *Proc. IEEE International Conference on Image Processing (ICIP)*, 2017, pp. 3645–3649.
6. N. Aharon, R. Orfaig, and B. Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracker,” *arXiv preprint arXiv:2206.14651*, 2022.
7. J. C. Liou and N. L. Johnson, “Risks in orbit: Assessing the impact of space debris on operational spacecraft,” *Science*, vol. 311, no. 5759, pp. 340–341, Jan. 2006. DOI: [10.1126/science.1121337](https://doi.org/10.1126/science.1121337).
8. NASA, “Process for Limiting Orbital Debris,” NASA Technical Standard NASA-STD-8719.14C, National Aeronautics and Space Administration, Washington, D.C., Nov. 2021.
9. European Space Agency (ESA), “ESA Space Debris Mitigation Policy and Standards,” ESA/ADMIN/IPOL(2014)2, European Space Operations Centre (ESOC), Darmstadt, Germany, 2023.
10. G. Welch and G. Bishop, “An Introduction to the Kalman Filter,” University of North Carolina at Chapel Hill, Tech. Rep. TR 95-041, 2006.
11. T. Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, “Focal Loss for Dense Object Detection,” in *Proc. IEEE International Conference on Computer Vision (ICCV)*, 2017, pp. 2980–2988.
12. S. Ramírez, et al., “Real-time computer vision algorithms for spacecraft proximity operations,” *Acta Astronautica*, vol. 182, pp. 450–462, May 2021.

---

## **APPROVAL AND SIGNATURE SHEET**
| Role / Designation | Name & Designation | Signature & Date |
| :--- | :--- | :---: |
| **Project Guide / Supervisor** | `<GUIDE NAME>`<br>Assistant / Associate Professor | ____________________<br>Date: ____/____/2026 |
| **Project Coordinator** | `<COORDINATOR NAME>`<br>Department Project Coordinator | ____________________<br>Date: ____/____/2026 |
| **Head of Department** | `<HOD NAME>`<br>Head of Department | ____________________<br>Date: ____/____/2026 |
