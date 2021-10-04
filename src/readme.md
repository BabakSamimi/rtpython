# Flags
Run with: `python main.py`

`-s` saves a screenshot when done with render (Beware that if you're moving around in the scene this will yield a lot of screenshots)

`-f` opens the program in fullscreen

`-width` width for viewport

`-height` height for viewport

`-scene` loads a scene-file to render

`-max` specify max depth for reflections

## Primitive camera movement:
**Camera was not done properly this time around.**

`WASD` to move the camera around

`Arrow keys` to look up and down (left and right is not working properly)

Examples:

`python main.py -f -s -scene "scenes/scene01.scene"`

`python main.py -scene "scenes/scene01.scene" -width 100 -height 100`

# Result (1920x1080, 9.8 minutes with 8 reflection rays as max depth)
![1920x1080](screenshots/finale.png)