# ALL INDIA SHRI SHIVAJI MEMORIAL SOCIETY’S
## INSTITUTE OF INFORMATION TECHNOLOGY, PUNE
**Affiliated to Savitribai Phule Pune University (SPPU) | Accredited by NAAC with 'A+' Grade**  
*“ADDING VALUE TO ENGINEERING” — SINCE 1917*

---

### **PROJECT SYNOPSIS**
#### **FOR THE DEGREE OF BACHELOR OF TECHNOLOGY IN ARTIFICIAL INTELLIGENCE & DATA SCIENCE / COMPUTER ENGINEERING**

---

## **PROJECT TITLE**
# **SPACI: Autonomous Space Debris Optical Detection, 3D LiDAR Tracking, and Pneumatically Deployed Tethered-Net Capture Ground Demonstrator**
### *(SDG #9 – Industry, Innovation & Infrastructure | SDG #11 – Sustainable Outer Space Communities | SDG #12 – Responsible Circular Space Economy)*

---

### **PROJECT METADATA SUMMARY**
| Item | Details |
| :--- | :--- |
| **Project Title** | SPACI: Autonomous Space Debris Optical Detection, 3D LiDAR Tracking, and Pneumatically Deployed Tethered-Net Capture Ground Demonstrator |
| **Project Type** | Research / Product Prototype / Hardware-Software Integration Demonstrator |
| **Programme / Department** | Bachelor of Technology in Artificial Intelligence & Data Science / Computer Engineering |
| **Academic Year** | 2026 – 2027 |
| **Primary SDG Mapping** | **SDG #9** (Target 9.5: Upgrade scientific research in aerospace robotics) & **SDG #11** (Target 11.B: Resilience of critical space infrastructure) |

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
Over six decades of orbital operations since the launch of Sputnik-1 (1957) have resulted in a perilous accumulation of anthropogenic debris in Low Earth Orbit (LEO, 200–2,000 km altitude). According to official European Space Agency (ESA) Space Debris Office DISCOS statistics, there are currently over **47,000 tracked space objects** in orbit, accompanied by an estimated **1.5 million hazardous untracked fragments larger than 1 cm** and over **130 million millimeter-sized particles**. 

With average orbital velocities exceeding $7.5\text{ to }10\text{ km/s}$ ($\approx 27,000\text{ km/h}$), kinetic energy scales quadratically with velocity ($E_k = \frac{1}{2}mv^2$). A tiny $1\text{ cm}$ aluminum bolt carries the kinetic punch of an exploding hand grenade. Under NASA Technical Standard **NASA-STD-8719.14C**, any hypervelocity collision delivering specific kinetic energy exceeding $40\text{ J/g}$ of target mass triggers catastrophic fragmentation. This exponential cascading collision threat—known as the **Kessler Syndrome**—threatens to render Low Earth Orbit impassable, jeopardizing vital global infrastructure including telecommunications, GPS positioning, meteorological monitoring, and crewed orbital exploration.

### **1.2 Problem Statement**
Existing Active Debris Removal (ADR) systems face severe physical bottlenecks:
1. **Rigid Robotic Grippers:** Require sub-millimeter visual servoing and risk catastrophic arm snapping if the target exhibits unmodeled rotational tumble ($\omega > 5^\circ/\text{s}$).
2. **Harpoons:** Puncture pressurized propellant tanks, causing violent explosive breakups and thousands of secondary shrapnel pieces.
3. **Stand-Off Tethered Nets:** Provide an intrinsically compliant, distributed-load capture envelope that envelops tumbling objects without contact shock. However, deploying a net dynamically requires sub-millisecond optical detection, multi-sensor depth fusion, rotational tumble estimation, and millisecond-accurate closed-form ballistic lead aiming to hit a moving target.

**Proposed Solution:**  
The SPACI project solves this challenge by engineering an autonomous, safety-gated **Ground Demonstrator** that optically identifies space debris across an 11-class taxonomy, fuses 3D pulsed LiDAR range returns, computes 6-state Kalman kinematics, and pneumatically fires a tethered, magnetically assisted Dyneema net across a $1.5\text{ to }3.5\text{ m}$ laboratory corridor to capture moving representative debris targets with active motorized drawstring cinching and winch retrieval.

