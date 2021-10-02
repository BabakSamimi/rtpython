import numpy as np
import argparse
import os
from utility import *
from fractions import Fraction
from pygame import display
from pygame.locals import *
from SceneParser import *
import pygame

class App:
    def __init__(self, window_width, window_height, title):

        self.window_width = window_width
        self.window_height = window_height
        self.window_aspect_ratio = float(self.window_width/self.window_height)
        self.title = title
        self.running = True
        
        parser = argparse.ArgumentParser(description="A ray tracing program")
        parser.add_argument('-width', metavar='w', type=int, help="Width", default=300)
        parser.add_argument('-height', metavar='h', type=int, help="Height", default=200)
        parser.add_argument('-max', metavar='m', type=int, help="Max recursive depth for reflections", default=3)
        parser.add_argument('-scene', metavar='s', type=str, help="load a scene file")
        parser.add_argument('-f', help="Fullscreen mode", action='store_true')
        parser.add_argument('-s', help="Save as a screenshot after completion", action='store_true')                
        args = parser.parse_args()
        
        self.viewport_width = args.width 
        self.viewport_height = args.height
        self.viewport_aspect_ratio = float(self.viewport_width/self.viewport_height)
        
        self.max_depth = args.max
        
        self.scene_path = args.scene if args.scene else None
        self.scene = load_scene_file(self.scene_path) if self.scene_path else Scene() # Scene
        self.last_stamp = os.stat(self.scene_path).st_mtime

        self.fullscreen = args.f
        self.screenshot = args.s

    def __str__(self):
        s = """ Application runtime:
        Window dimensions: {0}x{1}, aspect ratio: {2}/{3}
        Viewport dimensions: {4}x{5}, aspect ratio: {6}/{7}
        Window title: {8}
        """.format(self.window_width, self.window_height, *Fraction(self.window_aspect_ratio).as_integer_ratio(),
                   self.viewport_width, self.viewport_height, *Fraction(self.viewport_aspect_ratio).as_integer_ratio(),
                   self.title)
        return s

    def create_framebuffer(self):
        if self.fullscreen:
            return pygame.display.set_mode((self.window_width, self.window_height), flags=pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

        return pygame.display.set_mode((self.window_width, self.window_height))

    def process_events(self, camera):

        render = False
        camera = camera

        for event in pygame.event.get():
          if event.type == pygame.QUIT:
            self.running = False
            render = False

          if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
              self.running = False
              render = False
              break

            render, camera = self.process_input(pygame.key.get_pressed(), camera)

          if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_focused() and pygame.mouse.get_pressed()[0]:              
            render, camera = self.process_mouse_input(pygame.mouse.get_rel(), camera)

        return render, camera

    def process_input(self, keys, camera):

        if keys[K_w]:
          camera.position += np.array([0.0, 0.0, -0.4])
        elif keys[K_s]:
          camera.position -= np.array([0.0, 0.0, -0.4])
        elif keys[K_a]:
          camera.position += normalize(np.cross(camera.z, camera.up))
        elif keys[K_d]:
          camera.position -= normalize(np.cross(camera.z, camera.up))
        elif keys[K_UP]:
          camera.look_to[1] += 0.5
        elif keys[K_DOWN]:
          camera.look_to[1] -= 0.5    
        elif keys[K_LEFT]:
          camera.look_to[0] -= 0.5
        elif keys[K_RIGHT]:
          camera.look_to[0] += 0.5        
        else:
          return (False, camera)

        camera.z = normalize(camera.position - camera.look_to)
        return (True, camera)

    
    def process_mouse_input(self, rel_pos, camera):

        x_offset = rel_pos[0]
        y_offset = rel_pos[1]

        sensitivity = 0.1
        camera.yaw += x_offset * sensitivity
        camera.pitch += y_offset * sensitivity

        if camera.pitch > 89.0:
          camera.pitch = 89.9

        if camera.pitch < -89.0:
          camera.pitch -89.0

        yaw_rad = np.deg2rad(camera.yaw)
        pitch_rad = np.deg2rad(camera.pitch)

        z = np.array([np.cos(yaw_rad) * np.cos(pitch_rad),
                              np.sin(pitch_rad),
                              np.sin(yaw_rad) * np.cos(pitch_rad)])

        camera.z = normalize(z)
        return (True, camera)

    def check_for_scene_update(self):
        if self.scene_path:
            new_stamp = os.stat(self.scene_path).st_mtime
            if new_stamp != self.last_stamp:
                self.last_stamp = new_stamp
                self.scene = load_scene_file(self.scene_path)
                return True
            else:
                return False
        else:
            return False


class Scene:
    def __init__(self, default=True):
        self.objects = []
        self.lights = []
        
        # default init
        if default:
            print("Loading default scene")
            self.add_object(Sphere(center=(4.2, 0.5, -0.5), radius=2.0, material=Material(1.0, (255, 25, 50))))
            self.add_object(Sphere(center=(-2.2, 0.0, 0.0), radius=2.0, material=Material(0.0, (30, 255, 100))))
            self.add_object(Sphere(center=(0.0, -1.0, 0.5), radius=0.5, material=Material(0.0, (60, 25, 255))))
            self.add_object(Plane(origin=(1.2, -1.0 , 0.0), normal=(0, 1, 0), material=Material(0.0, None)))
    
            self.add_light(Light(position=(6.0, 3.0, -5.0), intensity=1.0, material=Material(0.0, (255,255,255))))
            self.add_light(Light(position=(0.0, 8.0, 2.0), intensity=4.0, material=Material(0.0, (255,255,255))))
        

    def add_object(self, obj):
        self.objects.append(obj)

    def add_light(self, light):
        self.lights.append(light)

    def get_all_scene_objects(self):
        return self.lights + self.objects

class Viewport:
    def __init__(self, height_ratio, aspect_ratio, image_width, image_height):
        # we want the viewport to have the same aspect ratio as the image itself
        # the viewport ranges from -1 to 1 in the x-axis
        # and -1/aspect_ratio to 1/aspect_ratio in the y-axis
        # these numbers are arbitrary, but it's a common thing to do
        self.width = 1
        self.height = (1.0 / aspect_ratio)

        viewport = (-self.width, -self.height, self.width, self.height) # LEFT, BOTTOM, RIGHT, TOP
        
        self.coordinates = [np.linspace(viewport[1], viewport[3], image_height), np.linspace(viewport[0], viewport[2], image_width)]
        
class Camera:
    def __init__(self, position, look_to, vertical_fov, aspect_ratio, image_width, image_height):

        # this FOV code might not work properly at the moment
        angle = np.deg2rad(vertical_fov)
        h = np.tan(angle/2)       
        
        self.position = np.array(position)
        self.look_to = np.array(look_to)
        self.up = np.array([0.0, 1.0, 0.0])        
        
        self.z = normalize(self.position - self.look_to) # unit vector at where we are looking
        self.x = normalize(np.cross(self.up, self.z))
        self.y = np.cross(self.z, self.x)

        self.yaw = 0.0
        self.pitch = 0.0
        
        self.viewport = Viewport(h, aspect_ratio, image_width, image_height)
