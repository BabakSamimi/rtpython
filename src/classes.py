import numpy as np
from utility import *


class Hit:
    def __init__(self, distance=None, geometry=None, normal=None):
        self.distance = distance
        self.geometry = geometry
        self.normal = normal
        self.hit = distance > 0
        
class Material:
    def __init__(self, reflection, ambient, color, checker=False):        
        self.reflection = reflection
        self.ambient = ambient
        if color:
            self.color = np.array([color[0], color[1], color[2]])
        self.checker = checker # checker pattern texture

# checkerboard pattern logic borrowed from here:
# https://github.com/carl-vbn/pure-java-raytracer/blob/23300fca6e9cb6eb0a830c0cd875bdae56734eb7/src/carlvbn/raytracing/solids/Plane.java#L32
def checker_color(intersection, origin):
    point = intersection - origin # get the point sitting on the plane by taking the scaled ray  minus plane origin
    pX = int(point[0])
    pZ = int(point[2])

    # for every other x and z position that is even, color the pixel white, otherwise beige
    # might not work behind the camera
    if ((pX % 2 == 0) == (pZ % 2 == 0)):
        return np.array([252, 204, 116])
    else:
        return np.array([30,30,30])

class Intersectable:
    
    def intersect_test(self, ray):
        pass

    def get_color(self, intersection):
        pass

    def get_normal(self, intersection):
        pass
        
class Sphere(Intersectable):
    def __init__(self, center, radius, material):
        self.center = np.array(center) # 3D coordinates of sphere center
        self.radius = radius
        self.material = material

    def get_normal(self, intersection):
        return normalize(intersection - self.center)
        
    def get_color(self, intersection):
        if self.material.checker:
            return checker_color(intersection, self.center)

        return self.material.color

    # treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
    # https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin
        sC = self.center
        sR = self.radius
        rOsC = rO - sC # origin - sphere

        a = length(rD)
        b = 2 * np.dot(rD, rOsC) # b = 2 * rD*rOsC
        c = np.dot(rOsC, rOsC) - sR ** sR  # (rO - sC)^2 - sR^2, dot product with itself will square the vector
        discriminant = (b**2) - (4*a*c)

        if discriminant < 0:
            # no solutions
            return -1.0
        else:
            # return closest intersection

            d1 = (-b + np.sqrt(discriminant)) / (2*a)
            d2 = (-b - np.sqrt(discriminant)) / (2*a)
            if d1 > 0 and d2 > 0:
                return min(d1, d2)
            else:
                return -1.0

class Plane(Intersectable):
    def __init__(self, origin, normal, material):
        self.origin = np.array(origin)
        self.normal = np.array(normal)
        self.material = material

    def get_normal(self, intersection):
        return normalize(intersection - self.origin)
        
    def intersect_test(self, ray):
        rD = ray.direction
        rO = ray.origin

        pN = self.normal
        pO = self.origin

        #rOY = rO[1] # ray origin y component 
        #pOY = pO[1] # plane origin y component
        #rDY = rD[1] # ray direction y component

        #d = -((rOY - pOY) / rDY)
        d = -(np.dot(rO, pN)) / np.dot(rD, pN)
        
        if d > 0 and d < 1e6:        
            return d

        return -1.0

    def get_color(self, intersection):
        if self.material.checker:
            return checker_color(intersection, self.origin)

        return self.material.color


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersection(self, d):
        return self.origin + self.direction * d

class Light:
    def __init__(self, position, intensity):
        self.position = np.array(position)
        self.intensity = intensity        

    def calculate_intensity(self, luminance, light_dir, surf_norm):
        return self.intensity * luminance / (length(surf_norm) * length(light_dir))

class Viewport:
    def __init__(self, height_ratio, aspect_ratio, image_width, image_height):
        # we want the viewport to have the same aspect ratio as the image itself
        # the viewport ranges from -1 to 1 in the x-axis
        # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
        # these numbers are arbitrary, but it's a common thing to do
        self.width = 1
        self.height = (1.0 / aspect_ratio) * height_ratio

        viewport = (-self.width, -self.height, self.width, self.height) # LEFT, BOTTOM, RIGHT, TOP
        
        self.coordinates = [np.linspace(viewport[1], viewport[3], image_height), np.linspace(viewport[0], viewport[2], image_width)]
        
class Camera:
    def __init__(self, position, look_to, vertical_fov, aspect_ratio, image_width, image_height):

        # this FOV code might not work properly at the moment
        angle = np.deg2rad(vertical_fov)
        h = np.tan(angle/2)       
        
        self.position = np.array(position)
        self.look_to = np.array(look_to)
        self.up = np.array([0.0, 1.0, 0.0])        
        
        self.z = normalize(self.position - self.look_to) # unit vector at where we are looking
        self.x = normalize(np.cross(self.up, self.z))
        self.y = np.cross(self.z, self.x)

        self.yaw = 0.0
        self.pitch = 0.0
        
        self.viewport = Viewport(h, aspect_ratio, image_width, image_height)
        
        

        
   
        
        