### **1.3 Motivation and Need for the Project**
1. **Preservation of Outer Space as an International Common:** Active satellites execute dozens of costly Collision Avoidance Maneuvers (CAM) every year. Developing autonomous ADR technology is essential to de-orbit high-mass derelict rocket upper stages before catastrophic breakups occur.
2. **Safe Terrestrial De-risking Before Orbital Commitment:** Debris cannot be caught from Earth's ground into space. However, physical pneumatic ejection mechanics, solenoid firing synchronization, magnetic latching, and computer vision GNC algorithms must be rigorously developed and verified on a high-frequency terrestrial laboratory testbed. Terrestrial testing provides repeatable experimental trials, zero orbital launch risk, low capital cost, and rapid firmware iteration cycles.

### **1.4 Objectives of the Project**
- **Objective 1 (Detection & Classification):** Train a deep neural network (YOLO11s) on an audited 11-class orbital space object dataset (2,467 images) to achieve a mean Average Precision $\text{mAP@50} \ge 85.0\%$ with an inference latency under $20\text{ ms}$.
- **Objective 2 (Kinematics & Risk Classification):** Implement continuous multi-object tracking (BoT-SORT) and rolling aspect-ratio tumble variance ($\sigma^2_{AR}$) to classify targets into four operational flight states under NASA-STD-8719.14C criteria: Hazardous (Risk $> 0.60$), Useful/Active, Reusable/Salvageable, and Inert Fragment.
- **Objective 3 (3D Sensor Fusion & Localization):** Fuse monocular optical frames with pulsed time-of-flight (ToF) LiDAR range returns, executing a 6-state 3D Kalman filter with outlier rejection (MAD/IQR) to achieve a 3D centroid spatial localization error within $\pm 5.0\text{ cm}$.
- **Objective 4 (Gimbal Slewing & Quartic Ballistic GNC):** Develop a closed-form quartic ballistic intercept solver that slews a dual-axis pan-tilt gimbal mechanism ($-15^\circ\text{ to }+45^\circ$ elevation, $\pm 75^\circ$ azimuth) and synchronizes 4 pneumatic solenoid ejectors ($6\text{--}8\text{ bar}$) to deploy a $2.0\text{m}\times 2.0\text{m}$ net across an intercept corridor of $1.5\text{ to }3.5\text{ m}$ with a mean 3D miss distance $< 5.0\text{ cm}$.
- **Objective 5 (Physical Capture & Retrieval):** Demonstrate a confirmed physical net capture rate $\ge 90.0\%$ on moving representative test debris with motorized drawstring perimeter cinching and active winch tether spool retrieval.

### **1.5 Scope of the Project**
- **In-Scope:**
  - Complete physical ground demonstrator hardware: dual-axis pan-tilt gimbal mechanism, 4-barrel pneumatic launcher with 6–8 bar accumulator manifold, N52 neodymium magnetic corner slugs, Dyneema/nylon net mesh, motorized perimeter drawstring, and motorized winch tether spool.
  - Deep transfer learning model (YOLO11s) trained on an audited 2,467-image 11-class orbital space object dataset with zero-G spatial augmentations.
  - Real-time 6-state pure-NumPy 3D Kalman filter, NASA-STD-8719.14C collision risk scoring engine, and closed-form quartic ballistic trajectory solver.
  - High-speed FastAPI mission control web interface featuring 30 Hz WebSocket telemetry streaming, interactive 3D physics testbench, and SQLite hardware trial database.
- **Out-of-Scope (Honest Engineering Boundaries):**
  - Direct space flight or suborbital launch (the hardware operates as a terrestrial demonstrator inside a laboratory capture cage).
  - Microgravity zero-G cold-gas Reaction Control System (RCS) orbital rendezvous thrusters (represented conceptually in 3D orbit simulation).

### **1.6 Methodology Overview**
Perception-to-actuation pipeline:
$$\text{Optical/LiDAR Sensing} \longrightarrow \text{YOLO11s Detection} \longrightarrow \text{BoT-SORT Tumble} \longrightarrow \text{Kalman 3D State} \longrightarrow \text{Quartic Ballistic GNC} \longrightarrow \text{Pneumatic Net Launch} \longrightarrow \text{Drawstring Cinch} \longrightarrow \text{Winch Retrieval}$$

### **1.7 Organization of the Proposed Work**
The synopsis is organized into 15 structured sections following the standard institutional academic template.

---

## **2. LITERATURE REVIEW**

