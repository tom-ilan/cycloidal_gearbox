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

# Keep references of the event handlers in a global list so they are not garbage collected
_handlers = []


def create_geometry(N: int, R: float, E: float, r: float, step_angle: float,
                    shaft_radius: float, output_pin_radius: float,
                    num_output_holes: int, output_bolt_radius: float,
                    profile_offset: float = 0.0):
    """Generates the sketches in Autodesk Fusion 360 with the specified parameters.

    Args:
        profile_offset: Signed tolerance offset applied only to the disk spline
            (cm).  Positive values shrink the disk away from the pins (clearance
            for 3D-print tolerance); negative values grow it (tighter fit).  The
            effective pin radius used for the disk profile is r + profile_offset,
            so the outer-housing pin circles are always drawn at the true r.
    """
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        return
        
    rootComp = design.rootComponent
    xyPlane = rootComp.xYConstructionPlane

    # Create distinct sketches for each component
    sketch_disk = rootComp.sketches.add(xyPlane)
    sketch_disk.name = "Cycloidal Disk Profile"

    sketch_pins = rootComp.sketches.add(xyPlane)
    sketch_pins.name = "Cycloidal Outer Pin Profile"

    sketch_output = rootComp.sketches.add(xyPlane)
    sketch_output.name = "Output Disk"

    # Generate cycloidal disk profile.
    # r_disk incorporates the tolerance offset: positive offset moves the profile
    # inward (away from the pins), giving clearance for 3D-print tolerances.
    r_disk = r + profile_offset

    points = adsk.core.ObjectCollection.create()

    # Compute and store the first point so we can reuse it exactly to close
    # the spline — avoids a floating-point seam kink from recomputing at 360°.
    first_x, first_y = cycloidal_math.disk(0.0, N, R, E, r_disk)
    points.add(adsk.core.Point3D.create(first_x, first_y, 0))

    angle = step_angle
    while angle < 360.0:
        t = math.radians(angle)
        x, y = cycloidal_math.disk(t, N, R, E, r_disk)
        points.add(adsk.core.Point3D.create(x, y, 0))
        angle += step_angle

    # Close the spline by reusing the exact first point (no recomputation).
    points.add(adsk.core.Point3D.create(first_x, first_y, 0))

    sketch_disk.sketchCurves.sketchFittedSplines.add(points)

    # Generate outer housing pins
    pin_circles = sketch_pins.sketchCurves.sketchCircles
    for i in range(N):
        cx, cy = cycloidal_math.outer_pin(i, N, R, E, r)
        center = adsk.core.Point3D.create(cx, cy, 0)
        pin_circles.addByCenterRadius(center, r)

    # Add input shaft circles to the cycloidal disk sketch
    disk_circles = sketch_disk.sketchCurves.sketchCircles
    offset_shaft_radius_center = adsk.core.Point3D.create(0, 0, 0)
    disk_circles.addByCenterRadius(offset_shaft_radius_center, shaft_radius)

    # Add output holes to the cycloidal disk (rotor)
    # Hole radius = output_pin_radius + E to accommodate the eccentric wobble.
    # Holes are on a bolt circle centered at the rotor center (E, 0).
    output_hole_radius = output_pin_radius + E

    for i in range(num_output_holes):
        hx, hy = cycloidal_math.output_pin_position(i, num_output_holes, output_bolt_radius)
        hole_center = adsk.core.Point3D.create(E + hx, hy, 0)
        disk_circles.addByCenterRadius(hole_center, output_hole_radius)

    # Generate output disk pins on the concentric output disk sketch
    output_circles = sketch_output.sketchCurves.sketchCircles
    for i in range(num_output_holes):
        px, py = cycloidal_math.output_pin_position(i, num_output_holes, output_bolt_radius)
        pin_center = adsk.core.Point3D.create(px, py, 0)
        output_circles.addByCenterRadius(pin_center, output_pin_radius)


# Event handler for the command execute event (user clicks OK)
class GearboxCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandEventArgs.cast(args)
            inputs = eventArgs.command.commandInputs
            
            # Retrieve values. Database units are cm for lengths and radians for angles.
            N = inputs.itemById('num_pins').value
            R = inputs.itemById('pitch_radius').value
            E = inputs.itemById('eccentricity').value
            r = inputs.itemById('pin_radius').value
            
            # Step angle is angular unit, so .value is in radians. Convert to degrees.
            step_angle_rad = inputs.itemById('step_angle').value
            step_angle = math.degrees(step_angle_rad)
            
            shaft_radius = inputs.itemById('shaft_radius').value
            output_pin_radius = inputs.itemById('output_pin_radius').value
            num_output_holes = inputs.itemById('num_output_holes').value
            output_bolt_radius = inputs.itemById('output_bolt_radius').value
            profile_offset = inputs.itemById('profile_offset').value
            
            if step_angle <= 0:
                adsk.core.Application.get().userInterface.messageBox('Precision step angle must be greater than 0.')
                return
            
            if num_output_holes < 2:
                adsk.core.Application.get().userInterface.messageBox('Number of output holes must be at least 2.')
                return
            
            # Validate outer pin radius against the undercutting limit.
            # The cycloidal disk profile is an inward offset of the base epitrochoid by r.
            # The minimum radius of curvature of that base curve occurs at the outer lobe
            # tips and equals (R + E*N)^2 / (R + E*N^2).  When r reaches this value the
            # lobe tips become cusps; beyond it the profile self-intersects (undercuts).
            # The prerequisite R > E*N (K > 1) must also hold for the base curve to be
            # valid at all.
            if R <= E * N:
                adsk.core.Application.get().userInterface.messageBox(
                    'Invalid geometry: Pitch Radius (R) must be greater than E × N '
                    f'({E * N:.4f} cm). Increase R or reduce E / N.'
                )
                return
            
            r_max = (R + E * N) ** 2 / (R + E * N ** 2)
            # The effective disk radius includes the tolerance offset; validate that too.
            r_disk = r + profile_offset
            if r_disk >= r_max:
                adsk.core.Application.get().userInterface.messageBox(
                    f'Outer lobe is too big: the effective disk profile radius '
                    f'(r + offset = {r_disk:.4f} cm) must be less than {r_max:.4f} cm '
                    f'for these parameters. The lobe tips would develop cusps or undercut, '
                    f'making the profile geometrically impossible. '
                    f'Reduce r or the profile offset, increase R, or reduce E / N.'
                )
                return
            
            create_geometry(N, R, E, r, step_angle, shaft_radius, output_pin_radius,
                            num_output_holes, output_bolt_radius, profile_offset)
            
        except Exception:
            adsk.core.Application.get().userInterface.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for input changes (dynamic updates)
class GearboxCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            changedInput = eventArgs.input
            inputs = eventArgs.inputs
            
            # When the user updates the outer pin count (N), automatically adjust the output holes to N-1
            if changedInput.id == 'num_pins':
                num_pins_input = adsk.core.IntegerSpinnerCommandInput.cast(changedInput)
                num_output_holes_input = adsk.core.IntegerSpinnerCommandInput.cast(inputs.itemById('num_output_holes'))
                if num_pins_input and num_output_holes_input:
                    num_output_holes_input.value = num_pins_input.value - 1
        except Exception:
            pass


# Event handler for command destroy (cleanup)
class GearboxCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except Exception:
            pass


# Event handler for command creation (adds widgets to dialog)
class GearboxCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
            cmd = eventArgs.command
            inputs = cmd.commandInputs
            
            # Dialog header
            inputs.addTextBoxCommandInput('info_text', '', '<b>Cycloidal Gearbox Profile Generator</b>', 1, True)
            
            # Inputs definition
            inputs.addIntegerSpinnerCommandInput('num_pins', 'Number of Stationary Pins (N)', 4, 100, 1, 6)
            
            inputs.addValueInput('pitch_radius', 'Pitch Radius (R)', 'cm', adsk.core.ValueInput.createByReal(5.0))
            inputs.addValueInput('eccentricity', 'Eccentricity (E)', 'cm', adsk.core.ValueInput.createByReal(0.2))
            inputs.addValueInput('pin_radius', 'Outer Pin Radius (r)', 'cm', adsk.core.ValueInput.createByReal(0.4))
            inputs.addValueInput('step_angle', 'Precision (Step angle)', 'deg', adsk.core.ValueInput.createByReal(math.radians(2.0)))
            inputs.addValueInput('shaft_radius', 'Input Shaft/Bearing Radius', 'cm', adsk.core.ValueInput.createByReal(1.0))
            inputs.addValueInput('output_pin_radius', 'Output Pin Radius', 'cm', adsk.core.ValueInput.createByReal(0.5))
            
            inputs.addIntegerSpinnerCommandInput('num_output_holes', 'Number of Output Holes', 2, 100, 1, 5)
            
            inputs.addValueInput('output_bolt_radius', 'Output Bolt Circle Radius', 'cm', adsk.core.ValueInput.createByReal(2.5))
            
            # Tolerance offset shifts the disk spline inward (+) or outward (-) along
            # the profile normal to compensate for 3D-print dimensional inaccuracy.
            # Typical FDM clearance: +0.01 to +0.02 cm (0.1 – 0.2 mm).
            inputs.addValueInput('profile_offset', 'Disk Profile Tolerance Offset  (+clearance / −tighter)', 'cm',
                                 adsk.core.ValueInput.createByReal(0.0))
            
            # Connect command execution event handler
            onExecute = GearboxCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
            
            # Connect input changed event handler (for auto N-1 synchronization)
            onInputChanged = GearboxCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)
            
            # Connect command destroy event handler
            onDestroy = GearboxCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)
            
        except Exception:
            adsk.core.Application.get().userInterface.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    ui = None
    # Clear stale handlers from any previous run in this Fusion 360 session
    # to prevent memory leaks and ghost callbacks accumulating over re-runs.
    _handlers.clear()
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)

        if not design:
            ui.messageBox('Please open a design before running the script.')
            return

        # Ensure any duplicate active command definition is cleaned up first
        cmdDef = ui.commandDefinitions.itemById('cycloidalGearboxCmd')
        if cmdDef:
            cmdDef.deleteMe()
            
        cmdDef = ui.commandDefinitions.addButtonDefinition(
            'cycloidalGearboxCmd', 
            'Create Cycloidal Gearbox', 
            'Generates sketch profiles for a cycloidal gearbox.'
        )
        
        onCreated = GearboxCommandCreatedHandler()
        cmdDef.commandCreated.add(onCreated)
        _handlers.append(onCreated)
        
        cmdDef.execute()
        
        # Prevent the script from exiting automatically to keep handlers alive
        adsk.autoTerminate(False)
        
    except Exception:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
