import os

def create_be_report_tex():
    tex_content = r'''%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\documentclass[12pt]{report}

\setlength{\textwidth}{6.25in}
\setlength{\textheight}{8in}
\renewcommand{\baselinestretch}{1.3}
\oddsidemargin 20pt
\evensidemargin 20pt
\topmargin 0pt
\newcommand{\squeezeup}{\vspace{-0.6cm}}
\renewcommand*\contentsname{INDEX}

% Packages
\usepackage{amssymb}
\usepackage{amsmath}
\usepackage{subfigure}
\usepackage{algorithmic}
\usepackage{algorithm}
\usepackage{graphics}
\usepackage{epsfig}
\usepackage{listing}
\usepackage{graphicx}
\usepackage{titlesec}
\usepackage{url}
\usepackage{fancyhdr}
\usepackage{float}
\usepackage{fancybox}
\usepackage{xcolor}
\usepackage[left=3.81cm,top=2.54cm,right=2.54cm,bottom=3.175cm]{geometry}
\usepackage{pdfpages}
\usepackage[font=normalsize,labelfont=bf]{caption}
\usepackage[]{hyperref}
\usepackage[intoc]{nomencl}

\makeindex

% Title Formatting
\titleformat{\chapter}[display]
  {\normalfont\large\bfseries\centering}{\chaptertitlename\ \thechapter}{14pt}{\large}
\titleformat{\section}{\normalsize \bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalsize \bfseries}{\thesubsection}{1em}{}

\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%	
% Title Page
\begin{titlepage}   
    \thisfancypage{\setlength{\fboxsep}{10pt}\doublebox}{}
    \begin{center}
    \begin{figure*}[h]
    \centerline{\includegraphics[width=5.4in,height=1.0in]{figures/IOIT_logo1.jpg}}
    \end{figure*}
    { \bf { PRELIMINARY PROJECT REPORT ON}}\\
    \vspace{0.15in}
    {\Large \bf {``SPACI: DEEP LEARNING-BASED AUTONOMOUS SPACE DEBRIS MULTI-CLASS DETECTION, ORBITAL VIDEO KINEMATIC TRACKING, AND COLLISION RISK ASSESSMENT SOFTWARE SYSTEM''}}
    \\
    \vspace{0.15in}
    {\small (SDG \#9 – Industry, Innovation \& Infrastructure | SDG \#11 – Sustainable Outer Space Communities | SDG \#12 – Responsible Circular Space Economy)}\\
    \vspace{0.15in}
    {\small SUBMITTED TO THE SAVITRIBAI PHULE PUNE UNIVERSITY, PUNE \\ IN PARTIAL FULFILLMENT OF THE REQUIREMENTS \\ FOR THE AWARD OF THE DEGREE OF }\\
    \vspace{0.1in}
    {\bf BACHELOR OF TECHNOLOGY}\\
    {\bf (ARTIFICIAL INTELLIGENCE \& DATA SCIENCE / COMPUTER ENGINEERING)}\\
    \vspace{0.15in}
    {\bf SUBMITTED BY}\\
    \vspace{0.1in}
    {\small  
    Mr. Deep Ravindra Kale \hspace*{1.1 in} Exam Seat No: <Seat No> \\
    Mr. <Student Name 2> \hspace*{1.3 in} Exam Seat No: <Seat No 2> \\
    Mr. <Student Name 3> \hspace*{1.3 in} Exam Seat No: <Seat No 3> \\
    }
    \vspace{0.15in}
    {\bfseries \fontsize{12}{12} \selectfont Under The Guidance of \\} 
    \vspace*{0.05in}
    {\bf <GUIDE NAME>}\\[2mm]
    {\small Assistant Professor / Associate Professor}
    \begin{figure*}[h]
    \centerline{\includegraphics[width=1.4in,height=1.3in]{figures/aissmsioitlogo.png}}
    \end{figure*}
    { \bf{ DEPARTMENT OF ARTIFICIAL INTELLIGENCE \& DATA SCIENCE / COMPUTER ENGINEERING}}\\ 
    \vspace{0.05in}
    { \bf AISSMS INSTITUTE OF INFORMATION TECHNOLOGY }\\ 
    {\small KENNEDY ROAD, NEAR R.T.O., PUNE – 411001 }\\ 
    \vspace{0.05in}	
    { \bf \small { ACADEMIC YEAR: 2026–2027}}\\
    \end{center}
\end{titlepage}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Certificate Page
\thisfancypage{\setlength{\fboxsep}{10pt}\doublebox}{}	
\begin{titlepage} 
    \begin{center} 
    \begin{figure*}[h]
        \centerline{\includegraphics[width=5.4in,height=1.0in]{figures/IOIT_logo1.jpg}}
        \par\noindent\rule{\textwidth}{0.4pt}
    \end{figure*}
    \vspace{0.1in}
    {\large\textbf{CERTIFICATE}}\\
    \vspace{0.1in}
    {\small This is to certify that the project report entitled \\}
    {\bf \large {``SPACI: DEEP LEARNING-BASED AUTONOMOUS SPACE DEBRIS MULTI-CLASS DETECTION, ORBITAL VIDEO KINEMATIC TRACKING, AND COLLISION RISK ASSESSMENT SOFTWARE SYSTEM''}}\\
    \vspace{0.1in}
    Submitted by \\ 	
    {\small  
    Mr. Deep Ravindra Kale \hspace*{1.1 in} PRN: 72312016B \\
    Mr. <Student Name 2> \hspace*{1.3 in} PRN: <PRN No 2> \\
    Mr. <Student Name 3> \hspace*{1.3 in} PRN: <PRN No 3> 
    }
    \end{center}
    \vspace{0.1in}
    {\small is a bonafide student of this institute and the work has been carried out by them under the supervision of {\bf <GUIDE NAME>} and it is approved for the partial fulfillment of the requirement of Savitribai Phule Pune University, for the award of the degree of {\bf Bachelor of Technology} (Artificial Intelligence \& Data Science / Computer Engineering). }\\

    \vspace*{0.3in}
    \hspace*{0.2in} {\bf (<GUIDE NAME>) } \hspace*{1.5in}{\bf (Dr. Sarika Zaware / Dr. K.S. Wagh)}\\
    \hspace*{0.5in}Guide \hspace*{3.0 in} Head\\
    \hspace*{0.0in}{Dept. of AIDS / Computer Engg.} \hspace*{0.9 in}{Dept. of AIDS / Computer Engg.}\\
    \vspace*{0.2in}\\
    \hspace*{0.5in}{AISSMS Institute of Information Technology, Pune-411001}\\
    \vspace*{0.1in}\\
    \hspace*{0.2in}{Place: PUNE}\\
    \hspace*{0.2in}Date:
\end{titlepage}

\pagenumbering{roman}

% Abstract
\addcontentsline{toc}{chapter}{Abstract}
\chapter*{ABSTRACT}
Low Earth Orbit (LEO, 200--2,000 km altitude) is experiencing exponential congestion from defunct satellite buses, spent rocket booster tanks, and hypervelocity fragmentation debris. According to the European Space Agency (ESA) Space Debris Office DISCOS database, over 47,000 tracked objects and an estimated 1.5 million hazardous untracked fragments larger than 1 cm travel at relative velocities exceeding 7.5 to 10 km/s. Under NASA Technical Standard NASA-STD-8719.14C, any orbital collision delivering kinetic energy exceeding 40 J/g of target mass triggers catastrophic fragmentation, escalating the cascading Kessler Syndrome.

This project develops SPACI, a high-performance software system engineered for autonomous multi-class space debris detection, kinematic video tracking, and operational collision risk assessment. The system comprises five integrated software components: (1) An audited 11-class orbital space object dataset (2,467 images) incorporating microgravity 360-degree rotation invariance and solar glare data augmentations; (2) A YOLO11s deep convolutional neural network fine-tuned via transfer learning, achieving 88.67\% mAP@50 and 82.46\% precision at 11.5 ms GPU latency (~87 FPS); (3) BoT-SORT temporal multi-object tracking coupled with rolling aspect-ratio variance ($\sigma^2_{AR}$) over a 15-frame sliding window to estimate attitude tumbling rate; (4) A NASA-STD-8719.14C kinetic risk scoring engine that dynamically categorizes objects into four operational flight states: Hazardous (CAM trigger), Useful/Active, Reusable/Salvageable, and Inert Fragment; and (5) A 6-state 3D Kalman filter with pulsed ToF LiDAR distance fusion and closed-form quartic ballistic trajectory guidance. The entire pipeline is deployed on an asynchronous FastAPI REST server paired with atomic 30 Hz WebSockets and an interactive dark glassmorphic Mission Control web HUD.

\vspace{0.2in}
\noindent \textbf{Keywords:} Space Debris Detection, YOLO11s, BoT-SORT Temporal Tracking, NASA-STD-8719.14C, Kinetic Collision Risk Engine, 3D Kalman Filter, FastAPI, WebSocket Telemetry HUD.

\newpage

% Acknowledgement
\addcontentsline{toc}{chapter}{Acknowledgement}
\chapter*{ACKNOWLEDGMENT}
It gives us immense pleasure in presenting this preliminary project report on \textbf{``SPACI: DEEP LEARNING-BASED AUTONOMOUS SPACE DEBRIS MULTI-CLASS DETECTION, ORBITAL VIDEO KINEMATIC TRACKING, AND COLLISION RISK ASSESSMENT SOFTWARE SYSTEM''}. The successful completion of this work required valuable guidance, technical infrastructure, and institutional support.

We express our sincere gratitude to our project guide \textbf{<GUIDE NAME>} for the continuous technical mentorship, constructive critiques, and constant encouragement throughout the research and software engineering phases. We also extend our heartfelt thanks to \textbf{Dr. Sarika Zaware} (Head of Department) for providing valuable departmental support and academic guidance.

We are profoundly grateful to our respected Principal \textbf{Dr. P.B. Mane} for his dynamic leadership and for providing state-of-the-art computational facilities and laboratory resources at AISSMS Institute of Information Technology, Pune.

\vspace{20mm} 
\begin{flushright}
\begin{minipage}{2.8 in}
\textbf{Mr. Deep Ravindra Kale}\\
\textbf{Mr. <Student Name 2>}\\
\textbf{Mr. <Student Name 3>}\\
(B.Tech AI \& DS / Computer Engineering)\\
AISSMS IOIT, Pune.
\end{minipage}
\end{flushright}

\newpage

% Index & Lists
\addcontentsline{toc}{chapter}{Index}
\tableofcontents
\newpage
\addcontentsline{toc}{chapter}{List of Figures}
\listoffigures
\newpage
\addcontentsline{toc}{chapter}{List of Tables}
\listoftables
\newpage

\pagenumbering{arabic}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 1: INTRODUCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{INTRODUCTION}
\section{Problem Definition}
Over six decades of orbital operations have populated Low Earth Orbit (LEO, 200--2,000 km altitude) with defunct satellites, spent rocket stages, and hypervelocity fragmentation debris. According to the European Space Agency (ESA) Space Debris Office DISCOS database, over 47,000 tracked objects and an estimated 1.5 million hazardous untracked fragments (> 1 cm) travel at velocities exceeding 7.5 to 10 km/s (approx. 27,000 km/h). Under NASA Technical Standard NASA-STD-8719.14C, any orbital collision delivering kinetic energy exceeding 40 Joules per gram of target mass triggers catastrophic fragmentation. This phenomenon---the Kessler Syndrome---threatens to render key orbital altitudes impassable, imperiling critical satellite telecommunications, navigation, and crewed orbital exploration.

\begin{figure}[h]
\centering
\includegraphics[width=5.2in]{figures/landing_hero.png}
\caption{Orbital Debris Congestion \& Hypervelocity Threat in Low Earth Orbit}
\label{fig:orbital_congestion}
\end{figure}

\section{Motivation}
Active satellites currently execute dozens of costly Collision Avoidance Maneuvers (CAM) annually. However, ground tracking via radar networks and Two-Line Element (TLE) ephemeris catalogs suffers from long observation latencies (hours to days), sensor blind spots, and an inability to estimate rotational tumbling rates. Autonomous Active Debris Removal (ADR) and Space Situational Awareness (SSA) vehicles require lightweight, onboard computer vision capable of detecting non-cooperative targets, maintaining persistent track identities through video streams, and evaluating operational kinetic collision risks in real time without human-in-the-loop delay.

\section{Project Scope (Software \& Computer Vision Focus)}
\textbf{Important Scope Definition:} This B.Tech engineering project focuses STRICTLY on the SOFTWARE, COMPUTER VISION, AND MATHEMATICAL MODELING components of the space debris mitigation challenge. Physical mechanical fabrication of pneumatic launch barrels, net ejector canisters, or physical satellite flight hardware is explicitly out of scope. The software suite ingests video sequences, lab webcams, and synthetic testbench feeds, delivering an end-to-end perception, tracking, risk assessment, and mission control platform.

\section{Objectives of the Project}
\begin{enumerate}
    \item \textbf{Dataset Engineering:} Curate, audit, and augment an 11-class orbital space object dataset (2,467 images) across train (2,105), valid (239), and test (123) splits with zero-G spatial rotations and solar glare jitter.
    \item \textbf{Deep Learning Detection:} Fine-tune a YOLO11s deep convolutional neural network via transfer learning, achieving multi-class mAP@50 $\ge$ 85.0\% and strict localization mAP@50-95 $\ge$ 50.0\% with an edge inference latency under 15 ms.
    \item \textbf{Kinematic Video Tracking:} Integrate BoT-SORT temporal tracking across orbital encounter video feeds and calculate rolling aspect-ratio variance ($\sigma^2_{AR}$) over a 15-frame window to measure rotational attitude tumbling.
    \item \textbf{NASA/ESA Collision Risk Engine:} Implement an operational collision risk engine based on NASA-STD-8719.14C kinetic thresholds, classifying targets into four operational flight states: Hazardous, Useful/Active, Reusable/Salvageable, and Inert Fragment.
    \item \textbf{3D Sensor Fusion \& GNC:} Formulate a pure-NumPy 6-state 3D Kalman filter with pulsed ToF LiDAR distance returns, executing a closed-form quartic ballistic lead solver and a 6-condition Go/No-Go safety interlock algorithm.
    \item \textbf{Real-Time Web Platform:} Engineer a full-stack Mission Control web interface using FastAPI and WebSockets (30 Hz) with dedicated per-tab KPI tracking grids, interactive sliders, and 1-click telemetry data export.
\end{enumerate}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 2: LITERATURE SURVEY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{LITERATURE SURVEY}
\section{Review of Existing Systems \& Related Work}
Kisantal et al. [1] established the Spacecraft Pose Estimation Dataset (SPEED), enabling benchmark competitions for Tango satellite pose estimation using ResNet backbones. Sharma and D'Amico [2] advanced pose regression using neural networks; however, these models are strictly constrained to single known satellite geometries and fail on unmodeled, tumbling debris fragments.

Redmon and Farhadi [3] introduced single-stage YOLO architectures. Recent iterations (YOLOv8 and YOLO11) introduce C3k2 cross-stage partial bottlenecks and anchor-free bounding box heads, significantly accelerating edge inference while improving small-object detection. Bewley et al. [4] developed SORT using Kalman state filtering and Hungarian matching. Wojke et al. [5] introduced DeepSORT to incorporate visual appearance embeddings. Recently, Aharon et al. [6] published BoT-SORT, which outperforms DeepSORT by integrating Camera Motion Compensation (CMC) and fused state vectors.

Liou and Johnson [7] and NASA Technical Standard NASA-STD-8719.14C [8] defined kinetic damage thresholds for hypervelocity orbital collisions. In published aerospace systems, however, risk scoring is computed in offline ground mainframes rather than inside streaming vision loops. SPACI addresses these limitations by uniting YOLO11s detection, BoT-SORT kinematics, and NASA-STD-8719.14C collision risk scoring into an end-to-end 30 Hz software pipeline.

\section{Summary Table of Existing Work}
\begin{table}[h]
\centering
\small
\begin{tabular}{|p{1.2in}|p{1.2in}|p{1.2in}|p{1.1in}|p{1.2in}|}
\hline
\textbf{Reference} & \textbf{Architecture} & \textbf{Tracking} & \textbf{Risk Engine} & \textbf{Identified Gap} \\ \hline
SPEED Pose [2] & ResNet-50 & None (Static) & None & Single satellite; fails on debris. \\ \hline
YOLOv8 Baseline & YOLOv8n & ByteTrack (2D) & None & Lacks zero-G rotation & risk rules. \\ \hline
DeepSORT Space [5] & YOLOv5+DeepSORT & DeepSORT & None & High latency (>35ms); no GNC. \\ \hline
\textbf{SPACI System} & \textbf{YOLO11s (Zero-G)} & \textbf{BoT-SORT ($\sigma^2_{AR}$)} & \textbf{NASA Kinetic} & \textbf{End-to-end 30Hz vision \& GNC.} \\ \hline
\end{tabular}
\caption{Technical Comparison with Existing Computer Vision SSA Systems}
\label{tab:lit_survey}
\end{table}

\section{Research Gap / Limitations in Existing Work}
\begin{enumerate}
    \item \textbf{Lack of Multi-Class Debris Generalization:} Prior space vision datasets model only single operational satellites. SPACI audits an 11-class taxonomy spanning operational satellites and irregular fragments.
    \item \textbf{Absence of Attitude Tumble Kinematics:} Existing detectors ignore rotational dynamics. SPACI introduces rolling aspect-ratio variance ($\sigma^2_{AR}$) to measure tumbling rates.
    \item \textbf{Decoupled Aerospace Safety Context:} Traditional detectors output unweighted bounding boxes. SPACI maps detections directly into NASA-STD-8719.14C operational flight rules.
\end{enumerate}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 3: SRS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{SOFTWARE REQUIREMENTS SPECIFICATION}
\section{Operating Environment}
The SPACI software platform executes across modern 64-bit operating systems (Microsoft Windows 11 / Ubuntu Linux 22.04 LTS). Deep learning inference leverages CUDA 12.1 and cuDNN on NVIDIA GPU architectures. The web service runs under Python 3.12 utilizing Uvicorn ASGI and FastAPI.

\section{Hardware and Software Requirements}
\begin{table}[h]
\centering
\small
\begin{tabular}{|l|l|l|}
\hline
\textbf{Hardware Component} & \textbf{Development Rig} & \textbf{Edge Deployment Target} \\ \hline
CPU & Intel Core i5 / AMD Ryzen 5 & NVIDIA Jetson Orin Nano (ARM Cortex) \\ \hline
GPU & NVIDIA RTX 3050 (8 GB VRAM) & 1024-Core NVIDIA Ampere (32 Tensor Cores) \\ \hline
RAM & 16 GB DDR4 3200 MHz & 8 GB LPDDR5 Unified Memory \\ \hline
Storage & 512 GB NVMe SSD & 64 GB eMMC 5.1 / NVMe \\ \hline
\end{tabular}
\caption{Hardware and Development Rig Specifications}
\label{tab:hw_specs}
\end{table}

\section{Functional & Non-Functional Requirements}
\begin{itemize}
    \item \textbf{FR1 (Multi-Class Optical Detection):} The software shall detect and classify objects into 11 taxonomy classes with confidence scores exceeding 0.25.
    \item \textbf{FR2 (Temporal Tracking):} The software shall assign persistent Track IDs across video frames via BoT-SORT camera motion compensation.
    \item \textbf{FR3 (Tumble Rate Estimation):} The software shall calculate rolling aspect-ratio variance ($\sigma^2_{AR}$) over 15-frame sliding windows.
    \item \textbf{FR4 (NASA Risk Scoring):} The software shall evaluate continuous collision risk scores and assign operational flight states.
    \item \textbf{FR5 (Telemetry Broadcasting):} The software shall serialize and broadcast 30 Hz JSON telemetry packets over WebSockets.
    \item \textbf{NFR1 (Performance):} Edge GPU forward pass inference latency shall not exceed 15 ms ($\ge$ 65 FPS).
    \item \textbf{NFR2 (Reliability):} Asynchronous WebSocket loop shall recover automatically from dropped network frames.
\end{itemize}

\section{Software Development Life Cycle (SDLC Model)}
The project follows an Iterative / Agile Engineering Model, enabling continuous dataset refinement, model hyperparameter tuning, and real-time dashboard optimization across sequential development sprints.

\begin{figure}[h]
\centering
\includegraphics[width=4.8in]{figures/sdlc_model.png}
\caption{Iterative / Agile Software Development Life Cycle (SDLC) Model}
\label{fig:sdlc}
\end{figure}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 4: SYSTEM DESIGN
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{SYSTEM DESIGN}
\section{System Architecture}
The software system is engineered as an asynchronous, non-blocking pipeline divided into four decoupled layers: Input Perception, AI Vision \& Kinematics, 3D GNC Guidance, and Web Control HUD.

\begin{figure}[h]
\centering
\includegraphics[width=5.4in]{figures/system_architecture.png}
\caption{SPACI End-to-End Software System Architecture}
\label{fig:sys_arch}
\end{figure}

\section{Data Flow (DFD) Diagrams}
\subsection{DFD Level 0 Diagram}
Level 0 DFD captures the context-level data flows between the Flight Dynamics Operator, Sensor Ingestion sources, the central SPACI Vision \& GNC System, and the SQLite Telemetry Database.

\begin{figure}[h]
\centering
\includegraphics[width=5.2in]{figures/dfd_level0.png}
\caption{Data Flow Diagram Level 0: Context Level Diagram}
\label{fig:dfd0}
\end{figure}

\subsection{DFD Level 1 Diagram}
Level 1 DFD decomposes the central system into six constituent processes: Ingest, YOLO11s Inference, BoT-SORT Tracking, 3D Kalman GNC, NASA Risk Engine, and WebSocket Streaming.

\begin{figure}[h]
\centering
\includegraphics[width=5.2in]{figures/dfd_level1.png}
\caption{Data Flow Diagram Level 1: Functional Decomposition}
\label{fig:dfd1}
\end{figure}

\section{UML Diagrams}
\subsection{UML Use Case Diagram}
\begin{figure}[h]
\centering
\includegraphics[width=4.8in]{figures/uml_usecase.png}
\caption{UML Use Case Diagram: Mission Control \& Autonomous Safety Watchdog}
\label{fig:uml_usecase}
\end{figure}

\subsection{UML Sequence Diagram}
\begin{figure}[h]
\centering
\includegraphics[width=4.8in]{figures/uml_sequence.png}
\caption{UML Sequence Diagram: Live Frame Ingestion, YOLO11s \& GNC Execution}
\label{fig:uml_seq}
\end{figure}

\subsection{UML Activity Diagram}
\begin{figure}[h]
\centering
\includegraphics[width=4.4in]{figures/uml_activity.png}
\caption{UML Activity Diagram: Perception-to-GNC Real-Time Execution Loop}
\label{fig:uml_act}
\end{figure}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 5: METHODOLOGY & MODELING
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{METHODOLOGY \& MATHEMATICAL MODELING}
\section{Dataset Engineering \& Zero-G Augmentation}
The dataset consolidates 2,467 images across 11 classes: Train (2,105), Valid (239), and Test (123). Automated audit scripts confirmed zero hash overlap between splits. To simulate microgravity, domain augmentations include 360-degree rotation invariance (`degrees=180.0`), vertical flip (`flipud=0.5`), and HSV solar glare jitter.

\begin{figure}[h]
\centering
\includegraphics[width=5.0in]{figures/eda_class_distribution.png}
\caption{11-Class Space Object Dataset Distribution Across Train, Valid, and Test Splits}
\label{fig:dataset_dist}
\end{figure}

\section{Deep Neural Network Architecture (YOLO11s)}
YOLO11s comprises 9.42M parameters and 21.5 GFLOPs. C3k2 cross-stage partial bottlenecks and Spatial Pyramid Pooling Fast (SPPF) extract multi-scale spatial features, while anchor-free heads predict bounding boxes and classification logits. Training utilized SGD with Cosine Annealing over 100 epochs on an NVIDIA GPU.

\section{BoT-SORT Kinematics \& Tumble Rate Estimation}
Over a sliding window of $W = 15$ frames, tracking aspect ratio $AR_t = w_t / h_t$:
$$\sigma^2_{AR} = \frac{1}{W} \sum_{i=1}^{W} \left(AR_i - \overline{AR}\right)^2$$
High variance signifies chaotic attitude tumbling, expanding the effective collision cross-section.

\begin{figure}[h]
\centering
\includegraphics[width=5.0in]{figures/annotated_video_frame.jpg}
\caption{BoT-SORT Kinematic Tracking and Aspect-Ratio Tumble Variance ($\sigma^2_{AR}$)}
\label{fig:video_tracking}
\end{figure}

\section{NASA-STD-8719.14C Kinetic Collision Risk Engine}
Continuous collision risk index $R \in [0.0, 1.0]$ is formulated as:
$$R = 0.55 \cdot \text{Size\_Proxy} + 0.30 \cdot \text{Threat\_Prior} + 0.15 \cdot (1.0 - \text{Confidence}) + \Delta R(v, h)$$
where Threat\_Prior is 0.85 for debris fragments and 0.30 for operational spacecraft. The risk score drives four operational flight states:
\begin{itemize}
    \item \textbf{HAZARDOUS (Risk > 0.60):} Trigger Collision Avoidance Maneuver (CAM) or arm net capture.
    \item \textbf{USEFUL / ACTIVE (Risk $\le$ 0.60):} Operational satellite payload; maintain safety corridor.
    \item \textbf{REUSABLE / SALVAGE (Risk $\le$ 0.40):} Derelict bus; nominate for On-Orbit Servicing (OOS).
    \item \textbf{INERT FRAGMENT (Risk $\le$ 0.60):} Passive fragment; log in orbital catalog.
\end{itemize}

\section{3D Sensor Fusion \& 6-State Kalman GNC}
State vector $\mathbf{x} = [x, y, z, \dot{x}, \dot{y}, \dot{z}]^T$. Lead flight time $t_f$ is computed from the 4th-degree quartic polynomial:
$$c_4 t_f^4 + c_2 t_f^2 + c_1 t_f + c_0 = 0$$
Pan ($\theta_p$) and tilt ($\theta_t$) lead angles:
$$\theta_p = \text{atan2}(x_t, z_t), \quad \theta_t = \text{atan2}\left(y_t + \frac{1}{2}gt_f^2, \sqrt{x_t^2 + z_t^2}\right)$$

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 6: RESULTS & BENCHMARKS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{RESULTS, BENCHMARKS AND DISCUSSION}
\section{Multi-Class Detection Benchmarks}
\begin{table}[h]
\centering
\small
\begin{tabular}{|l|c|c|l|}
\hline
\textbf{Metric} & \textbf{Baseline (YOLO11n)} & \textbf{SPACI Final (YOLO11s)} & \textbf{Impact} \\ \hline
mAP@50 & 46.0\% & \textbf{88.67\%} & +42.67\% accuracy gain across 11 classes. \\ \hline
mAP@50-95 & 23.1\% & \textbf{50.56\%} & +27.46\% gain; tight bounding boxes. \\ \hline
Precision & 32.0\% & \textbf{82.46\%} & Sharp suppression of false alarms. \\ \hline
Recall & 56.9\% & \textbf{84.99\%} & High recall ensures non-evasion of debris. \\ \hline
GPU Latency & 8.2 ms & \textbf{11.5 ms} & Maintains ~87 FPS edge throughput. \\ \hline
Pipeline Latency & 125.0 ms & \textbf{18.2 ms} & Guarantees 30 Hz streaming cycle. \\ \hline
\end{tabular}
\caption{Model Progression \& Quantitative Benchmark Results}
\label{tab:results_progression}
\end{table}

\section{Confusion Matrix Analysis}
Figure \ref{fig:cm} illustrates the normalized multi-class confusion matrix on the held-out test split, demonstrating sharp diagonal classification across operational scientific payloads and unmodeled fragments.

\begin{figure}[h]
\centering
\includegraphics[width=4.6in]{figures/confusion_matrix_normalized.png}
\caption{Normalized Multi-Class Confusion Matrix for 11 Orbital Object Classes}
\label{fig:cm}
\end{figure}

\section{Precision-Recall and F1 Performance Curves}
\begin{figure}[h]
\centering
\includegraphics[width=4.6in]{figures/PR_curve.png}
\caption{Precision-Recall (PR) Curve Across 11 Taxonomy Classes (mAP@50 = 88.67\%)}
\label{fig:pr_curve}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=4.6in]{figures/F1_curve.png}
\caption{F1-Score vs. Confidence Threshold Optimization Curve}
\label{fig:f1_curve}
\end{figure}

\section{Mission Control HUD Verification}
The Mission Control web dashboard operates on port 8080, providing atomic 30 Hz WebSocket telemetry streaming with dedicated per-tab KPI tracking grids.

\begin{figure}[h]
\centering
\includegraphics[width=5.0in]{figures/verified_unified_cockpit.png}
\caption{Mission Control Web HUD: Optical Viewport with YOLO11s Target Reticle}
\label{fig:hud_viewport}
\end{figure}

\begin{figure}[h]
\centering
\includegraphics[width=5.0in]{figures/verified_hud_workspace.png}
\caption{Video Kinematics Workspace \& NASA-STD-8719.14C Threat Assessment Console}
\label{fig:hud_threat}
\end{figure}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 7: OTHER SPECIFICATIONS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{OTHER SPECIFICATIONS}
\section{Advantages}
\begin{enumerate}
    \item \textbf{Lightweight Edge Inference:} 9.42M parameters executing at 11.5 ms GPU latency (~87 FPS), ideal for onboard edge processors.
    \item \textbf{Kinematics-Aware Tracking:} BoT-SORT maintains persistent Track IDs and calculates rolling tumble variance ($\sigma^2_{AR}$).
    \item \textbf{Aerospace Standards Grounded:} Implements NASA-STD-8719.14C kinetic energy thresholds directly within streaming vision loops.
    \item \textbf{High-Speed Web Architecture:} FastAPI + WebSockets deliver seamless 30 Hz telemetry without UI lag.
\end{enumerate}

\section{Limitations}
\begin{enumerate}
    \item Monocular optical area ratio serves as a linear size proxy; accurate absolute depth requires LiDAR or stereo depth cameras.
    \item Harsh unattenuated solar reflections in space vacuum can cause localized optical saturation.
\end{enumerate}

\section{Applications}
\begin{enumerate}
    \item \textbf{Autonomous Proximity Operations:} Guiding Active Debris Removal (ADR) spacecraft during rendezvous.
    \item \textbf{Space Traffic Management (STM):} Onboard collision detection alerting spacecraft operators to execute avoidance maneuvers.
    \item \textbf{Satellite On-Orbit Servicing (OOS):} Identifying reusable satellite buses for refueling and life-extension missions.
\end{enumerate}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CHAPTER 8: CONCLUSIONS AND FUTURE WORK
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{CONCLUSIONS AND FUTURE WORK}
\section{Conclusion}
The SPACI software project successfully establishes an open-source, highly accurate (88.67\% mAP@50), and real-time (11.5 ms) deep learning system for space debris detection, tracking, and collision risk assessment. By uniting YOLO11s detection, BoT-SORT kinematics, NASA-STD-8719.14C risk rules, 3D Kalman GNC, and a 30 Hz WebSocket Mission Control web interface, the project provides a robust software foundation for autonomous space situational awareness.

\section{Future Scope}
\begin{enumerate}
    \item \textbf{TensorRT Quantization:} Exporting PyTorch weights to FP16/INT8 engines for ultra-low power deployment on NVIDIA Jetson edge computers.
    \item \textbf{Stereo Vision \& Visual SLAM:} Extending monocular vision to dual cameras for full 6-DoF relative pose regression.
    \item \textbf{NASA cFS Containerization:} Packaging the Python pipeline into NASA Core Flight System (cFS) flight software modules.
\end{enumerate}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% BIBLIOGRAPHY
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\addcontentsline{toc}{chapter}{Bibliography}
\begin{thebibliography}{99}

\bibitem{1}
M. Kisantal, S. Sharma, T. H. Park, et al., ``Satellite Pose Estimation Challenge: Dataset, Competition Design, and Results,'' \emph{IEEE Transactions on Aerospace and Electronic Systems}, vol. 56, no. 5, pp. 4083--4098, Oct. 2020. DOI: 10.1109/TAES.2020.2989063.

\bibitem{2}
S. Sharma and S. D'Amico, ``Neural Network-Based Pose Estimation for Noncooperative Spacecraft Rendezvous,'' \emph{IEEE Transactions on Aerospace and Electronic Systems}, vol. 56, no. 6, pp. 4638--4658, Dec. 2020. DOI: 10.1109/TAES.2020.2999450.

\bibitem{3}
J. Redmon and A. Farhadi, ``YOLOv3: An Incremental Improvement,'' \emph{arXiv preprint arXiv:1804.02767}, 2018.

\bibitem{4}
A. Bewley, Z. Ge, L. Ott, F. Ramos, and B. Upcroft, ``Simple online and realtime tracking,'' in \emph{Proc. IEEE International Conference on Image Processing (ICIP)}, 2016, pp. 3464--3468.

\bibitem{5}
N. Wojke, A. Bewley, and D. Paulus, ``Simple online and realtime tracking with a deep association metric,'' in \emph{Proc. IEEE International Conference on Image Processing (ICIP)}, 2017, pp. 3645--3649.

\bibitem{6}
N. Aharon, R. Orfaig, and B. Z. Bobrovsky, ``BoT-SORT: Robust Associations Multi-Pedestrian Tracker,'' \emph{arXiv preprint arXiv:2206.14651}, 2022.

\bibitem{7}
J. C. Liou and N. L. Johnson, ``Risks in orbit: Assessing the impact of space debris on operational spacecraft,'' \emph{Science}, vol. 311, no. 5759, pp. 340--341, Jan. 2006. DOI: 10.1126/science.1121337.

\bibitem{8}
NASA, ``Process for Limiting Orbital Debris,'' \emph{NASA Technical Standard NASA-STD-8719.14C}, National Aeronautics and Space Administration, Washington, D.C., Nov. 2021.

\bibitem{9}
European Space Agency (ESA), ``ESA Space Debris Mitigation Policy and Standards,'' \emph{ESA/ADMIN/IPOL(2014)2}, European Space Operations Centre (ESOC), Darmstadt, Germany, 2023.

\bibitem{10}
G. Welch and G. Bishop, ``An Introduction to the Kalman Filter,'' University of North Carolina at Chapel Hill, Tech. Rep. TR 95-041, 2006.

\bibitem{11}
T. Y. Lin, P. Goyal, R. Girshick, K. He, and P. Dollár, ``Focal Loss for Dense Object Detection,'' in \emph{Proc. IEEE International Conference on Computer Vision (ICCV)}, 2017, pp. 2980--2988.

\bibitem{12}
S. Ramírez, et al., ``Real-time computer vision algorithms for spacecraft proximity operations,'' \emph{Acta Astronautica}, vol. 182, pp. 450--462, May 2021.

\bibitem{13}
G. S. Aglietti, et al., ``The active space debris removal mission RemoveDebris. Part 2: In orbit operations,'' \emph{Acta Astronautica}, vol. 168, pp. 310--322, Mar. 2020.

\bibitem{14}
M. Shan, J. Guo, and E. Gill, ``Review and comparison of active space debris capturing and removal methods,'' \emph{Progress in Aerospace Sciences}, vol. 80, pp. 18--32, Jan. 2016.

\bibitem{15}
Y. Liu, C. Gao, and Z. Meng, ``Tethered space-net capture dynamics and trajectory planning for space debris removal,'' \emph{IEEE Transactions on Aerospace and Electronic Systems}, vol. 58, no. 4, pp. 3210--3224, Aug. 2022.

\end{thebibliography}

\end{document}
'''
    with open("reports/SPACI_BE_PROJECT_REPORT_AISSMS.tex", "w", encoding="utf-8") as f:
        f.write(tex_content)
    print("Successfully generated reports/SPACI_BE_PROJECT_REPORT_AISSMS.tex")

if __name__ == "__main__":
    create_be_report_tex()
