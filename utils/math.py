import numpy as np


# def calculate_fourth_point(json):
#     json_dict["top_left"][0], json_dict["top_left"][1], json_dict["top_right"][0], json_dict["top_right"][1], \
#     json_dict["bottom_left"][0], json_dict["bottom_left"][1]
#     width = x2 - x1
#     height = y2 - y1
#     fourth_x = x3 + width
#     fourth_y = y3 + height
#     return fourth_x, fourth_


def calculate_fourth_point(json, offset):
    top_left = json["top_left"]
    top_right = json["top_right"]
    bottom_left = json["bottom_left"]
    top_left = np.array(top_left)
    top_right = np.array(top_right)
    bottom_left = np.array(bottom_left)

    # Calculate the width and height of the rectangle
    width = np.linalg.norm(top_right - top_left)
    height = np.linalg.norm(bottom_left - top_left)

    # Calculate the missing bottom-right corner
    bottom_right = top_left + width * (top_right - top_left) / np.linalg.norm(top_right - top_left)
    bottom_right += height * (bottom_left - top_left) / np.linalg.norm(bottom_left - top_left)

    bottom_right += np.array(offset)

    return bottom_right.tolist()

def apply_offset(json_dict, top_l_offs, top_r_offs, bot_l_offs):
    json_dict["top_left"][0] += top_l_offs[0]
    json_dict["top_left"][1] += top_l_offs[1]
    json_dict["top_right"][0] += top_r_offs[0]
    json_dict["top_right"][1] += top_r_offs[1]
    json_dict["bottom_left"][0] += bot_l_offs[0]
    json_dict["bottom_left"][1] += bot_l_offs[1]

    return json_dict
