import math


def disk(t: float, N: int, R: float, E: float, r: float) -> tuple:
    """Calculate a point on the cycloidal disk profile.

    Uses the parametric equations:
        x = R·cos(t) - r·cos(t + psi) - E·cos(N·t)
        y = -R·sin(t) + r·sin(t + psi) + E·sin(N·t)

    where psi = atan2(sin((1-N)·t), R/(E·N) - cos((1-N)·t))

    Args:
        t: Angle parameter in radians.
        N: Number of stationary ring pins (produces N-1 lobes).
        R: Pitch radius of the outer pins in centimeters.
        E: Eccentricity (offset) of the gear in centimeters.
        r: Radius of the outer pins/rollers in centimeters.

    Returns:
        (x, y) coordinates of the point on the disk profile.
    """
    num = math.sin((1 - N) * t)
    den = (R / (E * N)) - math.cos((1 - N) * t)
    psi = math.atan2(num, den)

    x = R * math.cos(t) - r * math.cos(t + psi) - E * math.cos(N * t)
    y = -R * math.sin(t) + r * math.sin(t + psi) + E * math.sin(N * t)
    return (x, y)


def outer_pin(index: int, N: int, R: float, E: float, r: float) -> tuple:
    """Calculate the center position of an outer housing pin.

    Distributes N pins equally spaced around a circle of radius R.

    Args:
        index: Pin index (0 to N-1).
        N: Total number of pins.
        R: Pitch radius of the pin circle in centimeters.
        E: Eccentricity (unused, kept for consistent API).
        r: Pin radius (unused, kept for consistent API).

    Returns:
        (x, y) coordinates of the pin center.
    """
    theta = 2 * math.pi * index / N
    x = R * math.cos(theta)
    y = R * math.sin(theta)
    return (x, y)
