import pygame
import numpy as np

WIDTH = 300
HEIGHT = 200
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

def ray_color(ray):
    pass

class Sphere:
    def __init__(self, center, radius):
        self.center = center # determines where in the 3D world the center of the sphere exists
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

    scene_objects = [ Sphere(np.array([-0.2, 0., -1]), 0.5), Sphere(np.array([0.1, -0.3, 0.]), 0.2)]

    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((WIDTH, HEIGHT, 3))
               
    framebuffer = pygame.display.set_mode((WIDTH + MARGIN, HEIGHT + MARGIN))
    pygame.display.set_caption("Backwards ray-tracing")
        
    running = True

    # Init progress text
    font = pygame.font.Font(None, 21)

    render = True

    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if render:
            # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
            for y_index, y in enumerate(np.linspace(viewport[1], viewport[3], HEIGHT)):
                for x_index, x in enumerate(np.linspace(viewport[0], viewport[2], WIDTH)):
                    if y_index % 10 == 0:
                        percentage = (y_index / WIDTH) * 100
                        progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
                        text = font.render(progress, False, (255, 255, 255), (0,0,0))
                        textpos = text.get_rect(centerx=MARGIN/2 + 60, centery=MARGIN/2 - 15)
                        framebuffer.blit(text, textpos)
                        pygame.display.update()


                    pixel = np.array([x,y,0])
                    direction = normalize(pixel - origin) # figure out where the ray is be going                 
                    ray = Ray(origin, direction)
                    
                    y_dir = ray.direction[1]
                    backbuffer[x_index, y_index] = np.array([np.abs(y_dir)*255, 30, 255])

            temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
            framebuffer.blit(temp_framebuffer, ( (MARGIN/2, MARGIN/2) )) # second parameter centers our viewport

            # render update
            pygame.display.update()
        render = False

    
if __name__ == '__main__':
    main()