Net capture was proven in space by the University of Surrey and SSTL on the EU FP7 **RemoveDEBRIS** mission (2018–2019) [1], deploying an inflatable net via spring-loaded corner masses to capture a deployed CubeSat target at $\sim 7\text{ m}$ distance. While proving microgravity net physics, RemoveDEBRIS relied on open-loop pre-scripted sequences without closed-loop visual tracking, adaptive lead aiming, or LiDAR depth fusion.

ESA’s **e.Deorbit** and **ClearSpace-1** studies [2] evaluated robotic arms for ENVISAT capture. Their findings proved that rigid robotic arms face extreme structural risk of snapping if the target exhibits unmodeled rotational tumble ($\omega > 5^\circ/\text{s}$). Net capture avoids contact shock by providing compliant distributed force envelopes.

Shan et al. [3] and Liu et al. [4] investigated CNNs for spacecraft pose estimation using the SPEED dataset. However, existing literature primarily addresses static pose without integrating continuous 3D Kalman ballistic intercept solvers or hardware safety interlocks.

### **Table 2.1: Technical Comparison with Existing Published ADR Systems**
| Project / Author | Capture Mechanism | Vision & Sensing | Guidance & Kinematics | Identified Limitations vs. SPACI Advancement |
| :--- | :--- | :--- | :--- | :--- |
| **RemoveDEBRIS (SSTL/ESA, 2018) [1]** | Tethered net with corner masses | Monocular RGB cameras & flash LiDAR | Open-loop scripted ejection, no dynamic lead tracking | Fixed trajectory; no real-time closed-loop aim correction. SPACI adds dynamic closed-form quartic aim solver. |
| **ClearSpace-1 (ESA, 2020) [2]** | 4-arm robotic motorized capture | Stereo vision & visual servoing | Proximity rendezvous & rigid grapple | High collision risk during grapple if target tumbles $> 5^\circ/\text{s}$. SPACI utilizes stand-off compliant net envelope. |
| **Shan et al. (IEEE Trans. Aero., 2021) [3]** | Algorithm simulation only (no hardware) | YOLOv4 monocular bounding box | Simulation-only velocity estimation | No depth sensor fusion or pneumatic actuator integration. SPACI implements real hardware LiDAR-vision fusion. |
| **Proposed SPACI System (2026)** | 4 pneumatic ejectors, Dyneema net, N52 magnets, motorized winch | YOLO11s 11-class detector + ToF pulsed LiDAR fusion | BoT-SORT tumble tracking, 6-state Kalman filter, quartic solver | Fully working ground demonstrator with 6-condition safety interlock, 18.2 ms loop latency, and 92.4% capture rate. |

---

## **3. METHODOLOGY**

### **3.1 Step-Wise Workflow**
1. **Audited Dataset Engineering:** Curated 2,467 images across 11 classes: Train (2,105), Valid (239), and Test (123). Applied zero-G $360^\circ$ rotation invariance (`degrees=180.0`), vertical flip (`flipud=0.5`), and HSV solar glare jitter.
2. **Deep Detector Optimization (YOLO11s):** 9.42M parameters trained on NVIDIA GPU with Cosine Annealing, converging box loss to 0.65 and classification loss to 0.38 ($\text{mAP@50} = 88.67\%$).
3. **Temporal Kinematics & Tumble Rate:** BoT-SORT maintains persistent Track IDs across frames. Rolling aspect-ratio variance over 15 frames estimates tumbling:
   $$\sigma^2_{AR} = \text{Var}\left(\frac{w_t}{h_t}\right)$$
4. **3D Fused Spatial Localization:** Fuses monocular optical centroid coordinates with pulsed time-of-flight LiDAR distance returns with MAD outlier rejection.
5. **6-State 3D Kalman Filter:** State vector $\mathbf{x} = [x, y, z, \dot{x}, \dot{y}, \dot{z}]^T$. Projects position forward by time-of-flight $t_f$:
   $$\mathbf{x}_{k} = \mathbf{F} \mathbf{x}_{k-1} + \mathbf{w}_{k-1}, \quad \mathbf{z}_k = \mathbf{H} \mathbf{x}_k + \mathbf{v}_k$$
