import numpy as np

def contours_to_gcode(contours):
    coords = []

    for contour in contours:
        for point in contour:
            x, y = point[0]
            coords.append([x, y])
    # Scale down coordinates
    coords = np.array(coords)
    coords = coords * (200 / np.max(coords))
    coords = coords[4:]
    # Create G-code

    gcode = []

    for coord in coords:
        x, y = coord
        gcode.append(f"G1 X{round(x, 3)} Y{round(y, 3)} \n")

    gcode.pop(0)
    return gcode