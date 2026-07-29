# Cycloidal Gearbox ⚙️

This project currently has two parts completed parts:

1) A Python-based script for **Autodesk Fusion 360** that automatically generates the sketch profiles required to model a complete cycloidal gearbox. It calculates and draws the cycloidal disk, the outer housing pins, and the concentric output disk pins, and the input pins.

2) An example of what a 3d printed cycloidal gearbox that was designed using the python script and 3d printed
[insert image from media]
---

## File Structure

- **[cycloidal_generator.py]** Main entry point for the Fusion 360 script. Handles user interface prompts, input validation, and sketch creation.
- **[cycloidal_math.py]** Dedicated mathematical helper module containing parametric equations for the cycloidal profile disk, outer pins, and output pins/holes.
- **[cycloidal_generator.manifest]** Autodesk Fusion 360 script manifest file.

---

## How to Install and Run

1. Open **Autodesk Fusion 360**.
2. Press `Shift + S` on your keyboard (or navigate to **Utilities** > **Add-Ins** > **Scripts and Add-Ins**).
3. Select the **Scripts** tab.
4. Click the green **`+` (Plus)** button next to "My Scripts" to add a new script.
5. Select the folder `cycloidal_generator` from this directory.
6. The script `cycloidal_generator` will appear under **My Scripts**. Select it and click **Run**.

---

## Input Parameters

When running the script, you will be prompted for the following parameters (all dimensions are in **centimeters**):

| Parameter | Default | Description |
|---|---|---|
| **Number of pins (N)** | `6` | Total number of outer stationary housing pins. The cycloidal disk will have $N - 1$ lobes. |
| **Pitch radius (R)** | `5.0` | Radius of the circle on which the outer housing pins are distributed. |
| **Eccentricity (E)** | `0.2` | The input shaft offset/eccentricity. |
| **Outer pin radius (r)** | `0.4` | Radius of the stationary outer housing pins/rollers. |
| **Step size / Precision** | `2.0` | Angular precision in degrees. A smaller step size generates a smoother spline profile. |
| **Input shaft/bearing radius** | `1.0` | Radius of the central input bearing. |
| **Output pin radius** | `0.5` | Radius of the pins attached to the output disk/shaft. |
| **Number of output holes** | `5` *(N-1)* | The quantity of output pin-and-hole arrangements. |
| **Output bolt circle radius** | `2.5` | The radial distance from the center to the output pins/holes. |

---

## Mathematical Foundations

### 1. Cycloidal Disk Profile
The profile of the cycloidal disk is generated parametrically with parameter $t$ (from $0$ to $2\pi$):

$$x = R \cos(t) - r \cos(t + \psi) - E \cos(N \cdot t)$$
$$y = -R \sin(t) + r \sin(t + \psi) + E \sin(N \cdot t)$$

Where $\psi$ is the offset angle calculation:

$$\psi = \text{atan2}\left(\sin((1 - N) \cdot t), \frac{R}{E \cdot N} - \cos((1 - N) \cdot t)\right)$$

### 2. Output Disk Clearance & Reduction
- **Output Holes (in Rotor):** Center of output holes are offset parametrically to track the rotor wobble:
  - $X\text{-offset} = -E \cos(N \cdot t)$
  - $Y\text{-offset} = E \sin(N \cdot t)$
  - **Output Hole Radius:** To accommodate the eccentric wobble, the hole radius in the rotor is drawn as $r_{\text{pin}} + E$.
- **Concentric Output Disk:** Sits concentric with the housing origin ($0$ offset).
- **Speed Reduction:** For an $N$-pin stationary ring housing, the output disk rotates in the opposite direction of the input shaft with a speed reduction of:

$$\theta_{\text{out}} = -\frac{t}{N - 1}$$

--- 
## In Development

- Version 2 of the drive using bearings, and screws for tighter tollerances, and higher efficencies
- Use of a Nema 17 stepper motor, a4988 driver to drive the gearbox (both version 1 and 2). 