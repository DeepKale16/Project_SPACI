# SPACI 2.0: Theoretical & Scientific Research Foundation
## Physics-Grounded Orbital Debris Risk Assessment & Computer Vision Architecture

---

### Executive Summary

The **SPACI 2.0 Space Debris Detection and Operational Risk Assessment System** provides an autonomous computer vision framework for detecting, tracking, and evaluating the collision hazard posed by orbital objects in Low Earth Orbit (LEO) and Geostationary Earth Orbit (GEO).

This document establishes the scientific principles, orbital mechanics equations, and hypervelocity impact research underlying the **SPACI Risk Assessment Matrix** and its **Four Operational Classification States** (`Hazardous`, `Reusable / Salvageable`, `Useful / Active`, `Inert Fragment`).

---

## 1. International Space Agency Standards & Frameworks

The operational thresholds and mathematical weighting factors in SPACI 2.0 are directly derived from established spaceflight standards:

| Agency / Body | Standard Reference | Core Operational Principle Applied in SPACI |
|---|---|---|
| **NASA** | **NASA-STD-8719.14C** (*Limiting Orbital Debris*) | Catastrophic Breakup Threshold ($E_p/M_t \ge 40\text{ J/g}$), collision probability safety limit ($P_c < 10^{-4}$), tether & fragmentation criteria. |
| **IADC** | **IADC-02-01** (*Space Debris Mitigation Guidelines*) | Debris regime categorization: sub-centimeter shieldable, $1\text{--}10\text{ cm}$ lethal non-trackable, $>10\text{ cm}$ trackable. |
| **ESA** | **MASTER-8 & DISCOS** (*Meteoroid and Space Debris Environment Reference*) | Spatial density flux modeling across LEO altitude shells ($400\text{--}900\text{ km}$ peak crowding), Clean Space Active Debris Removal (ADR) criteria ($\omega < 5^\circ/\text{s}$). |
| **UN COPUOS** | **A/AC.105/C.1/L.366** (*Space Debris Mitigation*) | Post-mission orbital lifetime limitations (25-year rule / 5-year update), passivation of stored energy, and preservation of on-orbit servicing assets. |
| **ISO** | **ISO 24113:2023** (*Space Debris Mitigation Requirements*) | Collision Avoidance Maneuver (CAM) execution thresholds and spacecraft survivability. |

---

## 2. Orbital Mechanics & Hypervelocity Impact Physics

### 2.1 Hypervelocity Impact Energy & Breakup Mechanics

In Low Earth Orbit (LEO), spacecraft and debris travel at mean circular velocities of:
$$v_{\text{LEO}} \approx 7.5\text{--}7.8\text{ km/s}$$

Because orbital inclinations intersect at high crossing angles (polar, sun-synchronous, and retrograde crossings), relative collision velocities typically range between:
$$v_{\text{rel}} \in [10.0,\, 15.5]\text{ km/s}$$

The kinetic energy $E_k$ delivered during hypervelocity impact is governed by:
$$E_k = \frac{1}{2} m_{\text{debris}} v_{\text{rel}}^2$$

At $v_{\text{rel}} = 10\text{ km/s}$, each gram of debris carries $50,000\text{ J}$ of kinetic energy ?" equivalent to the explosive yield of approximately **$12\text{ grams}$ of TNT per gram of debris**.

#### The Catastrophic Breakup Threshold ($40\text{ J/g}$)
Under the **NASA Standard Breakup Model (Johnson et al., 2001; NASA-STD-8719.14C)**, catastrophic breakup occurs when the specific impact energy delivered to target mass $M_{\text{target}}$ exceeds:
$$\frac{E_k}{M_{\text{target}}} \ge 40\text{ J/g} = 40,000\text{ J/kg}$$

Impacts above this threshold completely shatter the target spacecraft into thousands of secondary fragments, triggering exponential **Kessler Syndrome** cascades.

---

### 2.2 Computer Vision Formulation: Optical Proxies

In onboard autonomous visual situational awareness, the sensor is a **monocular optical / NIR camera**. SPACI derives physical parameters through theoretically sound optical proxies:

#### Characteristic Linear Dimension Proxy ($L_c$)
From pinhole optics, the solid angle $\Omega$ subtended by an object with physical cross-sectional area $A_c$ at range $R$ is:
$$\Omega = \frac{A_c}{R^2}$$

