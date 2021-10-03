import numpy as np
from utility import *

# incomplete material class        
class Material:
    def __init__(self, reflection, color):        
        self.reflection = reflection
        self.color = np.array([color[0], color[1], color[2]]) if color else None

class Intersectable:
    
    def intersect_test(self, ray):
        pass

    def get_color(self, intersection=None):
        pass

    def get_normal(self):
        pass
        
class Sphere(Intersectable):
    def __init__(self, center, radius, material):
        self.center = np.array(center) # 3D coordinates of sphere center
        self.radius = radius
        self.material = material

    def get_normal(self, intersection):
        return normalize(intersection - self.center)
        
    def get_color(self, intersection=None):
        return self.material.color

    # treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
    # https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin
        sC = self.center
        sR = self.radius
        rOsC = rO - sC # origin - sphere

        #a = length(rD)
        b = 2 * np.dot(rD, rOsC) # b = 2 * rD*rOsC
        c = np.dot(rOsC, rOsC) - (sR ** sR)  # (rO - sC)^2 - sR^2, dot product with itself will square the vector
        discriminant = (b**2) - (4*c)

        if discriminant > 0:
            # solutions found
            sqrt = np.sqrt(discriminant)
            d1 = (-b + sqrt) / (2)
            d2 = (-b - sqrt) / (2)
            if d1 > 0.001 and d2 > 0.001: # prevent shadow acne by checking above 0.001
                return min(d1, d2)
            
        return None
    
class Plane(Intersectable):
    def __init__(self, origin, normal, material):
        self.origin = np.array(origin)
        self.normal = np.array(normal)
        self.material = material
        self.checker = False if self.material.color else True            

    def get_normal(self, intersection):
        return normalize(intersection - self.origin)
        
    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin

        pN = self.normal
        pO = self.origin

        rOY = rO[1] # ray origin y component 
        pOY = pO[1] # plane origin y component
        rDY = rD[1] # ray direction y component

        d = -((rOY - pOY) / rDY)

        #d = -(np.dot(rO, pN) + 1) / np.dot(rD, pN)
        
        if d > 0.001 and d < 1e6: #  prevent shadow acne by checking above 0.001
          return d

        return None

    def get_color(self, intersection=None):
        if self.checker:
            return self.checker_color(intersection)

        return self.material.color

    # checkerboard pattern logic borrowed from here:
    # https://github.com/carl-vbn/pure-java-raytracer/blob/23300fca6e9cb6eb0a830c0cd875bdae56734eb7/src/carlvbn/raytracing/solids/Plane.java#L32
    def checker_color(self, intersection):
        point = intersection - self.origin
        
        pX = int(point[0])
        pZ = int(point[2])

        # for every other x and z position that is even, color the pixel white, otherwise beige
        if ((pX % 2 == 0) == (pZ % 2 == 0)):
            return np.array([252, 204, 116])
        else:
            return np.array([30,30,30])

class Light(Intersectable):
    def __init__(self, position, intensity, material):
        self.position = np.array(position)
        self.radius = 0.01
        self.intensity = intensity
        self.material = material

    # treat light points as a sphere
    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin
        sC = self.position
        sR = self.radius
        rOsC = rO - sC # origin - light ball position

        #a = length(rD)
        b = 2 * np.dot(rD, rOsC) # b = 2 * rD*rOsC
        c = np.dot(rOsC, rOsC) - (sR ** sR)  # (rO - sC)^2 - sR^2, dot product with itself will square the vector
        discriminant = (b**2) - (4*c)

        if discriminant > 0:
            # solutions found
            sqrt = np.sqrt(discriminant)
            d1 = (-b + sqrt) / (2)
            d2 = (-b - sqrt) / (2)
            if d1 > 0.001 and d2 > 0.001: # prevent shadow acne by checking above 0.001
                return min(d1, d2)
            
        return None

        
    def get_color(self, intersection=None):
        return self.material.color

    def get_normal(self, intersection):
        return normalize(intersection - self.position)
