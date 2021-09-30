import numpy as np
import pygame
from pygame.locals import *

# https://en.wikipedia.org/wiki/Gamma_correction
def gamma_correction(color):
  gamma = 2.0 # average gamma for most displays, mac uses 1.8 and some uses 2.2
  return np.array([color[0]**(1/gamma), color[1]**(1/gamma), color[2]**(1/gamma)])

def normalize(vec):
  # divides each component of vec with its length, normalizing it
  return vec / np.linalg.norm(vec)

def length(vec):
  return np.linalg.norm(vec)

def process_input(keys, camera):

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


def process_mouse_input(rel_pos, camera):
  
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


def clamp(a, min_val, max_val):
  if (a < min_val): return min_val
  if (a > max_val): return max_val
  return a

# get a value between a and b depending on t (or just get a or b)
def lerp(a, b, t):
  return (1-t) * a + t * b

def progress_text(y_index, font, width, height):
  percentage = ((y_index+1) / (height)) * 100
  progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
  
  color = (lerp(0, 255, y_index/(width-1)), 0, 255)
  
  text = font.render(progress, False, color, (0,0,0))
  textrect = text.get_rect(left=0, top=50)
  return (text, textrect)

def print_camera_info(camera, font):
  color = (255, 255, 255)
  formatter = {'float_kind': lambda x: "%.2f" % x}
  position = np.array2string(camera.position, precision=4, separator=',', formatter=formatter)
  look_to = np.array2string(camera.look_to, precision=4, separator=',', formatter=formatter)

  info = "Position: " + position + ", Looking at: " + look_to
  
  text = font.render(info, False, color, (0,0,0))
  textpos = text.get_rect(left=0, top=0)
  return (text, textpos)

def process_events(camera):

  running = True
  render = False
  camera = camera
  
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
      render = False
       
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        running = False
        render = False
        break
              
      render, camera = process_input(pygame.key.get_pressed(), camera)
              
    if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_focused() and pygame.mouse.get_pressed()[0]:              
      render, camera = process_mouse_input(pygame.mouse.get_rel(), camera)
    
  return (running, render, camera)

# checkerboard pattern logic borrowed from here:
# https://github.com/carl-vbn/pure-java-raytracer/blob/23300fca6e9cb6eb0a830c0cd875bdae56734eb7/src/carlvbn/raytracing/solids/Plane.java#L32
def checker_color(intersection, origin):
    point = intersection - origin # get the point sitting on the plane by taking the scaled ray  minus plane origin
    pX = int(point[0])
    pZ = int(point[2])

    # for every other x and z position that is even, color the pixel white, otherwise beige
    # might not work behind the camera
    if ((pX % 2 == 0) == (pZ % 2 == 0)):
        return np.array([252, 204, 116])
    else:
        return np.array([30,30,30])
