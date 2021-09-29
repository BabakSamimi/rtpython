# TODO:
# Create camera class, seperate the distinction between
# camera position and origin of world
# movement doesn't work properly because of this

from time import perf_counter
import pygame
import numpy as np
import argparse

from utility import *
from classes import *

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

# WIDTH AND HEIGHT ARE FOR THE TIME BEING USED AS DIMENSIONS FOR OUR VIEWPORT (WHICH THEN GETS SCALED UP)
WIDTH = 300
HEIGHT = 200
INSET = 200
MAX_DEPTH = 10

parser = argparse.ArgumentParser(description="A ray tracing program")
parser.add_argument('-width', metavar='w', type=int, help="Width")
parser.add_argument('-height', metavar='h', type=int, help="Height")
args = parser.parse_args()

if args.width:
  WIDTH = args.width
  
if args.height:
  HEIGHT = args.height
    
# https://en.wikipedia.org/wiki/Line-plane_intersection          
def plane_intersection(ray, plane):
    rD = ray.direction
    rO = ray.origin
    
    pN = plane.normal
    pO = plane.origin

    #d = -(np.dot(rO, pN) + 1) / np.dot(rD, pN)

    rOY = rO[1] # ray origin y component 
    pOY = pO[1] # plane origin y component
    rDY = rD[1] # ray direction y component
    
    d = -((rOY - pOY) / rDY)
    if d > 0 and d < 1e6:
      return d

    return -1.0

def light_intersection(intersection, light):
    intersection = ray.origin + (ray.direction * distance)
    surface_normal = normalize(intersection - sphere.center)
    surface_normal_shifted = intersection + 1e-6 * surface_normal

    for light in lights:
      intersection_to_light = normalize(light.position - surface_normal_shifted)
      i_l_normal = normalize(intersection_to_light)
      shadow_ray = Ray(intersection, intersection_to_light)
      luminance = int(np.dot(light.position, surface_normal_shifted))
      if luminance < 0:
        color -= np.zeros((3))

      #color = intersect_objects(shadow_ray, scene_objects, depth)

  
def intersect_objects(ray, scene_objects, depth):

    if depth >= MAX_DEPTH:
      return (None, None)
  
    depth += 1

    #color = np.zeros((3)) 

    spheres = scene_objects[0]
    planes = scene_objects[1]
    lights = scene_objects[2]

    # sphere intersection
    sphere_hit = False
    
    for sphere in spheres:
      distance = sphere.intersect_test(ray)
        
      if distance > 0:          
        sphere_hit = True

        return (sphere, distance)                              

    if not sphere_hit:            
      # plane intersection
      plane = planes[0]
      distance = plane_intersection(ray, plane)
      #distance = plane.intersect_test(ray) # this is bugged?! doesn't even work even if it's the exact same as the plane_intersection function

      if distance > 0:
        return (plane, distance)

    return (None, -1.0)

def trace_ray(ray, scene_objects):  

  geometry, distance = intersect_objects(ray, scene_objects, 0)

  hit_data = Hit(distance, geometry)

  # change this logic later
  if type(geometry) is Plane:
    hit_data.normal = normalize(ray.intersection(distance))
  elif type(geometry) is Sphere:
    hit_data.normal = normalize(ray.intersection(distance) - geometry.center)
  
  return hit_data

def compute_color(ray, hit_data, scene_objects):
  
  spheres = scene_objects[0]
  planes = scene_objects[1]
  lights = scene_objects[2]

  color = np.zeros((3))
  lightning = 0.3
  
  intersection = ray.intersection(hit_data.distance)
  # nudge it away a little from the intersection point
  sN_direction = intersection + 0.0001 * hit_data.normal # surface normal direction (NOTE, this is not a normalized vector)

  color = hit_data.geometry.get_color(intersection)

  # lightning computation from point-based lights
  for light in lights:
    sN = normalize(sN_direction)
    l_direction = light.position - sN_direction

    luminance = np.dot(l_direction, sN)
    # if the surface normal is facing away from the light
    # then 
    if luminance > 0.0:
      lightning += light.calculate_intensity(luminance, l_direction, sN)
      clamp(lightning, 0.0, 1.0)

  return color*lightning
       
            
