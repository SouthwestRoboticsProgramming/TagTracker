import numpy as np
import math

def euler_to_matrix(pitch, yaw, roll):
    x_rad = math.radians(pitch)
    y_rad = math.radians(yaw)
    z_rad = math.radians(roll)

    rot_z = np.identity(4)

    rot_z[0,0] = math.cos(z_rad)
    rot_z[0,1] = -math.sin(z_rad)
    rot_z[1,0] = math.sin(z_rad)
    rot_z[1,1] = math.cos(z_rad)

    rot_x = np.identity(4)

    rot_x[1,1] = math.cos(x_rad)
    rot_x[1,2] = -math.sin(x_rad)
    rot_x[2,1] = math.sin(x_rad)
    rot_x[2,2] = math.cos(x_rad)

    rot_y = np.identity(4)

    rot_y[0,0] = math.cos(y_rad)
    rot_y[0,2] = math.sin(y_rad)
    rot_y[2,0] = -math.sin(y_rad)
    rot_y[2,2] = math.cos(y_rad)

    return np.dot(rot_y, np.dot(rot_x, rot_z))

def apply_translation(matrix, x, y, z):
    matrix[0][3] = x
    matrix[1][3] = y
    matrix[2][3] = z
    return matrix
    
