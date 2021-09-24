class Sphere:
    def __init__(self, center, radius):
        self.center = center # 3D coordinates of sphere center
        self.radius = radius
        #self.color = color

class Plane:
    def __init__(self, origin, normal):
        self.origin = origin
        self.normal = normal

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
