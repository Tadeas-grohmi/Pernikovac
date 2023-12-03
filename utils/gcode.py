import numpy as np
import cv2

def con_to_gcode(contours, image, json_dict, extruder_rate, z_off):
    printer_x_length_mm = 215  # X-axis
    printer_y_length_mm = 200  # Y-axis
    
    width = json_dict['top_right'][0] - json_dict['top_left'][0]
    height = json_dict['bottom_left'][1] - json_dict['top_left'][1]
    
    # Scaling factor
    image_height_pixels, image_width_pixels, _ = image.shape
    x_scale = printer_x_length_mm / width  # X-axis - Pixels to mm
    y_scale = printer_y_length_mm / height  # Y-axis - Pixels to mm

    gcode_commands = []  

    # Min, max pro spravny GCODE
    x_min = 0  #Min X
    x_max = image_width_pixels  #Max X
    y_min = 0  #Min Y
    y_max = image_height_pixels  #Max Y

    
    gcode_commands.append(f'G1 Z10 F2000')
    gcode_commands.append(f'G92 E0')
    
    current_extruder = 0.0 
    
    default_extruder = extruder_rate #0,55
    
    extruder_increment = 1.6  # Increment pro prvnich 15
    extruder_decrement = 0.2  # Decrement pro poslednich 20 
    
    for i, contour in enumerate(contours):
        for j, point in enumerate(contour):
            x_pixel, y_pixel = point[0]
            
            #Otaceni souradnic po stredove ose
            middle_x_pixel = image_width_pixels // 2
            x_pixel_mirror = middle_x_pixel - (x_pixel - middle_x_pixel)
            
            #Scaling pixely na mm pro GCODE
            x_mm = ((x_pixel_mirror * x_scale) + 0)
            y_mm = (y_pixel * y_scale) - 6
            
            #Uprava extruze
            if i < 5:
                current_extruder += extruder_increment * 1.5
            if i < 15:
                current_extruder += extruder_increment  
            elif i >= len(contours) - 25:
                current_extruder += default_extruder - extruder_decrement  
            else:
                current_extruder += default_extruder  
            
            current_extruder = 0
            
            #Start extruze u prvniho conturu
            if i == 0 and j == 0:
                gcode_commands.append(f'G1 X{x_mm:.2f} Y{y_mm:.2f} Z{z_off + 5} E0 F1500.0')
                gcode_commands.append(f'G1 Z3.2 F200.0')
                gcode_commands.append(f'G4 P150')
                gcode_commands.append(f'G1 E50')
                gcode_commands.append(f'G4 P850')
                gcode_commands.append(f'G92 E0')
            else:
                gcode_commands.append(f'G1 X{x_mm:.3f} Y{y_mm:.3f} Z{z_off} E{current_extruder:.3f} F220.0')

    #Retrakce extruderu
    gcode_commands.append(f'G4 P1000')
    gcode_commands.append(f'G1 Z{z_off + 15} E{current_extruder - (current_extruder/2)} F350')
    
    #Moove do standby pozice
    gcode_commands.append(f'G1 X0 Y210 Z20.0 F2000')

    return gcode_commands  

    
    
    
    