# Cycloidal Gearbox ⚙️

Parametric cycloidal gearbox generator script for Autodesk Fusion 360 along with functional 3D printable designs.

---

## 🛠️ Fusion 360 Generator (Quick Guide)

The **`cycloidal_generator`** script automatically calculates and draws 2D sketch profiles in Fusion 360 for the cycloidal rotor disk, outer housing pins, and output drive pins.

### Installation & Execution
1. Open Fusion 360 and open **Scripts and Add-Ins** (`Shift + S`).
2. Under the **Scripts** tab, click **`+` (Plus)** to add a script.
3. Select the `cycloidal_generator` folder and click **Run**.

### Key Parameters
- **Pins ($N$) & Pitch Radius ($R$):** Sets outer stationary housing geometry (Rotor has $N-1$ lobes).
- **Eccentricity ($E$):** Input shaft offset distance. *(Constraint: $R > E \cdot N$)*.
- **Outer Pin Radius ($r$):** Roller pin radius. *(Constraint: validated against undercut limit $r_{\text{max}}$)*.
- **Precision / Profile Offset:** Angular step size and tolerance offset ($+$ for 3D print clearance).
- **Output Pins & Bolt Radius:** Defines concentric output pins and rotor clearance holes ($r_{\text{pin}} + E$).

### Profile Math
The cycloidal rotor profile is generated using:
$$x = R \cos(t) - E \cos(N t) - r \cos(t + \psi), \quad y = R \sin(t) - E \sin(N t) - r \sin(t + \psi)$$
$$\psi = \text{atan2}\left(\sin((1 - N) t), \frac{R}{E \cdot N} - \cos((1 - N) t)\right)$$
Reduction ratio: **$1 : (N - 1)$** (rotor rotates opposite to input shaft).

---

## 🚀 Version 3 — Detailed Overview & Stats

> [!NOTE]  
> This section is dedicated to **Version 3**, a fully functional 3D-printed cycloidal gearbox powered by a standard NEMA 17 stepper motor.

### Key Specifications & Performance Stats

| Metric / Parameter | Value / Detail |
|---|---|
| **Gear Ratio** | 1:9 ($N=10$ outer pins, 9 rotor lobes) |
| **Outer Diameter** | 9.0 cm (90 mm) |
| **Drive Motor** | NEMA 17 Stepper Motor |
| **3D Printing Material** | PLA |
| **Primary Fasteners / Hardware** | 4 **m3 x 8 screws**, 2 **6004 Bearings** |
| **Tolerance Offset Applied** | +0.15 mm (+0.015 cm) profile clearance |
| **Gearbox Torque** | 0.81  N/m ± 0.0039 N·m |
| **Base Nema17 Torque** | 0.13 N/m ± 0.0039 N·m|
| **Efficency** | 66% | 


### Design Breakdown & Features

#### 1. Output mechanism
This gearbox is an Inrunner meaning it has an output shaft/lobe, this repo contains both a flat output and a output stick.

#### 2.Maximum Torque
This gearbox when maxium torque is sustained has a chance of failing in the form of the output pins snapping, this only though tends to ocour during proplonged loading.

#### 3.Backdrivability
The gearbox is able to backdriven.

---

## 📁 Other Versions & History

- **Version 1:** Initial hand-powered demonstration cycloidal gearbox model.
- **Version 2:** Micro cycloidal gearbox prototype for NEMA 17 (experimental).

