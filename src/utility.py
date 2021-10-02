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

def clamp(a, min_val, max_val):
  if (a < min_val): return min_val
  if (a > max_val): return max_val
  return a

# get a value between a and b depending on t (or just get a or b)
def lerp(a, b, t):
  return (1-t) * a + t * b

# Returns a normalized reflected ray
def reflect(vector, normal):
  return vector - 2*np.dot(vector,normal) * normal

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



