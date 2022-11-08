import math
import numpy as np
import numpy.matlib as npm

def matrixToQuat(m):
    r11 = m[0][0]; r12 = m[0][1]; r13 = m[0][2]
    r21 = m[1][0]; r22 = m[1][1]; r23 = m[1][2]
    r31 = m[2][0]; r32 = m[2][1]; r33 = m[2][2]

    q0 = math.sqrt((1 + r11 + r22 + r33) / 4)
    q1 = math.sqrt((1 + r11 - r22 - r33) / 4)
    q2 = math.sqrt((1 - r11 + r22 - r33) / 4)
    q3 = math.sqrt((1 - r11 - r22 + r33) / 4)

    if q0 > q1 and q0 > q2 and q0 > q3:
        q1 = (r32 - r23) / (4 * q0)
        q2 = (r13 - r31) / (4 * q0)
        q3 = (r21 - r12) / (4 * q0)
    elif q1 > q0 and q1 > q2 and q1 > q3:
        q0 = (r32 - r23) / (4 * q1)
        q2 = (r12 + r21) / (4 * q1)
        q3 = (r13 + r31) / (4 * q1)
    elif q2 > q0 and q2 > q1 and q2 > q3:
        q0 = (r13 - r31) / (4 * q2)
        q1 = (r12 + r21) / (4 * q2)
        q3 = (r23 + r32) / (4 * q2)
    elif q3 > q0 and q3 > q1 and q3 > q2:
        q0 = (r21 - r12) / (4 * q3)
        q1 = (r13 + r31) / (4 * q3)
        q2 = (r23 + r32) / (4 * q3)

    return (q0, q1, q2, q3)

def invertQuat(q):
    return (q[0], -q[1], -q[2], -q[3])

def quatToAxisAngle(q):
    if q[0] == 1:
        return (0, (1, 0, 0))

    theta = 2 * math.acos(q[0])

    s = math.sin(theta / 2)
    x = q[1] / s
    y = q[2] / s
    z = q[3] / s

    return (theta, (x, y, z))

def quatToFUL(q):
    x, y, z, w = q
    
    forward = (
        2 * (x * z + w * y),
        2 * (y * z - w * x),
        1 - 2 * (x * x + y * y)
    )

    up = (
        2 * (x * y - w * z),
        1 - 2 * (x * x + z * z),
        2 * (y * z + w * x)
    )

    left = (
        1 - 2 * (y * y + z * z),
        2 * (x * y + w * z),
        2 * (x * z - w * y)
    )

    return (forward, up, left)


def averageQuats(quats_to_average):
    # Extract number of quaternions
    number_of_quats = quats_to_average.shape[0]
    a = npm.zeros(shape=(4,4))

    for i in range(number_of_quats):
        q = quats_to_average[i,:]
        # Multiply q with its transposed version of q' and add a
        a = np.outer(q,q) + a

    # Scale
    a = (1.0/number_of_quats) * a

    # Compute eigenvalues and -vectors
    eigenValues, eigenVectors = np.linalg.eig(a)

    # Sort by largest eigenvalue
    eigenVectors = eigenVectors[:, eigenValues.argsort()[::-1]]

    # Return the real part of the largest eigenvector
    return np.real(eigenVectors[:,0].A1)

