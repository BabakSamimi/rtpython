import numpy as np
import pygame
from pygame.locals import *

# treat sphere intersection as a quadratic function to solve, f = ax^2 + bx + c
# https://en.wikipedia.org/wiki/Quadratic_equation#Quadratic_formula_and_its_derivation
def solve_quadratic_equation(ray, sphere):
   rD = ray.direction
   rO = ray.origin
   sC = sphere.origin
   sR = sphere.radius
   rOsC = rO - sC # origin - sphere center

   #a = length(rD)
   b = 2 * np.dot(rD, rOsC) # b = 2 * rD*rOsC
   c = length(rOsC) ** 2 - (sR ** 2)  # (rO - sC)^2 - sR^2,
   discriminant = (b**2) - (4*c)

   if discriminant > 0:
       # solutions found
       sqrt = np.sqrt(discriminant)
       d1 = (-b + sqrt) / (2)
       d2 = (-b - sqrt) / (2)
       if d1 > 0.001 and d2 > 0.001: # prevent shadow acne by checking above 0.001
           return min(d1, d2)

   return None

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
  progress = "Progress: " +  "%.2f" % percentage + "%"
  
  color = (lerp(0, 255, y_index/(width-1)), 0, 255)
  
  text = font.render(progress, False, color, (0,0,0))
  textrect = text.get_rect(left=10, top=50)
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