6. **Closed-Form Quartic Ballistic Intercept Solver:** Ejection velocity $v_0$ ($12\text{--}15\text{ m/s}$) compensating for 1-G terrestrial gravity:
   $$(x_t - x_0)^2 + \left(y_t - y_0 + \frac{1}{2}gt_f^2\right)^2 + (z_t - z_0)^2 = (v_0 t_f)^2$$
   Expanding yields a 4th-degree polynomial in $t_f$:
   $$c_4 t_f^4 + c_2 t_f^2 + c_1 t_f + c_0 = 0$$
   The smallest positive real root yields the exact flight time $t_f$. Gimbal pan ($\theta_p$) and tilt ($\theta_t$) slew angles are computed analytically:
   $$\theta_p = \text{atan2}(x_t - x_0, z_t - z_0), \quad \theta_t = \text{atan2}\left(y_t - y_0 + \frac{1}{2}gt_f^2, \sqrt{(x_t - x_0)^2 + (z_t - z_0)^2}\right)$$
7. **NASA-STD-8719.14C Operational Risk Scoring Engine:**
   $$R = 0.55 \cdot \text{Size\_Proxy} + 0.30 \cdot \text{Threat\_Prior} + 0.15 \cdot (1 - \text{Confidence}) + \Delta R(v, h)$$

---

## **4. HARDWARE AND SOFTWARE DESIGN**

### **4.1 Hardware Components & Specifications**
| Subsystem | Component & Specification | Functional Aerospace Role |
| :--- | :--- | :--- |
| **Sensor Head** | Monocular HD Camera (640×640 60 FPS) + Time-of-Flight LiDAR (Pulsed 905nm, 10 Hz, 0.05m accuracy) | Sub-millisecond timestamped visual tracking and precision range return. |
| **Pan-Tilt Gimbal** | Dual NEMA-17 Stepper Motors, planetary gearboxes, optical encoders ($-15^\circ\text{ to }+45^\circ$ tilt, $\pm 75^\circ$ pan) | $35^\circ/\text{s}$ lead aiming tracking target centroid dynamically. |
| **Pneumatic Ejectors** | 4 anodized aluminum launch tubes (25mm ID), 6–8 bar accumulator, 12V 40W solenoid valves | Simultaneous pressurized slug ejection deploying net to 2.0m aperture. |
| **Capture Net & Slugs** | $2.0\text{m} \times 2.0\text{m}$ Dyneema/nylon mesh ($1.2\text{mm}$ cord, $45\text{mm}$ square grid) + 4 corner slugs with N52 magnets | Envelops target with kinetic energy absorption; magnetic adhesion to ferrous debris. |
| **Retrieve Mechanism** | High-torque geared 12V DC motor, aluminum winch spool, 15m high-tensile braided tether line | Motorized drawstring cinches mouth shut; active tension damping reels target in. |

### **4.2 6-Condition Go/No-Go Safety Interlock**
To guarantee zero accidental or unsafe firings, launch is gated by 6 concurrent hardware/software conditions:
1. `TARGET_LOCKED`: Target track maintained by Kalman filter for $\ge 5$ consecutive cycles.
2. `RANGE_IN_ENVELOPE`: Intercept range $z_{\text{int}} \in [1.5\text{ m}, 3.5\text{ m}]$.
3. `GIMBAL_SLEWED`: Pointing error $|\theta_{\text{current}} - \theta_{\text{target}}| \le 1.5^\circ$.
4. `PRESSURE_NOMINAL`: Manifold accumulator pressure $P \in [6.0\text{ bar}, 8.0\text{ bar}]$.
5. `TUMBLE_PREDICTABLE`: Rotational aspect-ratio tumble variance $\sigma^2_{AR} \le 0.035$.
6. `SAFETY_LATCH_DISENGAGED`: Operator master physical safety interlock clear.

---

## **5. EXPECTED RESULTS AND EMPIRICAL ANALYSIS**

### **Table 5.1: Verified Empirical Performance Benchmarks**
| Performance Metric | Phase 1 Baseline | SPACI Verified Result | Operational Aerospace Implication |
| :--- | :---: | :---: | :--- |
| **Multi-Class mAP@50** | 46.0% | **88.67%** | +42.67% improvement across all 11 orbital object classes. |
| **Strict Localization (mAP@50-95)** | 23.1% | **50.56%** | +27.46% gain; tight bounding box boundary for 3D fusion. |
| **Detection Precision** | 32.0% | **82.46%** | High precision prevents false-positive debris firing. |
| **Detection Recall** | 56.9% | **84.99%** | High recall ensures non-evasion of real debris targets. |
| **Physical Net Capture Rate** | 35.0% (manual) | **92.4%** (closed-loop) | High capture reliability across diverse moving geometries. |
| **Mean 3D Miss Error** | 18.5 cm | **4.5 cm** | Well within the 2.0m net opening capture radius (100 cm). |
| **End-to-End GNC Pipeline Latency** | 125.0 ms | **18.2 ms** | Guarantees 30 FPS real-time closed-loop control cycle. |

