from time import perf_counter
from datetime import datetime
import pygame
import numpy as np

from utility import *
from Ray import *
from Intersectable import *
from App import *

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800

def main():
    app = App(WINDOW_WIDTH, WINDOW_HEIGHT, "Ray tracing")
    pygame.init()
    pygame.event.set_grab(True)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(app.title)
    font = pygame.font.Font(None, int(38))
    
    print("Smooth scale backend:", pygame.transform.get_smoothscale_backend())

    camera = Camera((0.0, 0.0, 1.0), (0.0, 0.5, -1.0), app.viewport_width, app.viewport_height)
    
    # A pixel-array with 3 values for each pixel (RGB)
    # Essential this is a Width x Height with a depth of 3
    # PyGame will read the backbuffer as [X, Y], hence why WIDTH is being used to determine the rows of the matrix
    backbuffer = np.zeros((app.viewport_width, app.viewport_height, 3))
    framebuffer = app.create_framebuffer()
    
    render = True

    scene = app.scene
    depth = app.max_depth
    
    print(app)
    
    while app.running:
        app.running ^= app.headless # run game loop only once if headless mode is turned on
      
        if render:
            start_counter = perf_counter()
            # y_index and x_index are indices used for the pixel array and y and x are the viewport coordinates 
            for y_index, y in enumerate(camera.viewport.coordinates[0]):
                for x_index, x in enumerate(camera.viewport.coordinates[1]):
                    backbuffer[x_index, y_index] = calculate_pixel(x, y, camera, scene, depth)

                if not app.headless:
                    # create an upscaled version of our frame
                    surface_backbuffer = pygame.surfarray.make_surface(backbuffer)
                    backbuffer_smooth_upscaled = pygame.transform.smoothscale(surface_backbuffer, (app.window_width, app.window_height))
                    #center_x, center_y = (int(app.window_width/4), int((app.window_height/4)))
                    
                    framebuffer.blit(backbuffer_smooth_upscaled, ((0, 0)))
                    
                    text, textrect = print_camera_info(camera, font)
                    framebuffer.blit(text, textrect)

                    text, textrect = progress_text(y_index, font, app.window_width, app.window_height)
                    framebuffer.blit(text, textrect)

                    pygame.display.update()
                else:
                    percentage = ((y_index+1) / (app.viewport_height)) * 100
                    if percentage % 10 == 0:
                        print("\rProgress:", "%.2f" % percentage, "%", end='')
    
            end_counter = perf_counter()
            elapsed_seconds = (end_counter - start_counter)
            print("\nIt took", elapsed_seconds, "seconds to render")
            render = False

            # end of render
            
        if app.screenshot:
            print("Saving final image")
            screenshotbuffer =  pygame.surfarray.make_surface(backbuffer) # save raw data of the scene (no upscaling)
            pygame.image.save(screenshotbuffer, "screenshots/" + datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".png")        

        render, camera = app.process_events(camera)
            
        if app.check_for_scene_update():
            scene = app.scene
            render = True

        # end of game loop
        
# end of main    
if __name__ == '__main__':
    main()
