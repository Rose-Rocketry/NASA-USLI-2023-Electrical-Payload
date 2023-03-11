import math


def dot(a, b):
    return sum(an * bn for an, bn in zip(a, b))


def minus(a, b):
    return tuple(an - bn for an, bn in zip(a, b))


def get_angle(vector, x_basis, y_basis):
    angle = math.atan2(
        dot(vector, y_basis),
        dot(vector, x_basis),
    )
    return angle