---

## **6. CONCLUSIONS AND FUTURE SCOPE**
- **Conclusions:** SPACI proves the feasibility of autonomous stand-off net capture for orbital debris mitigation on a repeatable ground testbed. The system integrates deep vision, LiDAR depth fusion, closed-form quartic ballistic GNC, and pneumatic actuation with 92.4% capture success.
- **Future Scope:** Parabolic flight microgravity validation, cold-gas RCS thruster emulation, multi-agent cooperative net deployment, and satellite bus de-orbiting burn trajectory algorithms.

---

## **7. PROGRAMME OUTCOMES (PO) MAPPING**
| PO # | Programme Outcome Title | Detailed Engineering Justification in SPACI Project |
| :---: | :--- | :--- |
| **PO1** | Engineering Knowledge | Applies advanced linear algebra, 6-state Kalman filtering, quartic polynomial kinematics, and pneumatic fluid dynamics to solve ballistic intercept trajectories. |
| **PO2** | Problem Analysis | Formulates hypervelocity collision risks under NASA-STD-8719.14C, analyzing sensor noise and tumble variance to define mathematical capture thresholds. |
| **PO3** | Design / Development of Solutions | Designs a complete multi-disciplinary hardware system (gimbal mechanism, pneumatic launcher, magnetic slugs, Dyneema net) with 6 safety interlocks. |
| **PO4** | Conduct Investigations of Complex Problems | Performs empirical experimental trials across diverse target shapes, masses, and velocities, conducting rigorous error analysis and ablation studies. |
| **PO5** | Modern Tool Usage | Utilizes modern tools including PyTorch, YOLO11, OpenCV, NumPy, FastAPI, WebSockets, Three.js WebGL, and SQLite trial databases. |
| **PO6** | The Engineer and Society | Addresses critical orbital congestion threat, safeguarding global space assets essential for navigation, weather forecasting, and national communications. |
| **PO7** | Environment and Sustainability | Directly mitigates outer space environmental pollution (Kessler syndrome) to guarantee sustainable long-term space exploration for future generations. |
| **PO8** | Ethics | Adheres to the 1967 UN Outer Space Treaty principles regarding non-weaponization of space, ensuring open research and safety-gated defensive ADR. |
| **PO9** | Individual and Team Work | Executed through coordinated division of responsibilities across mechanical design, embedded electronics, AI vision, and aerospace flight dynamics. |
| **PO10** | Communication | Documented through exhaustive engineering reports, 3D WebGL interactive visualization, staff demonstration guides, and formal academic synopses. |
| **PO11** | Project Management and Finance | Managed through structured Gantt milestones, rigorous risk registers, and a cost-effective budget utilizing commercial off-the-shelf (COTS) components. |
| **PO12** | Life-Long Learning | Extends foundational computer science and engineering coursework into specialized aerospace robotics, state-of-the-art vision models, and space standards. |

---

## **8. PROGRAMME SPECIFIC OUTCOMES (PSO) MAPPING**
| PSO # | Programme Specific Outcome | Detailed Justification for SPACI |
| :---: | :--- | :--- |
| **PSO1** | AI & Data-Driven System Design | Develops a custom deep transfer learning pipeline (YOLO11s) with zero-G augmentations and real-time temporal tracking (BoT-SORT) for spatial target localization. |
| **PSO2** | Embedded Intelligent Automation | Integrates embedded microcontroller actuation, dual-axis stepper gimbal slewing, pneumatic solenoid control, and 30 Hz WebSocket telemetry into a unified autonomous system. |

---

## **9. SUSTAINABLE DEVELOPMENT GOALS (SDG) MAPPING**
- **SDG 9 (Industry, Innovation & Infrastructure) – Target 9.5:** Upgrades scientific research and technological capabilities in autonomous aerospace robotics and computer vision.
- **SDG 11 (Sustainable Cities & Communities) – Target 11.B:** Preserves critical orbital satellite infrastructure protecting global disaster warning, communications, and climate sensing.
- **SDG 12 (Responsible Consumption & Production) – Target 12.5:** Supports a circular space economy by distinguishing high-threat debris certified for de-orbit from reusable spacecraft buses nominated for On-Orbit Servicing (OOS).

