import numpy as np
from utility import *

# Neat data structure for hit data
class Hit:
    def __init__(self, distance, geometry, intersection):
        self.distance = distance
        self.geometry = geometry
        self.intersection = intersection
        self.normal = geometry.get_normal(intersection)

# incomplete material class        
class Material:
    def __init__(self, reflection, color, checker=False):        
        self.reflection = reflection
        if color:
            self.color = np.array([color[0], color[1], color[2]])
        self.checker = checker # checker pattern texture

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
        c = np.dot(rOsC, rOsC) - (sR ** sR)  # (rO - sC)^2 - sR^2, dot product with itself will square the vector
        discriminant = (b**2) - (4*a*c)

        if discriminant < 0:
            # no solutions
            return None
        else:
            
            # return closest intersection
            d1 = (-b + np.sqrt(discriminant)) / (2*a)
            d2 = (-b - np.sqrt(discriminant)) / (2*a)
            if d1 > 0.001 and d2 > 0.001: # prevent shadow acne by checking above 0.001
                return min(d1, d2)
            else:
                return None

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

        rOY = rO[1] # ray origin y component 
        pOY = pO[1] # plane origin y component
        rDY = rD[1] # ray direction y component

        d = -((rOY - pOY) / rDY)

        #d = -(np.dot(rO, pN) + 1) / np.dot(rD, pN)
        if d > 0.001 and d < 1e6: #  prevent shadow acne by checking above 0.001
          return d

        return None

    def get_color(self, intersection=None):
        if self.material.checker:
            return checker_color(intersection, self.origin)

        return self.material.color

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

        a = length(rD)
        b = 2 * np.dot(rD, rOsC) # b = 2 * rD*rOsC
        c = np.dot(rOsC, rOsC) - (sR ** sR)  # (rO - sC)^2 - sR^2, dot product with itself will square the vector
        discriminant = (b**2) - (4*a*c)

        if discriminant < 0:
            # no solutions
            return None
        else:
            
            # return closest intersection
            d1 = (-b + np.sqrt(discriminant)) / (2*a)
            d2 = (-b - np.sqrt(discriminant)) / (2*a)
            if d1 > 1e-10 and d2 > 1e-10: # prevent shadow acne by checking above 0.001
                return min(d1, d2)
            else:
                return None

        
    def get_color(self, intersection=None):
        return self.material.color

    def get_normal(self, intersection):
        return normalize(intersection - self.position)
    
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersection(self, d):
        return self.origin + self.direction * d

class Scene:
    def __init__(self):
        self.objects = []
        self.lights = []

    def add_object(self, obj):
        self.objects.append(obj)

    def add_light(self, light):
        self.lights.append(light)

    def get_all_scene_objects(self):
        return self.lights + self.objects
    

class Viewport:
    def __init__(self, height_ratio, aspect_ratio, image_width, image_height):
        # we want the viewport to have the same aspect ratio as the image itself
        # the viewport ranges from -1 to 1 in the x-axis
        # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
        # these numbers are arbitrary, but it's a common thing to do
        self.width = 1
        self.height = (1.0 / aspect_ratio)

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
        
        

        
   
        
        
