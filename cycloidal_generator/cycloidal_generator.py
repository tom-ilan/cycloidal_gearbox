import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys

# Ensure the script's directory is on the Python path so sibling modules can be imported.
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import cycloidal_math

# Helper function to get float input from the user
def _get_float_input(ui, prompt: str, title: str, default: str):
    """Prompt the user for a float value. Returns None if cancelled."""
    value, cancelled = ui.inputBox(prompt, title, default)
    if cancelled or not value:
        return None
    return float(value)

# Helper function to get integer input from the user
def _get_int_input(ui, prompt: str, title: str, default: str):
    """Prompt the user for an integer value. Returns None if cancelled."""
    value, cancelled = ui.inputBox(prompt, title, default)
    if cancelled or not value:
        return None
    return int(value)

# Main entry point for the script
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        # Guarantee that the script is in a design environment
        if not design:
            ui.messageBox('Please open a design before running the script.')
            return

        # Gather user inputs:
        title = 'Gear Parameters'

        # N = number of pins
        N = _get_int_input(ui, 'Enter number of pins (N):', title, '6')
        if N is None: return

        # R = pitch radius
        R = _get_float_input(ui, 'Enter pitch radius in cm (R):', title, '5.0')
        if R is None: return

        # E = eccentricity
        E = _get_float_input(ui, 'Enter eccentricity in cm (E):', title, '0.2')
        if E is None: return

        # r = pin radius
        r = _get_float_input(ui, 'Enter pin radius in cm (r):', title, '0.4')
        if r is None: return

        # step_angle = precision step size
        # The smaller the step size, the higher the precision of the generated profile.
        step_angle = _get_float_input(
            ui,
            'Enter step size in degrees (Precision):\n(Smaller = higher precision)',
            title, '2.0'
        )
        if step_angle is None: return

        shaft_radius = _get_float_input(
            ui, 'Enter input shaft radius in cm:', title, '1.0'
        )
        if shaft_radius is None: return

        if step_angle <= 0:
            ui.messageBox('Precision step angle must be greater than 0.')
            return

        # Create sketches for the cycloidal disk and outer pins
        rootComp = design.rootComponent
        xyPlane = rootComp.xYConstructionPlane

        sketch_disk = rootComp.sketches.add(xyPlane)
        sketch_disk.name = "Cycloidal Disk Profile"

        sketch_outer_pins = rootComp.sketches.add(xyPlane)
        sketch_outer_pins.name = "Cycloidal Outer Pin Profile"

        sketch_input_shaft = rootComp.sketches.add(xyPlane)
        sketch_input_shaft.name = "Input Shaft/Bearing Profile"

        # Generate cycloidal disk profile
        points = adsk.core.ObjectCollection.create()
        angle = 0.0

        while angle < 360.0:
            t = math.radians(angle)
            x, y = cycloidal_math.disk(t, N, R, E, r)
            points.add(adsk.core.Point3D.create(x, y, 0))
            angle += step_angle

        # Close the spline at exactly 360°
        x_end, y_end = cycloidal_math.disk(math.radians(360.0), N, R, E, r)
        points.add(adsk.core.Point3D.create(x_end, y_end, 0))

        sketch_disk.sketchCurves.sketchFittedSplines.add(points)

        # --- Generate outer housing pins ---
        pin_circles = sketch_outer_pins.sketchCurves.sketchCircles
        for i in range(N):
            cx, cy = cycloidal_math.outer_pin(i, N, R, E, r)
            center = adsk.core.Point3D.create(cx, cy, 0)
            pin_circles.addByCenterRadius(center, r)

        # Add center bore to disk sketch
        sketch_input_shaft_circles = sketch_input_shaft.sketchCurves.sketchCircles
        bore_center = adsk.core.Point3D.create(E, 0, 0)
        sketch_input_shaft_circles.addByCenterRadius(bore_center, shaft_radius)
        sketch_input_shaft_circles.addByCenterRadius(bore_center, shaft_radius + E)

    # Handle exceptions and provide user feedback
    except ValueError:
        if ui:
            ui.messageBox('Error: Please enter valid numerical values.')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
