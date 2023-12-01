import numpy as np
import cv2

# def contours_to_gcode(contours, image):
#     coords = []
#
#     for contour in contours:
#         for point in contour:
#             x, y = point[0]
#             coords.append([x, y])
#     # Scale down coordinates
#     coords = np.array(coords)
#     coords = coords * (200 / np.max(coords))
#     coords = coords[4:]
#     # Create G-code
#
#     gcode = []
#
#     for coord in coords:
#         x, y = coord
#         gcode.append(f"G1 X{round(x, 3)} Y{round(y, 3)} \n")
#
#     gcode.pop(0)
#     return gcode

def con_to_g_test(image, contours):
    printer_x_length_mm = 210  # X-axis
    printer_y_length_mm = 200  # Y-axis
    image_height_pixels, image_width_pixels, _ = image.shape

    x_scale = printer_x_length_mm / image_width_pixels  # X-axis - Pixely na mm
    y_scale = printer_y_length_mm / image_height_pixels  # Y-axis - Pixely na mm



def con_to_g(contours, image):
    printer_x_length_mm = 210  # X-axis
    printer_y_length_mm = 200  # Y-axis

    # Scaling faktory
    image_height_pixels, image_width_pixels, _ = image.shape
    print(image_height_pixels, image_width_pixels)
    x_scale = printer_x_length_mm / image_width_pixels  # X-axis - Pixely na mm
    y_scale = printer_y_length_mm / image_height_pixels  # Y-axis - Pixely na mm

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
        gcode_file.write(f'G0 X{start_x:.2f} Y{start_y:.2f}\n')

        for contour in contours:
            for point in contour:
                x_pixel, y_pixel = point[0]
                x_mm = x_pixel * x_scale
                y_mm = y_pixel * y_scale

                # G1 pro hladsi pohyb
                gcode_file.write(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z20.0 F1000.0\n')

#{'top_left': [599, 136], 'top_right': [1493, 136], 'bottom_left': [601, 955]}

def con_to_gcode(contours, image, json_dict):
    printer_x_length_mm = 210  # X-axis
    printer_y_length_mm = 200  # Y-axis

    width = json_dict['top_right'][0] - json_dict['top_left'][0]
    height = json_dict['bottom_left'][1] - json_dict['top_left'][1]

    print(height, width)

    # Scaling factor
    image_height_pixels, image_width_pixels, _ = image.shape
    print(image_height_pixels, image_width_pixels)
    x_scale = printer_x_length_mm / image_width_pixels  # X-axis - Pixels to mm
    y_scale = printer_y_length_mm / image_height_pixels  # Y-axis - Pixels to mm

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

    # Move to start position
    gcode_commands.append(f'G0 Z30.0 X{start_x:.2f} Y{start_y:.2f}')

    for contour in contours:
        for point in contour:
            x_pixel, y_pixel = point[0]
            x_mm = x_pixel * x_scale
            y_mm = y_pixel * y_scale

            # G1 for smoother movement
            gcode_commands.append(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z18.0 F1000.0')

    gcode_commands.append(f'G1 X0 Y210 Z20.0 F1000.0')

    return gcode_commands  # Return the list of G-code commands


