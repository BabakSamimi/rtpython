import App
from Intersectable import *
from utility import clamp
import re



def load_scene_file(path):
    scene = App.Scene()
    data = None
    #sphere_attributes = re.compile(r'((\d+\.\d)|(\d+))')    
    with open(path) as f:
        for line in f:
            print(line)
            if "Sphere:" in line:
                m = re.findall(r'(\d+\.\d|\d+)', line)
                if m:
                    print(m)
                    scene.add_object(Sphere(
                        center=(float(m[0]), float(m[1]), float(m[2])),
                        radius=float(m[3]),
                        material=Material(
                            float(m[4]),
                                  (clamp(int(m[5]), 0, 255), clamp(int(m[6]), 0, 255), clamp(int(m[7]), 0, 255)))))
            elif "Plane:" in line:
                m = re.findall(r'(\d+\.\d|\d+)', line)
                if m:
                    print(m)
                    scene.add_object(Plane(
                        origin=(float(m[0]), float(m[1]), float(m[2])),
                        normal=(float(m[3]), float(m[4]), float(m[5])),
                        material=Material(
                            float(m[6]), None)))

            elif "Light:" in line:
                m = re.findall(r'(\d+\.\d|\d+)', line)
                if m:
                    print(m)
                    scene.add_light(Light(
                        position=(float(m[0]), float(m[1]), float(m[2])),
                        intensity=float(m[3]),
                        material=Material(
                            float(m[4]), (clamp(int(m[5]), 0, 255), clamp(int(m[6]), 0, 255), clamp(int(m[7]), 0, 255)))))

    print("Loaded scene file!")
    return scene




