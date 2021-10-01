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

    rOY = rO[1] # ray origin y component 
    pOY = pO[1] # plane origin y component
    rDY = rD[1] # ray direction y component
    
    d = -((rOY - pOY) / rDY)
    
    #d = -(np.dot(rO, pN) + 1) / np.dot(rD, pN)
    
    if d > 0.001 and d < 1e6: #  prevent shadow acne by checking above 0.001
      return d

    return None
  
def intersect_objects(ray, scene_objects):

    spheres = scene_objects[0]
    planes = scene_objects[1]
    lights = scene_objects[2]
    
    # sphere intersection
    solutions = []
    nearest_solution = np.inf # apparently this exists!
    nearest_geometry = None
    
    # Find intersection of every sphere and the plane
    # Save the closest one

    # Save every intersection
    for sphere in spheres:
      solutions.append(sphere.intersect_test(ray))

    #for light in lights:
      #solutions.append(light.intersect_test(ray))

    # iterate through every intersection and save the closest one and associate it with the relevant sphere
    for idx, solution in enumerate(solutions):
      # keep the solution that has the closest distance to ray origin
      if solution and solution < nearest_solution:
        nearest_solution = solution
        nearest_geometry = spheres[idx]    

    #plane intersection
    plane = planes[0]
    plane_distance = plane.intersect_test(ray)

    if plane_distance:
      if plane_distance < nearest_solution:
        return Hit(plane_distance, plane, ray.intersection(plane_distance))
      else:
        return Hit(nearest_solution, nearest_geometry, ray.intersection(nearest_solution))
    elif nearest_geometry:
      return Hit(nearest_solution, nearest_geometry, ray.intersection(nearest_solution))
    
    return None

def trace_ray(ray, scene_objects):  

  hit_data = intersect_objects(ray, scene_objects)
  
  return hit_data

def compute_color(ray, hit_data, scene_objects):
  
  spheres = scene_objects[0]
  planes = scene_objects[1]
  lights = scene_objects[2]

  geometry = hit_data.geometry

  color = np.zeros((3))
  lightning = 0.0 # start with an arbitrary ambient light value
  
  intersection = ray.intersection(hit_data.distance)
    
  # nudge it away a little from the intersection point
  intersection_moved = intersection + (0.0001 * hit_data.normal) # NOTE, this is not a normalized vector

  color = geometry.get_color(intersection)

  # lightning computation from point-based lights
  for light in lights:
    
    l_dir = light.position - intersection_moved
    
    # shadows
    shadow_ray = Ray(intersection, normalize(l_dir))
    shadow_data = trace_ray(shadow_ray, scene_objects)

    if shadow_data and shadow_data.distance > 0.0:
      lightning += 0.05 # softer shadow, better than 0.0
    else: 
      sqrt_dist = np.sqrt(length(l_dir))
      lightning += light.intensity / (4*np.pi*sqrt_dist) # Inverse-square law      

  return color*lightning
       
def main():
    
    pygame.init()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, int(30))
    
    print("Smooth scale backend:", pygame.transform.get_smoothscale_backend())

    aspect_ratio = float(WIDTH/HEIGHT)
    print("Aspect ratio:", aspect_ratio)

    camera = Camera((0.0, 2.0, 8.0), (0.0, 0.0, 0.0), 90, aspect_ratio, WIDTH, HEIGHT)
    
    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((WIDTH, HEIGHT, 3))
               
    framebuffer = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT)) #flags=pygame.FULLSCREEN)
    pygame.display.set_caption("Backwards ray-tracing")

    render = True
    running = True

    # multi-array, first array is for spheres, second array for planes, third for lights
    scene_objects = []
    scene_objects.append([Sphere(center=(0.0, 0.0, -1.0), radius=1.0, material=Material(1.0, (255, 25, 50))),
                          Sphere(center=(-1.0, 1.0, -4.0), radius=2.0, material=Material(0.0, (30, 255, 100))),
                          Sphere(center=(3.0, 0.0, -1.0), radius=0.1, material=Material(0.4, (30, 50, 255)))])

    scene_objects.append([Plane(origin=(0.0, -1.0 , 0.0), normal=(.0, 1.0, .0), material=Material(0.0, None, True))])
    
    scene_objects.append([Light(position=(0.0, 1.0, 1.0), intensity=10.0, material=(0.0, (255,255,255)))])

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
            
            if hit_data:
              
              color = compute_color(primary_ray, hit_data, scene_objects)
              
              color[0] = clamp(color[0], 0, 255)
              color[1] = clamp(color[1], 0, 255)
              color[2] = clamp(color[2], 0, 255)            

            backbuffer[x_index, y_index] = color


        temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
        #temp_framebuffer_upscaled = pygame.transform.scale(temp_framebuffer, (int(WINDOW_WIDTH/2),int(WINDOW_HEIGHT/2)))

        # create an upscaled version of our frame that is half the size of the window dimensions
        temp_framebuffer_upscaled = pygame.transform.smoothscale(temp_framebuffer, (int(WINDOW_WIDTH),int(WINDOW_HEIGHT)) )
        center_x, center_y = (int(WINDOW_WIDTH/4), int((WINDOW_HEIGHT/4)))

        text, textrect = print_camera_info(camera, font)
        
        framebuffer.blit(temp_framebuffer_upscaled, ( (0, 0)))        
        framebuffer.blit(text, textrect)
        pygame.display.update()

        end_counter = perf_counter()
        elapsed_seconds = (end_counter - start_counter)
        print("It took", elapsed_seconds, "seconds to render")
        render = False
        
      running, render, camera = process_events(camera)
    

    
if __name__ == '__main__':
    main()
