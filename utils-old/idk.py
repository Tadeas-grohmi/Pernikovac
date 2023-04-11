hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Split the HSV image into channels
h, s, v = cv2.split(hsv)

# Threshold the V channel to create a binary image of the square
thresh = cv2.threshold(v, 195, 255, cv2.THRESH_BINARY)[1]

# Find the contours of the square in the binary image
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


#pocty
max_area = 0
max_contour = None
for contour in contours:
    area = cv2.contourArea(contour)
    if area > max_area:
        max_area = area
        max_contour = contour

x, y, w, h = cv2.boundingRect(max_contour)

#Crop fotky
cropped_img = img[y:y+h, x:x+w]

#detekce rohu
corners = cv2.approxPolyDP(max_contour, 0.01*cv2.arcLength(max_contour,True),True)

# Find the angle between the longest side of the square and the horizontal axis
x1, y1 = corners[0][0]
x2, y2 = corners[1][0]
x3, y3 = corners[2][0]
x4, y4 = corners[3][0]
longest_side = max(np.sqrt((x2-x1)**2 + (y2-y1)**2),
                   np.sqrt((x3-x2)**2 + (y3-y2)**2),
                   np.sqrt((x4-x3)**2 + (y4-y3)**2),
                   np.sqrt((x1-x4)**2 + (y1-y4)**2))
if x2 == x1:
    angle = 0
else:
    angle = np.arctan((y2-y1)/(x2-x1))

# Rotate the image by the angle
rows, cols, _ = img.shape
M = cv2.getRotationMatrix2D((cols/2,rows/2),angle*-4/np.pi,1)
rotated_img = cv2.warpAffine(img,M,(cols,rows))

# Crop the rotated image to the bounding rectangle of the square
x, y, w, h = cv2.boundingRect(max_contour)
cropped_img = rotated_img[y:y+h, x:x+w]

cv2.imshow('Tohle ', cropped_img)


hsv = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
gray_smooth = cv2.GaussianBlur(gray, (15, 25), 0)
thresh = cv2.threshold(gray_smooth, 165, 255, cv2.THRESH_BINARY)[1]
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(cropped_img, contours, -1, (0, 0, 255), 2)
cv2.imshow('Tohle more', cropped_img)




#corners = cv2.approxPolyDP(max_contour, 0.01*cv2.arcLength(max_contour,True),True)

# Sort the corners by their x coordinates
# sorted_corners = sorted(corners, key=lambda x:x[0][0])
#
# # Get the left and right corners
# left_corner = sorted_corners[0][0]
# right_corner = sorted_corners[-1][0]
#
# # Get the top and bottom edges
# if left_corner[1] < right_corner[1]:
#     top_edge = left_corner[1]
#     bottom_edge = right_corner[1]
# else:
#     top_edge = right_corner[1]
#     bottom_edge = left_corner[1]
#
# # Crop the image after the top and bottom edges
# cropped_img2 = cropped_img[top_edge:bottom_edge, :]
#
# cv2.imshow("OUT", cropped_img2)