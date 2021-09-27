import numpy as np
from utility import *

class Material:
    def __init__(self, reflection, ambient, color):        
        self.reflection = reflection
        self.ambient = ambient
        self.color = np.array([color[0], color[1], color[2]])

class Intersectable:
    
    def intersect_test(self, ray):
        pass
        
class Sphere(Intersectable):
    def __init__(self, center, radius, material):
        self.center = center # 3D coordinates of sphere center
        self.radius = radius
        self.material = material

    # treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
    # https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
    def intersect_test(self, ray):
          rD = ray.direction
          rO = ray.origin
          sC = self.center
          sR = self.radius
          rOsC = rO-sC # origin - sphere
          unit_rOsC = normalize(rOsC)

          # determines if the ray direction is looking at the sphere, temporary code
          if np.dot(unit_rOsC, rD) > 0:
            return -1.0

          a = 1 # a = ||rD|| = 1 because rD is a unit vector
          b = 2 * np.dot(rD, rOsC) # b = 2 * rD (rO - sC)
          c = np.dot(rOsC, rOsC) - np.dot(sR, sR) # (rO - sC)^2 - sR^2, dot product with itself will square the vector
          discriminant = (b**2) - (4*c)

          if discriminant < 0:
            # no solutions
            return -1.0
          else:
            # return closest intersection

            d1 = (-b + np.sqrt(discriminant)) / 2
            d2 = (-b - np.sqrt(discriminant)) / 2
            if d1 > 0 and d2 > 0:
              return min(d1, d2)
            else:
              return -1.0

class Plane(Intersectable):
    def __init__(self, origin, normal):
        self.origin = origin
        self.normal = normal

    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin

        pN = self.normal
        pO = self.origin

        #d = -(np.dot(rO, pN) + 1) / np.dot(rD, pN)

        rOY = rO[1] # ray origin y component 
        pOY = pO[1] # plane origin y component
        rDY = rD[1] # ray direction y component

        d = -((rOY - pOY) / rDY)
        if d > 0 and d < 1e6:        
            return d # scaling factor for direction

        return -1.0

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

class Light:
    def __init__(self, position, intensity):
        self.position = position
        self.intensity = intensity
        
        
