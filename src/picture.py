from time import perf_counter
import pygame
from pygame.locals import *
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
MAX_DEPTH = 2

parser = argparse.ArgumentParser(description="A ray tracing program")
parser.add_argument('-width', metavar='w', type=int, help="Width")
parser.add_argument('-height', metavar='h', type=int, help="Height")
args = parser.parse_args()

if args.width:
  WIDTH = args.width
  
if args.height:
  HEIGHT = args.height
    
# treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
# https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
def sphere_intersection(ray, sphere):
  rD = ray.direction
  rO = ray.origin
  sC = sphere.center
  sR = sphere.radius
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
      return rO + (rD * d) # the ray vector that now intersects with a point on the plane

    return None
  
def intersect_objects(ray, scene_objects, x,y):
    
    spheres = scene_objects[0]
    planes = scene_objects[1]
   
    sphere_hit = False
    for sphere in spheres:
        distance = sphere_intersection(ray, sphere)

        if distance > 0:
            sphere_hit = True
            break

    ray_y = (1 + ray.direction[1]) * 0.5 # do some math to get a value between 0 and 1 depending on where at the y-axis we're looking

    # starting with background color
    # notice that we're multiplying the red color with 255, this gives a cool effect
    color = np.array([lerp(0, 255, ray_y), 30, 255]) 

    if sphere_hit:
        color = np.array([lerp(0, 255, ray_y), 0, lerp(0, 255, ray_y)])
    else:
       
      # only 1 plane for now
      plane = planes[0]
      hit_vector = plane_intersection(ray, plane)
       
      if hit_vector is not None:
        # checkerboard pattern logic borrowed from here:
        # https://github.com/carl-vbn/pure-java-raytracer/blob/23300fca6e9cb6eb0a830c0cd875bdae56734eb7/src/carlvbn/raytracing/solids/Plane.java#L32

        point = hit_vector - plane.origin # a point sitting on the plane
        pX = int(point[0])
        pZ = int(point[2])

          # for every other x and z position that is even, color the pixel white, otherwise gray/black
          # might not work behind the camera
        if ((pX % 2 == 0) == (pZ % 2 == 0)):
          color = np.array([255,255,255])
        else:
          color = np.array([30,30,30])


    return color

def process_input(keys, origin):

  if keys[K_w]:
    origin[2] -= 0.1
  elif keys[K_a]:
    origin[0] -= 0.1
  elif keys[K_s]:
    origin[2] += 0.1
  elif keys[K_d]:
    origin[0] += 0.1
  else:
    return (False, origin)
  print(origin)
  return (True, origin)

def main():
    
    pygame.init()

    print("Smooth scale backend:", pygame.transform.get_smoothscale_backend())

    aspect_ratio = float(WIDTH/HEIGHT)
    print("Aspect ratio:", aspect_ratio)

    # Init font for progress text
    font = pygame.font.Font(None, int(aspect_ratio * 15))

    # we want the viewport to have the same aspect ratio as the image itself
    # the viewport ranges from -1 to 1 in the x-axis
    # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
    # these numbers are really arbitrary, but as long as they have the same ratio as the image itself it's fine
    
    viewport_width = 1.0
    viewport_height = (1.0 / aspect_ratio)
    viewport = (-viewport_width, -viewport_height, viewport_width, viewport_height) # LEFT, BOTTOM, RIGHT, TOP

   
    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((WIDTH, HEIGHT, 3))
               
#   framebuffer = pygame.display.set_mode((WIDTH + INSET, HEIGHT + INSET))
    framebuffer = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Backwards ray-tracing")

    render = True
    running = True

    # ray origin
    origin = np.array([0.0, 0.0, 1.0])

    # multi-array, first array is for spheres, second array for planes, third for lights
    scene_objects = []
    scene_objects.append([Sphere(center=np.array([-0.25, 0, -0.15]), radius=0.5),
                          Sphere(center=np.array([0.5, 0.16, 0]), radius=0.2)])
    
    scene_objects.append([Plane(origin=np.array([.0, -1.0 , .0]), normal=np.array([.0, 1.0, .0]))])
    
    scene_objects.append([np.array([-1.0 ,2.0, 0.5])])                      

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
              render, origin = process_input(pygame.key.get_pressed(), origin)


        if render:
            start_counter = perf_counter()
            print(origin)
            # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
            for y_index, y in enumerate(np.linspace(viewport[1], viewport[3], HEIGHT)):
                if (y_index+1) % 10 == 0:
                    text, textpos = progress_text(y_index, font, WIDTH, HEIGHT, INSET)
                    framebuffer.blit(text, textpos)
                    pygame.display.update()
                    
                for x_index, x in enumerate(np.linspace(viewport[0], viewport[2], WIDTH)):
                    
                    # Pygame seems to be using the origin at the upper left corner,
                    # so we have to make y negative in order to respect a right-handed coordinate system (3D)
                    pixel = np.array([x,-y,0]) 
                    direction = normalize(pixel - origin) # figure out the direction of the ray

                    primary_ray = Ray(origin, direction)

                    color = intersect_objects(primary_ray, scene_objects, x_index, y_index)
                    
                    backbuffer[x_index, y_index] = color

            
            temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
            #temp_framebuffer_upscaled = pygame.transform.scale(temp_framebuffer, (1200, 800))

            # create an upscaled version of our frame that is half the size of the window dimensions
            temp_framebuffer_upscaled = pygame.transform.smoothscale(temp_framebuffer, (int(WINDOW_WIDTH/2),int(WINDOW_HEIGHT/2)) )
            center_x, center_y = (int(WINDOW_WIDTH/4), int((WINDOW_HEIGHT/4)))
            
            framebuffer.blit(temp_framebuffer_upscaled, ( (center_x, center_y )))
            pygame.display.update()
            
            end_counter = perf_counter()
            elapsed_seconds = (end_counter - start_counter)
            print("It took", elapsed_seconds, "seconds to render") 
            
        render = False

    
if __name__ == '__main__':
    main()
