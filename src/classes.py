import numpy as np
from utility import *


class Hit:
    def __init__(self, t=None, point=None, normal=None):
        self.t = t
        self.point = point
        self.normal = normal

        
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
        self.center = np.array(center) # 3D coordinates of sphere center
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
              return min(d1, d2) # return the closest intersection (this should be the front-face of the sphere)
            else:
              return -1.0

class Plane(Intersectable):
    def __init__(self, origin, normal):
        self.origin = np.array(origin)
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

    def surface_color(self, intersection):
        # checkerboard pattern logic borrowed from here:
        # https://github.com/carl-vbn/pure-java-raytracer/blob/23300fca6e9cb6eb0a830c0cd875bdae56734eb7/src/carlvbn/raytracing/solids/Plane.java#L32

        point = intersection - self.origin # get the point sitting on the plane by taking the scaled ray  minus plane origin
        pX = int(point[0])
        pZ = int(point[2])

        # for every other x and z position that is even, color the pixel white, otherwise orange
        # might not work behind the camera
        if ((pX % 2 == 0) == (pZ % 2 == 0)):
          return np.array([252, 204, 116])
        else:
          return np.array([30,30,30])

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersection(self, d):
        return self.origin + (self.direction * d)

class Light:
    def __init__(self, position, intensity):
        self.position = np.array(position)
        self.intensity = intensity

class Viewport:
    def __init__(self, aspect_ratio, image_width, image_height):
        # we want the viewport to have the same aspect ratio as the image itself
        # the viewport ranges from -1 to 1 in the x-axis
        # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
        # these numbers are arbitrary, but it's a common occurrence
        self.width = 1
        self.height = (1.0 / aspect_ratio)

        viewport = (-self.width, -self.height, self.width, self.height) # LEFT, BOTTOM, RIGHT, TOP
        self.coordinates = [np.linspace(viewport[1], viewport[3], image_height), np.linspace(viewport[0], viewport[2], image_width)]
        
class Camera:
    def __init__(self, position, vertical_fov, viewport):
        self.position = np.array(position)
        self.viewport = viewport
        
        
        

        
   
        
        