In a digitized frame of resolution $W \times H$, the normalized bounding box area ratio is:
$$r_A = \frac{w_{\text{bbox}} \cdot h_{\text{bbox}}}{W \cdot H}$$

Because area scales quadratically with length ($A_c \propto L_c^2$), the linear spatial scale of the detected debris is proportional to the square root of its projected area:
$$L_{\text{proxy}} = \sqrt{r_A}$$

To map $L_{\text{proxy}}$ to a normalized physical hazard factor $S \in [0.0, 1.0]$, SPACI defines:
$$S(r_A) = \text{clip}\left(\sqrt{r_A} \cdot k_{\text{size}},\, 0.0,\, 1.0\right), \quad \text{where } k_{\text{size}} = 3.9$$

**Calibration Justification:** When an object occupies $r_A \ge 0.065$ ($6.5\%$ of the sensor field of view), $\sqrt{0.065} \times 3.9 \approx 1.0$. In spaceborne optical rendezvous, an object occupying $>6.5\%$ of the focal plane indicates a close-range proximity zone ($R < 100\text{ m}$ for typical spacecraft optics), representing critical spatial intrusion.

---

### 2.3 Rotational Dynamics & Tumbling Rate Estimation ($\omega_{\text{tumble}}$)

Defunct satellites and rocket upper stages lose attitude control and begin unconstrained 3D tumbling due to:
- Solar Radiation Pressure (YORP effect)
- Gravity gradient torques
- Residual aerodynamic drag gradients
- Outgassing of residual propellants

#### ESA Clean Space ADR Criteria:
Under ESA Clean Space Active Debris Removal guidelines, capture mechanisms (robotic arms, magnetic couplers) require tumble rates $\omega < 5^\circ/\text{s}$. Objects tumbling faster cannot be safely serviced.

#### Quantification via Temporal Aspect Ratio Fluctuation:
As an unconstrained 3D rigid body tumbles, its 2D projected aspect ratio $\text{AR}(t) = \frac{w(t)}{h(t)}$ fluctuates periodically over time.
Using **BoT-SORT** with a Kalman filter across a rolling observation window $t \in [t - N, t]$ ($N \ge 5$ frames):
$$\mu_{\text{AR}} = \frac{1}{N} \sum_{i=1}^N \text{AR}_i, \quad \sigma^2_{\text{AR}} = \frac{1}{N-1} \sum_{i=1}^N \left(\text{AR}_i - \mu_{\text{AR}}\right)^2$$

The tumble hazard factor $T$ is computed as:
$$T(\sigma^2_{\text{AR}}) = \text{clip}\left(7.5 \cdot \sigma^2_{\text{AR}},\, 0.0,\, 1.0\right)$$

- A stabilized 3-axis controlled satellite exhibits $\sigma^2_{\text{AR}} < 10^{-4} \implies T \approx 0.0$.
- A tumbling rocket stage or fragment with aspect ratio swings produces $\sigma^2_{\text{AR}} \ge 0.133 \implies T = 1.0$.

---

## 3. Four Operational Classification States

```
                [ Detected Orbital Object ]
                             |
             +---------------+---------------+
             |                               |
       Risk > 0.60?                    Risk <= 0.60?
             |                               |
      [ HAZARDOUS ]                          |
   (Critical CAM Trigger)      +-------------+-------------+
                               |                           |
                       Active Satellite?            Intact Structure?
                               |                           |
                     [ USEFUL / ACTIVE ]          Risk < 0.40?
                    (Preservation Priority)        /         \
                                                 YES          NO
                                                  |            |
                                       [ REUSABLE / SALVAGE ]  [ INERT FRAGMENT ]
                                      (Serviceable Candidate)  (Passive Monitored)
```

1. **Hazardous:** Critical collision hazard requiring immediate Collision Avoidance Maneuvers.
2. **Reusable / Salvageable:** Intact spacecraft bus retaining servicing, refueling, or ADR potential.
3. **Useful / Active:** Operational satellites maintaining station-keeping and attitude stabilization.
4. **Inert Fragment:** Passive fragments and uncontrolled debris continuously monitored by Space Surveillance Networks.
