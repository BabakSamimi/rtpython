# Flags
Run with: `python main.py`

`-s` saves a screenshot when done with render (Beware that if you're moving around in the scene this will yield a lot of screenshots)

`-f` opens the program in fullscreen

`-width` width for viewport

`-height` height for viewport

`-scene` loads a scene-file to render

`-max` specify max depth for reflections

Examples:

`python main.py -f -s -scene "scenes/scene01.scene"`

`python main.py -scene "scenes/scene01.scene" -width 100 -height 100`

# Result (1200x800) (takes 2.8 minutes to render)
![1920x1080](2021-10-03-12-42-57.png)