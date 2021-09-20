from time import perf_counter
import pygame
import numpy as np
import argparse

WIDTH = 300
HEIGHT = 200
MARGIN = 200
MAX_DEPTH = 2


parser = argparse.ArgumentParser(description="A ray tracing program")
parser.add_argument('-width', metavar='w', type=int, help="Width")
parser.add_argument('-height', metavar='h', type=int, help="Height")
args = parser.parse_args()

if args.width:
  WIDTH = args.width
  
if args.height:
  HEIGHT = args.height
        
class Sphere:
    def __init__(self, center, radius):
        self.center = center # 3D coordinates of sphere center
        self.radius = radius
        #self.color = color

class Plane:
    def __init__(self, normal):
        self.normal = normal

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction


# get a value between a and b depending on t (or just get a or b)
def lerp(a, b, t):
    return (1-t) * a + t * b

def normalize(vec):
    # divides each component of vec with its length, normalizing it
    return vec / np.linalg.norm(vec)
    
def progress_text(y_index, font):
  percentage = ((y_index+1) / (HEIGHT)) * 100
  progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
  color = (lerp(0, 255, y_index/(WIDTH-1)), 0, 255)
  text = font.render(progress, False, color, (0,0,0))
  textpos = text.get_rect(centerx=MARGIN/2 + 60, centery=MARGIN/2 - 15)
  return (text, textpos)
    
# treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
# https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
# returns closest intersection
def sphere_intersection(ray, sphere):
    rD = ray.direction
    rO = ray.origin
    sC = sphere.center
    sR = sphere.radius
    rOsC = rO-sC # origin - sphere center gives us where the sphere center will be located relative to ray origin
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
    p_normal = plane.normal

    # adding + 1 for now, otherwise d will always be 0
    d = -(np.dot(rO, p_normal) + 1) / np.dot(rD, p_normal)

    return d > 0

def intersect_objects(ray, objects):
    
    spheres = objects[0]
    planes = objects[1]

    # only 1 plane for now
    plane_hit = plane_intersection(ray, planes[0])

    sphere_hit = False
    for sphere in spheres:
        distance = sphere_intersection(ray, sphere)

        if distance > 0:
            sphere_hit = True
            break

    ray_y = (1 + ray.direction[1]) * 0.5 # do some math to get a value between 0 and 1 depending on where at the y-axis we're looking

    color = np.array([lerp(0, 255, ray_y)*255, 30, 255]) # notice that we're multiplying the red color with 255, this gives a cool effect

    if plane_hit:
        color = np.array([lerp(0, 255, ray_y), lerp(0, 255, ray_y), lerp(0, 255, ray_y)])

    if (sphere_hit):
        color = np.array([lerp(0, 255, ray_y), 0, lerp(0, 255, ray_y)])

    return color


def main():
    
    pygame.init()

    aspect_ratio = float(WIDTH/HEIGHT) # 3:2 aspect ratio for now
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
               
    framebuffer = pygame.display.set_mode((WIDTH + MARGIN, HEIGHT + MARGIN))
    pygame.display.set_caption("Backwards ray-tracing")

    render = True
    running = True
    
    origin = np.array([0,0,1])

    # multi-array, first array is for spheres, second array for planes
    scene_objects = [ [Sphere(np.array([.0, 0, -1]), 0.5),
                       Sphere(np.array([0.8, 0.5, -1]), 0.2)],
                      [Plane(np.array([.0, 1.0, 0.0]))]]

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if render:
            start_counter = perf_counter()
            
            # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
            for y_index, y in enumerate(np.linspace(viewport[1], viewport[3], HEIGHT)):
                if (y_index+1) % 10 == 0:
                    text, textpos = progress_text(y_index, font)
                    framebuffer.blit(text, textpos)
                    pygame.display.update()
                    
                for x_index, x in enumerate(np.linspace(viewport[0], viewport[2], WIDTH)):
                    
                    # Pygame seems to be using the origin at the upper left corner,
                    # so we have to make y negative in order to respect a right-handed coordinate system (3D)
                    pixel = np.array([x,-y,0]) 
                    direction = normalize(pixel - origin) # figure out the direction of the ray

                    primary_ray = Ray(origin, direction)

                    color = intersect_objects(primary_ray, scene_objects)
                    
                    backbuffer[x_index, y_index] = color

            
            temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
            framebuffer.blit(temp_framebuffer, ( (MARGIN/2, MARGIN/2) )) # second parameter centers our viewport
            pygame.display.update()
            
            end_counter = perf_counter()
            elapsed_seconds = (end_counter - start_counter)
            print("It took", elapsed_seconds, "seconds to render") 
            
        render = False

    
if __name__ == '__main__':
    main()