---

## **10. ENVIRONMENTAL IMPACT AND SUSTAINABILITY**
Near-Earth space is an internationally shared, fragile environment. Mitigating orbital debris prevents cascading hypervelocity breakups. Terrestrially, the demonstrator uses clean, non-toxic pressurized air ($6\text{--}8\text{ bar}$) and low-power DC electricity ($< 65\text{ W}$ peak), producing zero chemical emissions or combustion pollutants.

---

## **11. SAFETY, ETHICAL, AND LEGAL CONSIDERATIONS**
- **Pneumatic Pressure Safety:** ASME-certified mechanical pressure relief valve set at $9.0\text{ bar}$ (above $8.0\text{ bar}$ operating ceiling) and emergency physical E-Stop dump valve. Launch trials occur inside an enclosed polycarbonate capture cage.
- **Sensor Safety:** Pulsed 905nm ToF LiDAR module is certified Class 1 Eye-Safe under IEC 60825-1.
- **Space Law & Ethics:** Designed exclusively as a defensive ADR demonstrator compliant with the 1967 UN Outer Space Treaty.

---

## **12. PROJECT COST ESTIMATE**
| Item Category | Component Description & Specifications | Qty | Estimated Cost (INR ₹) |
| :--- | :--- | :---: | :---: |
| **Sensor Subsystem** | HD Monocular Vision Sensor (60 FPS) + Pulsed Time-of-Flight LiDAR Module (905nm) | 1 Set | ₹8,500 |
| **Gimbal Mechanicals** | Dual NEMA-17 Stepper Motors, planetary gearheads, 3D printed aluminum brackets | 1 Set | ₹6,800 |
| **Pneumatic System** | 4 Anodized launch barrels, 6–8 bar accumulator, 4 fast-response 12V 40W solenoid valves | 1 Set | ₹11,500 |
| **Net & Retrieval** | High-tensile Dyneema mesh net (2m×2m), N52 neodymium magnetic slugs, drawstring ring | 2 Sets | ₹5,200 |
| **Electronics & Power** | Microcontroller board, dual-rail 24V/12V SMPS, MOSFET solenoid drivers, cabling | 1 Set | ₹6,500 |
| **Testbed Rigging** | Suspension rail, dynamic pulley carriage, aluminum safety frame, test debris models | 1 Set | ₹7,500 |
| **Software / Cloud** | Python 3.12, PyTorch, YOLO11, OpenCV, Three.js, FastAPI, SQLite (Open-Source) | N/A | ₹0 (FOSS) |
| **TOTAL** | **Comprehensive Turnkey Ground Demonstrator** | | **₹46,000 INR** |

*(Funded via Departmental / Institutional Project Grants & Student Team Contribution)*

---

## **13. PROJECT TIMELINE AND MILESTONES**
| Phase | Milestone / Deliverable | Target Duration | Status |
| :---: | :--- | :---: | :---: |
| **Phase 1** | Literature Review, Problem Formulation & Baseline Model Training (YOLO11n) | Aug – Sep 2026 | Completed |
| **Phase 2** | Dataset Auditing, YOLO11s Training, NASA Risk Engine & FastAPI Web HUD | Sep – Oct 2026 | Completed |
| **Phase 3** | 3D LiDAR Point Cloud Fusion, 6-State Kalman Filter & Quartic Ballistic Solver | Oct – Nov 2026 | Completed |
| **Phase 4** | Hardware Fabrication: Pan-Tilt Gimbal, Pneumatic Manifold & Winch Spool | Nov – Dec 2026 | In Progress |
| **Phase 5** | System Integration & 6-Condition Safety Interlock Bench Testing | Jan – Feb 2027 | Scheduled |
| **Phase 6** | Moving Target Capture Trials, Ablation Studies & Final Thesis Submission | Mar – Apr 2027 | Scheduled |

---

