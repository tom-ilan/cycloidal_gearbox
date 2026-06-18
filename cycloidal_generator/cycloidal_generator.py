import adsk.core
import adsk.fusion
import traceback
import math
import os
import sys

# 1. Get the absolute path of the directory containing this script
script_dir = os.path.dirname(os.path.realpath(__file__))

# 2. Append this directory to Python's system search paths if it isn't there
if script_dir not in sys.path:
    sys.path.append(script_dir)

# 3. Safe to import your custom file/module now
import cycloidal_math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = adsk.fusion.Design.cast(app.activeProduct)
        
        if not design:
            ui.messageBox('Please open a design before running the script.')
            return

        # USER INPUT DIALOGS
        # 1. Input for Number of Pins (N)
        input_N, cancelled = ui.inputBox('Enter number of pins (N):', 'Gear Parameters', '6')
        if cancelled or not input_N: return
        N = int(input_N)

        # 2. Input for Pitch Radius (R)
        input_R, cancelled = ui.inputBox('Enter pitch radius in cm (R):', 'Gear Parameters', '5.0')
        if cancelled or not input_R: return
        R = float(input_R)

        # 3. Input for Eccentricity (E)
        input_E, cancelled = ui.inputBox('Enter eccentricity in cm (E):', 'Gear Parameters', '0.2')
        if cancelled or not input_E: return
        E = float(input_E)

        # 4. Input for Pin Radius (r)
        input_r, cancelled = ui.inputBox('Enter pin radius in cm (r):', 'Gear Parameters', '0.4')
        if cancelled or not input_r: return
        r = float(input_r)

        # 5. Input for Precision / Step Size
        input_step, cancelled = ui.inputBox('Enter step size in degrees (Precision):\n(Smaller number = higher precision/more points)', 'Gear Parameters', '2.0')
        if cancelled or not input_step: return
        step_angle = float(input_step)

        # Guard rail to prevent infinite loops or crashes
        if step_angle <= 0:
            ui.messageBox('Precision step angle must be greater than 0.')
            return

        # SKETCH CREATION
        rootComp = design.rootComponent
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        
        # Distinct sketches for disk profile and housing pins
        sketch_disk = sketches.add(xyPlane)
        sketch_disk.name = "Cycloidal Disk Profile"
        
        sketch_outer_pin = sketches.add(xyPlane)
        sketch_outer_pin.name = "Cycloidal Outer Pin Profile"

        # Generate Cycloidal Disk Profile points
        cycloidal_disk_points = adsk.core.ObjectCollection.create()
        current_angle = 0.0
        
        while current_angle < 360.0:
            t = math.radians(current_angle)
            x_disk, y_disk = cycloidal_math.disk(t, N, R, E, r)
            cycloidal_disk_points.add(adsk.core.Point3D.create(x_disk, y_disk, 0))
            current_angle += step_angle

        # Close the disk spline profile seamlessly at 360 degrees
        t_end = math.radians(360.0)
        x_end, y_end = cycloidal_math.disk(t_end, N, R, E, r)
        cycloidal_disk_points.add(adsk.core.Point3D.create(x_end, y_end, 0))
        
        # Draw the disk spline
        sketch_disk.sketchCurves.sketchFittedSplines.add(cycloidal_disk_points)
        
        # Generate and draw the Outer Housing Pins
        sketch_outer_pin_circles = sketch_outer_pin.sketchCurves.sketchCircles
        
        for i in range(N):
            # Pass the raw index integer 'i' directly to match the module's math logic
            x_outer_pin, y_outer_pin = cycloidal_math.outer_pin(i, N, R, E, r)
            
            # Format center point as a proper Point3D object
            pin_center = adsk.core.Point3D.create(x_outer_pin, y_outer_pin, 0)

            # Draw the housing pin using the correct pin radius variable 2 * r to ensure proper spacing and fit
            radius_for_pin = 2 * 
            sketch_outer_pin_circles.addByCenterRadius(pin_center, radius_for_pin)

        sketch_outer_pin_circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), radius_for_pin)
        sketch_outer_pin_circles.addByCenterRadius(adsk.core.Point3D.create(E, 0, 0), r)

    except ValueError:
        if ui:
            ui.messageBox('Error: Please enter valid numerical values.')
    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