def main():
    
    pygame.init()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, int(30))
    
    print("Smooth scale backend:", pygame.transform.get_smoothscale_backend())

    aspect_ratio = float(WIDTH/HEIGHT)
    print("Aspect ratio:", aspect_ratio)

    camera = Camera((0.3, 0.3, 2.0), (0.0, 0.0, 0.0), 90, aspect_ratio, WIDTH, HEIGHT)
    
    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((WIDTH, HEIGHT, 3))
               
    framebuffer = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags=pygame.FULLSCREEN)
    pygame.display.set_caption("Backwards ray-tracing")

    render = True
    running = True

    # multi-array, first array is for spheres, second array for planes, third for lights
    scene_objects = []
    scene_objects.append([Sphere(center=(-1.5, -0.2, -0.5), radius=0.1, material=Material(1.0, 0.0, (255, 25, 55))),
                          Sphere(center=(0.0, 0.2, -.5), radius=0.2, material=Material(0.0, 0.4, (30, 255, 90)))])

    scene_objects.append([Plane(origin=(.0, -1.0 , .0), normal=np.array([.0, 1.0, .0]), material=Material(0.0, 1.0, (0,0,0)))])
    
    scene_objects.append([Light(position=(-3.0, 0.0, 0.0), intensity=1.0),
                          Light(position=(1.0, 1.0, -1.0), intensity=0.5)])

    while running:               
      
      if render:
        start_counter = perf_counter()
        # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
        for y_index, y in enumerate(camera.viewport.coordinates[0]):
          if (y_index+1) % 10 == 0:
            text, textrect = progress_text(y_index, font, WIDTH, HEIGHT)
            framebuffer.blit(text, textrect)
            pygame.display.update()

          for x_index, x in enumerate(camera.viewport.coordinates[1]):

            # Pygame seems to be using the origin at the upper left corner,
            # so we have to make y negative in order to respect a right-handed coordinate system (3D)
            pixel = np.array([x,-y,0]) 
            direction = normalize(pixel - camera.z) # figure out the direction of the ray

            color = np.zeros((3))
            
            primary_ray = Ray(camera.position, direction)
            hit_data = trace_ray(primary_ray, scene_objects)
            
            if hit_data.hit:
              color = compute_color(primary_ray, hit_data, scene_objects)
              
              # clamping because nothing ever works
              color[0] = clamp(color[0], 0, 255)
              color[1] = clamp(color[1], 0, 255)
              color[2] = clamp(color[2], 0, 255)              

            backbuffer[x_index, y_index] = color


        temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
        #temp_framebuffer_upscaled = pygame.transform.scale(temp_framebuffer, (int(WINDOW_WIDTH/2),int(WINDOW_HEIGHT/2)))

        # create an upscaled version of our frame that is half the size of the window dimensions
        temp_framebuffer_upscaled = pygame.transform.smoothscale(temp_framebuffer, (int(WINDOW_WIDTH/2),int(WINDOW_HEIGHT/2)) )
        center_x, center_y = (int(WINDOW_WIDTH/4), int((WINDOW_HEIGHT/4)))

        framebuffer.blit(temp_framebuffer_upscaled, ( (center_x, center_y)))
        text, textrect = print_camera_info(camera, font)
        framebuffer.blit(text, textrect)
        pygame.display.update()

        end_counter = perf_counter()
        elapsed_seconds = (end_counter - start_counter)
        print("It took", elapsed_seconds, "seconds to render")
        render = False
        
      running, render, camera = process_events(camera)
    

    
if __name__ == '__main__':
    main()
