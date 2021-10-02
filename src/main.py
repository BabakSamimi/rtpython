# TODO:
# Create camera class, seperate the distinction between
# camera position and origin of world
# movement doesn't work properly because of this

from time import perf_counter
import pygame
import numpy as np

from utility import *
from Ray import *
from Intersectable import *
from App import *

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

app = App(WINDOW_WIDTH, WINDOW_HEIGHT, "Ray tracing")
       
def main():
    pygame.init()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    font = pygame.font.Font(None, int(30))
    
    print("Smooth scale backend:", pygame.transform.get_smoothscale_backend())

    aspect_ratio = float(app.viewport_width/app.viewport_height)
    print(app)

    camera = Camera((0.0, 2.0, 12.0), (0.0, 0.0, 0.0), 90, aspect_ratio, app.viewport_width, app.viewport_height)
    
    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((app.viewport_width, app.viewport_height, 3))
               
    framebuffer = pygame.display.set_mode((app.window_width, app.window_height)) #flags=pygame.FULLSCREEN)
    pygame.display.set_caption(app.title)

    render = True

    scene = Scene()
    scene.add_object(Sphere(center=(4.2, 0.5, -0.5), radius=2.0, material=Material(1.0, (255, 25, 50))))
    scene.add_object(Sphere(center=(-2.2, 0.0, 0.0), radius=2.0, material=Material(0.0, (30, 255, 100))))
    scene.add_object(Sphere(center=(0.0, -1.0, 0.5), radius=0.5, material=Material(0.0, (60, 25, 255))))
    scene.add_object(Plane(origin=(1.2, -1.0 , 0.0), normal=(0, 1, 0), material=Material(0.0, None)))
    
    scene.add_light(Light(position=(6.0, 3.0, -5.0), intensity=1.0, material=Material(0.0, (255,255,255))))
    scene.add_light(Light(position=(0.0, 8.0, 2.0), intensity=4.0, material=Material(0.0, (255,255,255))))

    scene = app.scene

    while app.running:
      
      if render:
        start_counter = perf_counter()
        # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
        for y_index, y in enumerate(camera.viewport.coordinates[0]):
          if (y_index+1) % 10 == 0:
            text, textrect = progress_text(y_index, font, app.viewport_width, app.viewport_height)
            framebuffer.blit(text, textrect)
            pygame.display.update()

          for x_index, x in enumerate(camera.viewport.coordinates[1]):

            # Pygame seems to be using the origin at the upper left corner,
            # so we have to make y negative in order to respect a right-handed coordinate system (3D)
            pixel = np.array([x,-y,0]) 
            direction = normalize(pixel - camera.z) # figure out the direction of the ray

            color = np.zeros((3))
            
            primary_ray = Ray(camera.position, direction)
            hit_data = trace_ray(primary_ray, scene.get_all_scene_objects())
            
            if hit_data:
              
              color = compute_color(primary_ray, hit_data, scene)
              
              color[0] = clamp(color[0], 0, 255)
              color[1] = clamp(color[1], 0, 255)
              color[2] = clamp(color[2], 0, 255)            

            backbuffer[x_index, y_index] = color


        temp_framebuffer = pygame.surfarray.make_surface(backbuffer)
        #temp_framebuffer_upscaled = pygame.transform.scale(temp_framebuffer, (int(WINDOW_WIDTH/2),int(WINDOW_HEIGHT/2)))

        # create an upscaled version of our frame that is half the size of the window dimensions
        temp_framebuffer_smooth_upscaled = pygame.transform.smoothscale(temp_framebuffer, (int(app.window_width),int(app.window_height)) )
        #temp_framebuffer_upscaled = pygame.transform.scale(temp_framebuffer, (int(WINDOW_WIDTH),int(WINDOW_HEIGHT)) )
        center_x, center_y = (int(app.window_width/4), int((app.window_height/4)))

        text, textrect = print_camera_info(camera, font)
        
        framebuffer.blit(temp_framebuffer_smooth_upscaled, ( (0, 0)))        
        framebuffer.blit(text, textrect)
        pygame.display.update()

        end_counter = perf_counter()
        elapsed_seconds = (end_counter - start_counter)
        print("It took", elapsed_seconds, "seconds to render")
        render = False
        
      render, camera = app.process_events(camera)
    

    
if __name__ == '__main__':
    main()
