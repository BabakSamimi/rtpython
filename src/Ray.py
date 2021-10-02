import numpy as np
from utility import *
from Intersectable import *

# Neat data structure for hit data
class Hit:
    def __init__(self, distance, geometry, intersection):
        self.distance = distance
        self.geometry = geometry
        self.intersection = intersection
        self.normal = geometry.get_normal(intersection)
    
class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def intersection(self, d):
        return self.origin + self.direction * d

def intersect_objects(ray, scene_objects):

    solutions = []
    nearest_solution = np.inf # apparently this exists!
    nearest_geometry = None
    
    # Find the cloests intersection of every intersectable object
    
    for obj in scene_objects:
      solutions.append(obj.intersect_test(ray))

    # iterate through every intersection and save the closest one and associate it with the relevant object
    for idx, solution in enumerate(solutions):
      # keep the solution that has the closest distance to ray origin
      if solution and solution < nearest_solution:
        nearest_solution = solution
        nearest_geometry = scene_objects[idx]    

    if nearest_geometry:
      return Hit(nearest_solution, nearest_geometry, ray.intersection(nearest_solution))
    
    return None

def compute_color(ray, hit_data, scene):

    geometry = hit_data.geometry

    if type(geometry) is Light:
      return geometry.get_color()

    intersection = ray.intersection(hit_data.distance)    
    # nudge it away a little from the intersection point
    intersection_moved = intersection + (1e-7 * hit_data.normal) # NOTE, this is not a normalized vector

    lightning = 0.0 # start with an arbitrary ambient light value
    color = geometry.get_color(intersection)

    # lightning computation from point-based lights
    for light in scene.lights:
      l_dir = light.position - intersection_moved

      # shadows
      shadow_ray = Ray(intersection_moved, normalize(l_dir))
      shadow_data = trace_ray(shadow_ray, scene.objects)

      # check if our shadow ray hit something
      # check if hit distance is less than the length between the light and the original intersection
      if shadow_data and shadow_data.distance < length(light.position - intersection_moved):
        lightning = 0.0
      else:
        # We're modeling a spherical light source
        # thus our attenuation can be based on, for instance, it's distance
        sqrt_dist = np.sqrt(length(l_dir))
        lightning += light.intensity / (4*np.pi*sqrt_dist) # Inverse-square law

        # because of my broken logic for Planes,
        # this isn't really possibly to calculate on planes at the moment
        if type(geometry) is Sphere:
          normal_ratio = clamp(np.dot(hit_data.normal, l_dir), 0.0, np.inf)
          lightning *= normal_ratio

    return color*lightning

def trace_ray(ray, scene_objects):  

    hit_data = intersect_objects(ray, scene_objects)
  
    return hit_data
