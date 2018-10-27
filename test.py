import numpy as np
import scipy.optimize
import math


def make_array(ph, d, a, alp):
    A0 = np.array([[math.cos(ph), -math.sin(ph), 0, 0],
                   [math.sin(ph), math.cos(ph), 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])

    A1 = np.array([[1, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 1, d],
                   [0, 0, 0, 1]])

    A2 = np.array([[1, 0, 0, a],
                   [0, 1, 0, 0],
                   [0, 0, 1, 0],
                   [0, 0, 0, 1]])

    A3 = np.array([[1, 0, 0, 0],
                   [0, math.cos(alp), -math.sin(alp), 0],
                   [0, math.sin(alp), math.cos(alp), 0],
                   [0, 0, 0, 1]])
    A = np.dot(A0, A1)
    A = np.dot(A, A2)
    A = np.dot(A, A3)
    return A


def return_final(ph1, ph2, ph3):
    A0 = make_array(math.pi / 2, 0, 0, 0)
    A1 = make_array(-ph1, 0.25, 0, -math.pi / 2)
    A2 = make_array(ph2, 0.1, 0, math.pi / 2)
    A3 = make_array(0, 0.25, 0, math.pi / 2)
    A4 = make_array(-ph3, 0.1, 0, -math.pi / 2)
    A5 = make_array(0, 0.3, 0, 0)

    A = np.dot(A0, A1)
    A = np.dot(A, A2)
    A = np.dot(A, A3)
    A = np.dot(A, A4)
    A = np.dot(A, A5)

    return A


o1 = math.pi/2
o2 = math.pi/2
o3 = math.pi/2

x = 0.1
y = 0.0
z = 0.4

target = [x, y, z]


def fun(x):
    cur = return_final(x[0], x[1], x[2])
    cur = cur.T[3][0:3]
    return np.sqrt(np.sum([(c - t) ** 2 for c, t in zip(cur, target)]))


result = scipy.optimize.minimize(fun=fun, x0=np.array([o1, o2, o3]))

print(result.x * (180/math.pi))
