def find_qr_corners(qr_corners, image_shape):
    # Get image width and height
    image_width = image_shape[1]
    image_height = image_shape[0]

    # Sort the corners by x + y coordinate (left upper corner has smallest sum)
    qr_corners_sorted = sorted(qr_corners, key=lambda x: x[0] + x[1])

    # Extract individual corner coordinates
    x1, y1 = qr_corners_sorted[0][0], qr_corners_sorted[0][1]
    x2, y2 = qr_corners_sorted[1][0], qr_corners_sorted[1][1]
    x3, y3 = qr_corners_sorted[2][0], qr_corners_sorted[2][1]
    x4, y4 = qr_corners_sorted[3][0], qr_corners_sorted[3][1]

    # Detect the QR code position based on corner coordinates
    if x1 < image_width / 2 and y1 < image_height / 2:
        # QR code is in the upper left corner, need upper right corner
        qr_position = "Upper Left"
        corner_coords = (x3, y3)
    elif x1 >= image_width / 2 and y1 < image_height / 2:
        # QR code is in the upper right corner, need bottom right corner
        qr_position = "Upper Right"
        corner_coords = (x4, y4)
    elif x1 < image_width / 2 and y1 >= image_height / 2:
        # QR code is in the bottom left corner, need right down corner
        qr_position = "Bottom Left"
        corner_coords = (x2, y2)
    else:
        # QR code is in the bottom right corner, need bottom right corner
        qr_position = "Bottom Right"
        corner_coords = (x4, y4)

    return qr_position, corner_coords