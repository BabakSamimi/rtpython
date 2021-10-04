import App
from Intersectable import *
from utility import clamp
import re

def load_scene_file(path):
    scene = App.Scene(False)
    data = []
    try:
        with open(path) as f:
            data = f.readlines()
            f.seek(0)
            
        for line in data:
            m = re.findall(r'(-?\d+\.\d|\d+)', line)
            if m:
                if "Sphere:" in line:
                    print("Sphere:", m)
                    if expected_match_size(m, 8):
                        scene.add_object(Sphere(
                            center=(float(m[0]), float(m[1]), float(m[2])),
                            radius=float(m[3]),
                            material=Material(
                                float(m[4]),
                                (clamp(int(m[5]), 0, 255), clamp(int(m[6]), 0, 255), clamp(int(m[7]), 0, 255)))))

                elif "Plane:" in line:
                    print("Plane:", m)
                    if expected_match_size(m, 8):                                             
                        scene.add_object(Plane(
                            origin=(float(m[0]), float(m[1]), float(m[2])),
                            normal=(float(m[3]), float(m[4]), float(m[5])),
                            material=Material(
                            float(m[6]), None)))

                elif "Light:" in line:
                    print("Light:", m)
                    if expected_match_size(m, 8):                                         
                        scene.add_light(Light(
                            position=(float(m[0]), float(m[1]), float(m[2])),
                            intensity=float(m[3]),
                            material=Material(
                            float(m[4]), (clamp(int(m[5]), 0, 255), clamp(int(m[6]), 0, 255), clamp(int(m[7]), 0, 255)))))
        
    except Error:
        print("Error loading scene file!")
        return App.Scene() # default init
    

    print("Loaded scene file!")
    return scene


def expected_match_size(m, expected_size):
    if len(m) == expected_size:
        return True

    print("Size of search result was not as expected!")
    return False

