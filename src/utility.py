import numpy as np

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
