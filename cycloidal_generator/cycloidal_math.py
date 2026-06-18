import math

# The following functions all use the following variables where:
# t = the angle parameter (in radians)
# N = the number of stationary ring pins (produces N-1 lobes)
# R = the pitch radius of the outer pins (in centimeters)
# E = the eccentricity (offset) of the gear (in centimeters)
# r = the radius of the outer pins/rollers (in centimeters)



# This function receives the parameters of the cyclodial gear and returns the coordinates of the points of the cyclodial gear.
# It uses the parametric equations of the cyclodial gear:
# x = R * cos(t) - r * cos(t + atan(sin((1 - N) * t) / ((R / (E * N)) - cos((1 - N) * t)))) - E * cos(N * t)
# y = -R * sin(t) + r * sin(t + atan(sin((1 - N) * t) / ((R / (E * N)) - cos((1 - N) * t)))) + E * sin(N * t)
def disk(t: float, N: int, R: float, E: float, r: float):
    num = math.sin((1 - N) * t)
    den = (R / (E * N)) - math.cos((1 - N) * t)
    psi = math.atan2(num, den)
    
    x = R * math.cos(t) - r * math.cos(t + psi) - E * math.cos(N * t)
    y = -R * math.sin(t) + r * math.sin(t + psi) + E * math.sin(N * t)
    return (x, y)


# Generates the outer pins for the cycloidal disk to slide on
# Does this by generating a circle equal with a radius equal to R + r
# Then populates the circle with N number of equally spaced cirlces with radius r
def outer_pin(t: float, N: int, R: float, E: float, r: float):
    # t is treated as the pin index (0 to N-1); convert it to an angle
    # equally spaced around the circle of radius R - r
    theta = 2 * math.pi * t / (N)
    pin_x = R * math.cos(theta)
    pin_y = R * math.sin(theta)
    return pin_x, pin_y
