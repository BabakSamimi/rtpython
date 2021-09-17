from time import perf_counter
import pygame
import numpy as np

WIDTH = 600
HEIGHT = 400
MARGIN = 200
MAX_DEPTH = 2

def normalize(vec):
    # divides each component of vec with its length, normalizing it
    return vec / np.linalg.norm(vec)

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def at(coefficient):
        # Coefficient is used to move the ray along a line in 3D space
        return origin + (coefficient*direction)

# treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
# returns true if we have at least one intersection
def sphere_intersection(ray, sphere):
    rD = ray.direction
    rO = ray.origin
    sC = sphere.center
    sR = sphere.radius

    a = 1 # a = ||rD|| = 1 
    b = 2 * np.dot(rD, rO-sC) # b = 2 * rD (rO - sC)
    c = np.linalg.norm(rO - sC) ** 2 - sR ** 2 # (rO - sC)^2 - sR^2
    discriminant = (b**2) - (4*a*c)
    
    return (discriminant > 0)
    #if (discriminant > 0):
        
        
class Sphere:
    def __init__(self, center, radius):
        self.center = center # 3D coordinates of sphere center
        self.radius = radius
        #self.color = color
        
class Camera:
    def __init__(self, origin, viewport_width, viewport_height, focal_length):
        self.origin = origin
        self.horizontal = np.array([viewport_width, 0, 0])
        self.vertical = np.array([0, viewport_height, 0])
        self.focal_length = focal_length # distance between camera and viewport

        self.lower_left_corner = self.origin - self.horizontal/2 - self.vertical/2 - np.array([0, 0, focal_length])
    
def main():
    pygame.init()

    aspect_ratio = float(WIDTH/HEIGHT) # 3:2 aspect ratio for now
    print("Aspect ratio:", aspect_ratio)

    # we want the viewport to have the same aspect ratio as the image itself
    # the viewport ranges from -1 to 1 in the x-axis
    # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
    # these numbers are really arbitrary, but as long as they have the same ratio as the image itself it's fine
    
    viewport_width = 1.0
    viewport_height = (1.0 / aspect_ratio)
    viewport = (-viewport_width, -viewport_height, viewport_width, viewport_height) # LEFT, BOTTOM, RIGHT, TOP

    origin = np.array([0,0,1])
    camera = Camera(origin, viewport_width, viewport_height, 1.0)

    scene_objects = [ Sphere(np.array([-0.5, -0.2, -1]), 0.5),
                      Sphere(np.array([0.8, -0.3, -1]), 0.2)]

    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((WIDTH, HEIGHT, 3))
               
    framebuffer = pygame.display.set_mode((WIDTH + MARGIN, HEIGHT + MARGIN))
    pygame.display.set_caption("Backwards ray-tracing")
        
    running = True

    # Init font for progress text
    font = pygame.font.Font(None, 21)

    render = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if render:
            start_counter = perf_counter()
            
            # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
            for y_index, y in enumerate(np.linspace(viewport[1], viewport[3], HEIGHT)):
                if (y_index+1) % 10 == 0:
                    percentage = ((y_index+1) / (HEIGHT)) * 100
                    progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
                    text = font.render(progress, False, (y_index/(WIDTH-1)*255, 30, 255), (0,0,0))
                    textpos = text.get_rect(centerx=MARGIN/2 + 60, centery=MARGIN/2 - 15)
                    framebuffer.blit(text, textpos)
                    pygame.display.update()
                    
                for x_index, x in enumerate(np.linspace(viewport[0], viewport[2], WIDTH)):
                    # Pygame seems to be using the origin at the upper left corner,
                    # so we have to make y negative in order to respect a right-handed coordinate system (3D)
                    pixel = np.array([x,-y,0]) 
                    direction = normalize(pixel - origin) # figure out the direction of the ray
                    ray = Ray(origin, direction)

                    sphere_hit = False
                    for i in range(0, 2):
                        sphere_hit = sphere_intersection(ray, scene_objects[i])
                        if sphere_hit:
                            break
                    
                    y_dir = ray.direction[1]

                    color = np.array([0.5*(y_dir+1)*255, 30, 255])

                    if (sphere_hit):
                        color = np.array([0.5*(y_dir+1)*255, 0, 0.5*(y_dir+1)*108])
                    
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
