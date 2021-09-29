import numpy as np
import pygame
from pygame.locals import *

def normalize(vec):
  # divides each component of vec with its length, normalizing it
  return vec / np.linalg.norm(vec)

def process_input(keys, camera):

  if keys[K_w]:
    camera.position += np.array([0.0, 0.0, -0.4])
  elif keys[K_s]:
    camera.position -= np.array([0.0, 0.0, -0.4])
  elif keys[K_a]:
    camera.position += normalize(np.cross(camera.z, camera.up))
  elif keys[K_d]:
    camera.position -= normalize(np.cross(camera.z, camera.up))    
  else:
    return (False, camera)

  camera.z = normalize(camera.position - camera.look_to)
  return (True, camera)

FIRST_MOUSE_INPUT = True

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

def progress_text(y_index, font, width, height, inset):
  percentage = ((y_index+1) / (height)) * 100
  progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
  color = (lerp(0, 255, y_index/(width-1)), 0, 255)
  text = font.render(progress, False, color, (0,0,0))
  textpos = text.get_rect(centerx=inset/2 + 60, centery=inset/2 - 15)
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
