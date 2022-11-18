import numpy as np
import math

def euler_to_matrix(pitch, yaw, roll):
    # x is pitch
    # y is yaw
    # z is roll

    # Do sin an cosine for all axis
    s_pitch = math.sin(pitch)
    c_pitch = math.cos(pitch)

    s_yaw = math.sin(yaw)
    c_yaw = math.cos(yaw)

    s_roll = math.sin(roll)
    c_roll = math.cos(roll)

    # Initial matrix to edit
    x = np.array(
        [[1, 0, 0, 0],
        [0, c_pitch, -s_pitch, 0],
        [0, s_pitch, c_pitch, 0],
        [0, 0, 0, 1]]
    )

    y = np.array(
        [[c_yaw, 0, s_yaw, 0],
        [0, 1, 0, 0],
        [-s_yaw, 0, c_yaw, 0],
        [0, 0, 0, 1]]
    )

    z = np.array(
        [[c_roll, -s_roll, 0, 0],
        [s_roll, c_roll, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]]
    )

    # Combine indevidual matricies
    return np.dot(z, np.dot(y,x))

def apply_translation(matrix, x, y, z):
    matrix[0][3] = x
    matrix[1][3] = y
    matrix[2][3] = z
    return matrix
    
