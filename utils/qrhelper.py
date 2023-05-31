import cv2

def find_qr_corners(qr_corners, image_shape):
    # Get image width and height
    image_width = image_shape[1]
    image_height = image_shape[0]

    # Sort the corners by x + y coordinate (left upper corner has smallest sum)
    qr_corners_sorted = sorted(qr_corners, key=lambda x: x[0] + x[1])

    print(qr_corners_sorted)

    # Extract individual corner coordinates
    x1, y1 = qr_corners_sorted[0][0], qr_corners_sorted[0][1]
    x2, y2 = qr_corners_sorted[1][0], qr_corners_sorted[1][1]
    x3, y3 = qr_corners_sorted[2][0], qr_corners_sorted[2][1]
    x4, y4 = qr_corners_sorted[3][0], qr_corners_sorted[3][1]

    print(x1, y1)
    print(x2, y2)
    print(x3, y3)
    print(x4, y4)

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

def detect_qrcode(image):
    #detekce QR kodu s OpenCV qr detekci
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("gray", gray)
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(gray)
    return retval, decoded_info, points, straight_qrcode, gray

def detect_qr_codes(image):
    qr_pos_list = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    qr_detector = cv2.QRCodeDetector()
    retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(gray)

    print(retval)

    if retval:
        for i in range(len(points)):
            qr_corners = points[i].astype(int)
            qr_position, corner_coords = find_qr_corners(qr_corners, image.shape)
            qr_pos_list.append(qr_position)

    return qr_pos_list

def detect_3_qr_code():
    led_bright = 0
    while True:
        # Capture a Full HD photo
        photo = take_picture()

        # Detect QR codes in the photo
        qr_codes = detect_qr_codes(photo)

        # Check if exactly 3 QR codes were detected
        if len(qr_codes) == 3:
            print("3 QR codes detected!")
            led_bright = 0
            return photo
        else:
            led_bright += 5
            print(f"Detected {len(qr_codes)} QR codes. Retrying...")

def take_picture():
    #prvni foto
    cap = cv2.VideoCapture(0)
    #full hd rozliseni
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    #ukladani
    result, image = cap.read()
    cap.release()
    return image