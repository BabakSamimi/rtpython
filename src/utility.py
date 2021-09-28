import numpy as np
from pygame.locals import *

def process_input(keys, origin):

   if keys[K_w]:
       origin[2] -= 0.1
   elif keys[K_a]:
       origin[0] -= 0.1
   elif keys[K_s]:
       origin[2] += 0.1
   elif keys[K_d]:
      origin[0] += 0.1
   else:
      return (False, origin)

   return (True, origin)

def clamp(a, min_val, max_val):
    if (a < min_val): return min_val
    if (a > max_val): return max_val
    return a

# normal = normal of the surface the ray hit
def reflect(ray, normal):
    # calculate how a ray gets reflected
    # if the ray were to have the same "outgoing" angle
    # as the "ingoing" angle.
    # the result will be a reflected ray
    return ray - 2*np.dot(ray, normal)*normal

def xor(a, b):
    return bool(a) ^ bool(b)

# get a value between a and b depending on t (or just get a or b)
def lerp(a, b, t):
    return (1-t) * a + t * b

def normalize(vec):
    # divides each component of vec with its length, normalizing it
    return vec / np.linalg.norm(vec)
    
def progress_text(y_index, font, width, height, inset):
    percentage = ((y_index+1) / (height)) * 100
    progress = "Progress: " + '{:.2f}'.format(percentage) + "%"
    color = (lerp(0, 255, y_index/(width-1)), 0, 255)
    text = font.render(progress, False, color, (0,0,0))
    textpos = text.get_rect(centerx=inset/2 + 60, centery=inset/2 - 15)
    return (text, textpos)

    
