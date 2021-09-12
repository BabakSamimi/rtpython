import pygame
import numpy as np

WIDTH = 300
HEIGHT = 200
MAX_DEPTH = 2


def fill_screen(screen_buffer):
    for y in range(0, WIDTH):
        for x in range(0, HEIGHT):
            screen_buffer.set_at((x,y), pygame.Color(0,0,0))

class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    def at(coefficient):
        # Coefficient is used to move the ray along a line in 3D space
        return origin + (coefficient*direction)

# 3D object class
class Mesh:
    def __init__(self):
        pass

class Camera:
    def __init__(self, origin, viewport_width, viewport_height):
        self.origin = origin
        self.horizontal = np.array([viewport_width, 0, 0])
        self.vertical = np.array([0, viewport_height, 0])
        
        self.coordinate_origin = origin - horizontal/2 - vertical/2 - np.array([0, 0, 1])
    
def main():
    pygame.init()

    
    camera = np.array([0, 0, 1]) # camera starts at (0,0,1) in 3D-space
    aspect_ratio = float(WIDTH/HEIGHT) # 3:2 aspect ratio
    print("Aspect ratio:")
    
    # we want the viewport to have the same aspect ratio as the image itself
    # the viewport ranges from -1 to 1 in the x-axis
    # and -1/ratio to 1/ratio in the y-axis
    viewport = (-1, 1 / aspect_ratio, 1, -1 / aspect_ratio) # LEFT, TOP, RIGHT, BOTTOM

    # A pixel-array with 3 values for each pixel (RGB)
    backbuffer = np.zeros((HEIGHT, WIDTH, 3))
           
    framebuffer = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Backwards ray-tracing")
    
    running = True
    
    while running:
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # enumerating through linspace will give us indices for the image itself
        # and the y and x values will correspond to the viewport (screen-coordinate space)
        for height_index, y in enumerate(np.linspace(viewport[1], viewport[3], HEIGHT)):
            for width_index, x in enumerate(np.linspace(viewport[0], viewport[2], WIDTH)): 
                backbuffer[height_index, width_index] = np.array([255, 30, 30])

        temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
        framebuffer.blit(temp_framebuffer, (0,0))
        
        # render update
        pygame.display.update()

    
        
if __name__ == '__main__':
    main()
