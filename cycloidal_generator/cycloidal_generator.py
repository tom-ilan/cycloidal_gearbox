import adsk.core
import adsk.fusion
import traceback
import math
import importlib
import os
import sys

# Ensure the script's directory is on the Python path so sibling modules can be imported.
script_dir = os.path.dirname(os.path.realpath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import cycloidal_math
importlib.reload(cycloidal_math)


def _get_float_input(ui, prompt: str, title: str, default: str):
    """Prompt the user for a float value. Returns None if cancelled."""
    value, cancelled = ui.inputBox(prompt, title, default)
    if cancelled or not value:
        return None
    return float(value)


def _get_int_input(ui, prompt: str, title: str, default: str):
    """Prompt the user for an integer value. Returns None if cancelled."""
    value, cancelled = ui.inputBox(prompt, title, default)
    if cancelled or not value:
        return None
    return int(value)

# Main entry point for the Fusion 360 script.
def run(context):
    ui = None
    try:
        # Get the Fusion 360 application and user interface
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('Please open a design before running the script.')
            return

        # Gather user inputs
        title = 'Gear Parameters'

        N = _get_int_input(ui, 'Enter number of pins (N):', title, '6')
        if N is None: return

        R = _get_float_input(ui, 'Enter pitch radius in cm (R):', title, '5.0')
        if R is None: return

        E = _get_float_input(ui, 'Enter eccentricity in cm (E):', title, '0.2')
        if E is None: return

        r = _get_float_input(ui, 'Enter pin radius in cm (r):', title, '0.4')
        if r is None: return

        step_angle = _get_float_input(
            ui,
            'Enter step size in degrees (Precision):\n(Smaller = higher precision)',
            title, '2.0'
        )
        if step_angle is None: return

        shaft_radius = _get_float_input(
            ui, 'Enter input shaft/bearing radius in cm:', title, '1.0'
        )
        if shaft_radius is None: return

        output_pin_radius = _get_float_input(
            ui, 'Enter output pin radius in cm:', title, '0.5'
        )
        if output_pin_radius is None: return

        num_output_holes = _get_int_input(
            ui, 'Enter number of output holes (default N-1):', title, str(N - 1)
        )
        if num_output_holes is None: return

        output_bolt_radius = _get_float_input(
            ui, 'Enter output bolt circle radius in cm:', title, '2.5'
        )
        if output_bolt_radius is None: return

        if step_angle <= 0:
            ui.messageBox('Precision step angle must be greater than 0.')
            return

        if num_output_holes < 2:
            ui.messageBox('Number of output holes must be at least 2.')
            return

        # Creates sketches
        rootComp = design.rootComponent
        xyPlane = rootComp.xYConstructionPlane

        sketch_disk = rootComp.sketches.add(xyPlane)
        sketch_disk.name = "Cycloidal Disk Profile"

        sketch_pins = rootComp.sketches.add(xyPlane)
        sketch_pins.name = "Cycloidal Outer Pin Profile"

        sketch_output = rootComp.sketches.add(xyPlane)
        sketch_output.name = "Output Disk"

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

        # Generate outer housing pins
        pin_circles = sketch_pins.sketchCurves.sketchCircles
        for i in range(N):
            cx, cy = cycloidal_math.outer_pin(i, N, R, E, r)
            center = adsk.core.Point3D.create(cx, cy, 0)
            pin_circles.addByCenterRadius(center, r)

        # Add input shaft
        disk_circles = sketch_disk.sketchCurves.sketchCircles
        offset_shaft_radius_center = adsk.core.Point3D.create(E, 0, 0)
        shaft_radius_center = adsk.core.Point3D.create(0, 0, 0)
        disk_circles.addByCenterRadius(offset_shaft_radius_center, shaft_radius)
        disk_circles.addByCenterRadius(shaft_radius_center, shaft_radius + E)

        # Add output holes to the cycloidal disk (rotor)
        # Hole radius = output_pin_radius + E to accommodate the eccentric wobble.
        # Holes are on a bolt circle centered at the rotor center (E, 0).
        output_hole_radius = output_pin_radius + E

        for i in range(num_output_holes):
            hx, hy = cycloidal_math.output_pin_position(i, num_output_holes, output_bolt_radius)
            hole_center = adsk.core.Point3D.create(E + hx, hy, 0)
            disk_circles.addByCenterRadius(hole_center, output_hole_radius)

        # Generate output disk pins
        # The output disk is concentric with the housing (centered at origin).
        # It rotates opposite to the input shaft at a 1:(N-1) reduction ratio:
        #   θ_out = -t / (N - 1)
        output_circles = sketch_output.sketchCurves.sketchCircles
        for i in range(num_output_holes):
            px, py = cycloidal_math.output_pin_position(i, num_output_holes, output_bolt_radius)
            pin_center = adsk.core.Point3D.create(px, py, 0)
            output_circles.addByCenterRadius(pin_center, output_pin_radius)

    # Error handling for user input and unexpected exceptions
    except ValueError:
        if ui:
            ui.messageBox('Error: Please enter valid numerical values.')
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
