
def calculate_fourth_point(x1, y1, x2, y2, x3, y3):
    width = x2 - x1
    height = y2 - y1
    fourth_x = x3 + width
    fourth_y = y3 + height
    return fourth_x, fourth_y