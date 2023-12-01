import cv2
import numpy as np

def transform_image(image, corners):
    # Define the destination points after transformation
    dest_points = np.array([[0, 0], [210, 0], [0, 200]], dtype=np.float32)

    # Calculate the transformation matrix
    matrix = cv2.getAffineTransform(corners, dest_points)

    # Apply the transformation
    transformed_image = cv2.warpAffine(image, matrix, (210, 200))

    return transformed_image

# Example usage
# Load your original image
original_image = cv2.imread('your_image_path.jpg')

# Define the original image corners (X, Y coordinates)
original_corners = np.array([[right_top_x, right_top_y], [left_top_x, left_top_y], [right_bottom_x, right_bottom_y]], dtype=np.float32)

# Transform the image
transformed_image = transform_image(original_image, original_corners)

# Display the original and transformed images
cv2.imshow('Original Image', original_image)
cv2.imshow('Transformed Image', transformed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()