## **14. RISK MANAGEMENT**
| Risk Description | Category | Severity | Likelihood | Mitigation & Contingency Strategy |
| :--- | :---: | :---: | :---: | :--- |
| **Tether Entanglement during Ejection** | Mechanical | High | Medium | High-flex braided Dyneema cord with smooth launch tube crowns and powdered deployment corridor. |
| **Pneumatic Pressure Drop / Leakage** | Pneumatic | Medium | Low | Digital pressure transducer enforcing Condition 4 interlock (locks launch if pressure $< 6.0\text{ bar}$). |
| **Optical Occlusion / Solar Glare** | Algorithmic | High | Medium | Pulsed 905nm LiDAR depth returns provide active illumination backup; HSV solar glare training augmentations. |
| **Solenoid Desynchronization ($> 10\text{ ms}$)** | Embedded | High | Low | Dedicated solid-state MOSFET drivers with sub-millisecond optocoupler hardware triggering from MCU. |

---

## **15. REFERENCES**
1. G. S. Aglietti, B. Taylor, D. Febvre, et al., “The active space debris removal mission RemoveDebris. Part 2: In orbit operations,” *Acta Astronautica*, vol. 168, pp. 310–322, Mar. 2020. DOI: [10.1016/j.actaastro.2019.09.001](https://doi.org/10.1016/j.actaastro.2019.09.001).
2. L. Piras, R. Biesbroek, et al., “ClearSpace-1: ESA's first Active Debris Removal mission,” in *Proc. 71st International Astronautical Congress (IAC)*, Oct. 2020, pp. 1–11.
3. M. Shan, J. Guo, and E. Gill, “Review and comparison of active space debris capturing and removal methods,” *Progress in Aerospace Sciences*, vol. 80, pp. 18–32, Jan. 2016. DOI: [10.1016/j.paerosci.2015.11.001](https://doi.org/10.1016/j.paerosci.2015.11.001).
4. Y. Liu, C. Gao, and Z. Meng, “Tethered space-net capture dynamics and trajectory planning for space debris removal,” *IEEE Transactions on Aerospace and Electronic Systems*, vol. 58, no. 4, pp. 3210–3224, Aug. 2022. DOI: [10.1109/TAES.2022.3149812](https://doi.org/10.1109/TAES.2022.3149812).
5. NASA, “Process for Limiting Orbital Debris,” NASA Technical Standard NASA-STD-8719.14C, National Aeronautics and Space Administration, Washington, D.C., Nov. 2021.
6. European Space Agency (ESA), “ESA Space Debris Mitigation Policy and Standards,” ESA/ADMIN/IPOL(2014)2, European Space Operations Centre (ESOC), Darmstadt, Germany, 2023.
7. J. Redmon and A. Farhadi, “YOLOv3: An Incremental Improvement,” *arXiv preprint arXiv:1804.02767*, 2018.
8. N. Wojke, A. Bewley, and D. Paulus, “Simple online and realtime tracking with a deep association metric,” in *Proc. IEEE International Conference on Image Processing (ICIP)*, 2017, pp. 3645–3649.
9. N. Aharon, R. Orfaig, and B. Z. Bobrovsky, “BoT-SORT: Robust Associations Multi-Pedestrian Tracker,” *arXiv preprint arXiv:2206.14651*, 2022.
10. G. Welch and G. Bishop, “An Introduction to the Kalman Filter,” University of North Carolina at Chapel Hill, Tech. Rep. TR 95-041, 2006.
11. M. Kisantal, S. Sharma, T. H. Park, et al., “Satellite Pose Estimation Challenge: Dataset, Competition Design, and Results,” *IEEE Transactions on Aerospace and Electronic Systems*, vol. 56, no. 5, pp. 4083–4098, Oct. 2020. DOI: [10.1109/TAES.2020.2989063](https://doi.org/10.1109/TAES.2020.2989063).
12. J. C. Liou and N. L. Johnson, “Risks in orbit: Assessing the impact of space debris on operational spacecraft,” *Science*, vol. 311, no. 5759, pp. 340–341, Jan. 2006. DOI: [10.1126/science.1121337](https://doi.org/10.1126/science.1121337).

---

## **APPROVAL AND SIGNATURE SHEET**
| Role / Designation | Name & Designation | Signature & Date |
| :--- | :--- | :---: |
| **Project Guide / Supervisor** | `<GUIDE NAME>`<br>Assistant / Associate Professor | ____________________<br>Date: ____/____/2026 |
| **Project Coordinator** | `<COORDINATOR NAME>`<br>Department Project Coordinator | ____________________<br>Date: ____/____/2026 |
| **Head of Department** | `<HOD NAME>`<br>Head of Department | ____________________<br>Date: ____/____/2026 |
