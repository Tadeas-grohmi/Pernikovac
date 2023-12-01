import numpy as np
import cv2

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
    
    
def con_to_g(contours, image, json_dict):
    printer_x_length_mm = 210  # X-axis
    printer_y_length_mm = 200  # Y-axis
    
    width = json_dict['top_right'][0] - json_dict['top_left'][0]
    height = json_dict['bottom_left'][1] - json_dict['top_left'][1]
    
    # Scaling factor
    image_height_pixels, image_width_pixels, _ = image.shape
    x_scale = printer_x_length_mm / width  # X-axis - Pixels to mm
    y_scale = printer_y_length_mm / height  # Y-axis - Pixels to mm

    gcode_commands = []  # List to store G-code commands

    # Min, max for proper G-code
    x_min = 0  # Minimum X coordinate (left edge of the image)
    x_max = image_width_pixels  # Maximum X coordinate (right edge of the image)
    y_min = 0  # Minimum Y coordinate (top edge of the image)
    y_max = image_height_pixels  # Maximum Y coordinate (bottom edge of the image)

    # Start position
    start_pixel_x = x_min  # Starting X coordinate in pixels
    start_pixel_y = y_min  # Starting Y coordinate in pixels
    start_x = start_pixel_x * x_scale  # Starting X coordinate in mm
    start_y = start_pixel_y * y_scale  # Starting Y coordinate in mm

    with open('output.gcode', 'w') as gcode_file:
        # Min, max na spravny GCODE
        x_min = 0  # Minimum X coordinate (left edge of the image)
        x_max = image_width_pixels  # Maximum X coordinate (right edge of the image)
        y_min = 0  # Minimum Y coordinate (top edge of the image)
        y_max = image_height_pixels  # Maximum Y coordinate (bottom edge of the image)

        # Start pozice
        start_pixel_x = x_min  # Starting X coordinate in pixels
        start_pixel_y = y_min  # Starting Y coordinate in pixels
        start_x = start_pixel_x * x_scale  # Starting X coordinate in mm
        start_y = start_pixel_y * y_scale  # Starting Y coordinate in mm

        # Moove na start pozici
        gcode_file.write(f'G0 Z30.0 X{start_x:.2f} Y{start_y:.2f}\n')

        for contour in contours:
            for point in contour:
                x_pixel, y_pixel = point[0]
                x_mm = x_pixel * x_scale
                y_mm = y_pixel * y_scale

                # G1 pro hladsi pohyb
                gcode_file.write(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z30.0 F1000.0\n')

def reflect_points_along_x(points, center_x):
    """
    Reflect X-axis points with respect to the given center_x.

    Parameters:
    - points: List of (x, y) coordinates
    - center_x: X-coordinate for the reflection center

    Returns:
    - List of reflected (x, y) coordinates
    """
    reflected_points = []
    
    for x, y in points:
        reflected_x = 2 * center_x - x
        reflected_point = (reflected_x, y)
        reflected_points.append(reflected_point)

    return reflected_points


def con_to_gcode(contours, image, json_dict):
    printer_x_length_mm = 215  # X-axis
    printer_y_length_mm = 200  # Y-axis
    
    width = json_dict['top_right'][0] - json_dict['top_left'][0]
    height = json_dict['bottom_left'][1] - json_dict['top_left'][1]
    
    # Scaling factor
    image_height_pixels, image_width_pixels, _ = image.shape
    x_scale = printer_x_length_mm / width  # X-axis - Pixels to mm
    y_scale = printer_y_length_mm / height  # Y-axis - Pixels to mm

    gcode_commands = []  

    # Min, max for proper G-code
    x_min = 0  # Minimum X coordinate (left edge of the image)
    x_max = image_width_pixels  # Maximum X coordinate (right edge of the image)
    y_min = 0  # Minimum Y coordinate (top edge of the image)
    y_max = image_height_pixels  # Maximum Y coordinate (bottom edge of the image)

    
    gcode_commands.append(f'G1 Z10 F1000')
    gcode_commands.append(f'G92 E0')
    
    extruder = 0
    current_extruder = 0.0  # Initial extruder value
    
    default_extruder = 0.55 #0,55
    
    extruder_increment = 1.5  # Increment for the first 15 contours 1,7
    extruder_decrement = 0.2  # Decrement for the last 15 contours 0,5
    
    current_extruder += default_extruder
    
    
    for i, contour in enumerate(contours):
        for j, point in enumerate(contour):
            x_pixel, y_pixel = point[0]
            
            middle_x_pixel = image_width_pixels // 2
            x_pixel_mirror = middle_x_pixel - (x_pixel - middle_x_pixel)
            
            
            x_mm = ((x_pixel_mirror * x_scale) + 1)
            y_mm = (y_pixel * y_scale) - 8
            
            if i < 5:
                current_extruder += extruder_increment * 1.5
            if i < 15:
                current_extruder += extruder_increment  # Increment for the first 15 contours
            elif i >= len(contours) - 20:
                current_extruder += default_extruder - extruder_decrement  # Increment and then decrement for the last 15 contours
            else:
                current_extruder += default_extruder  # Default increment
            
            current_extruder = 0
            
            # Start extruding at the first point of the first contour
            if i == 0 and j == 0:
                gcode_commands.append(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z5.0 E0 F1000.0')
                gcode_commands.append(f'G1 Z3.2 F200.0')
                gcode_commands.append(f'G4 P150')
                #gcode_commands.append(f'G1 E45')
                gcode_commands.append(f'G4 P850')
                gcode_commands.append(f'G92 E0')
            else:
                # Extrude during normal movements
                gcode_commands.append(f'G1 X{x_mm:.3f} Y{y_mm:.3f} Z3.9 E{current_extruder:.3f} F200.0')

    # Retract the extruder after completing the contours
    gcode_commands.append(f'G4 P1000')
    gcode_commands.append(f'G1 Z10 E{current_extruder - (current_extruder/2)} F500')

    gcode_commands.append(f'G1 X0 Y210 Z20.0 F1000.0')

    return gcode_commands  # Return the list of G-code commands

    
    
    
    