import math


def disk(t: float, N: int, R: float, E: float, r: float) -> tuple:
    """Calculate a point on the cycloidal disk profile.

    Uses the parametric equations:
        x = R·cos(t) - E·cos(N·t) - r·cos(t + ψ)
        y = R·sin(t) - E·sin(N·t) - r·sin(t + ψ)

    where ψ = atan2(sin((1-N)·t), R/(E·N) - cos((1-N)·t))

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

    # Standard aligned parametric equations
    x = R * math.cos(t) - E * math.cos(N * t) - r * math.cos(t + psi)
    y = R * math.sin(t) - E * math.sin(N * t) - r * math.sin(t + psi)
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


def output_pin_position(index: int, num_pins: int, bolt_radius: float) -> tuple:
    """Calculate a position on the output bolt circle.

    Returns the (x, y) position equally spaced with num_pins total positions
    on a circle of the given radius. Coordinates are relative to the center
    of the bolt circle.

    Used for both:
      - Output pins on the output disk (bolt circle centered at origin).
      - Output holes in the rotor (bolt circle centered at rotor center).

    The output disk rotates opposite to the input at a reduction ratio of
    1:(N-1), where N is the number of outer housing pins:
        θ_out = -t / (N - 1)

    Args:
        index: Pin/hole index (0 to num_pins-1).
        num_pins: Total number of pins/holes (typically N-1 lobes).
        bolt_radius: Radius of the bolt circle in centimeters.

    Returns:
        (x, y) coordinates relative to the bolt circle center.
    """
    theta = 2 * math.pi * index / num_pins
    x = bolt_radius * math.cos(theta)
    y = bolt_radius * math.sin(theta)
    return (x, y)
