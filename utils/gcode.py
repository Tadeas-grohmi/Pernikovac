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



def con_to_g(contours, image):
    printer_x_length_mm = 210  # X-axis length in mm
    printer_y_length_mm = 200  # Y-axis length in mm

    # Calculate scaling factors
    image_height_pixels, image_width_pixels, _ = image.shape
    x_scale = printer_x_length_mm / image_width_pixels  # Pixels to mm conversion for X-axis
    y_scale = printer_y_length_mm / image_height_pixels  # Pixels to mm conversion for Y-axis

    with open('output.gcode', 'w') as gcode_file:
        # Set the ROI to cover the entire image
        x_min = 0  # Minimum X coordinate (left edge of the image)
        x_max = image_width_pixels  # Maximum X coordinate (right edge of the image)
        y_min = 0  # Minimum Y coordinate (top edge of the image)
        y_max = image_height_pixels  # Maximum Y coordinate (bottom edge of the image)

        # Define start position (adjust as needed)
        start_pixel_x = x_min  # Starting X coordinate in pixels
        start_pixel_y = y_min  # Starting Y coordinate in pixels
        start_x = start_pixel_x * x_scale  # Starting X coordinate in mm
        start_y = start_pixel_y * y_scale  # Starting Y coordinate in mm

        # Move to start position (G0 command)
        gcode_file.write(f'G0 X{start_x:.2f} Y{start_y:.2f}\n')

        # Iterate through the filtered contours
        for contour in contours:
            for point in contour:
                x_pixel, y_pixel = point[0]
                x_mm = x_pixel * x_scale
                y_mm = y_pixel * y_scale

                # Move to the next point (G1 command)
                gcode_file.write(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z20.0 F1000.0\n')



