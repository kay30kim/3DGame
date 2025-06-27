from ursina import *

app = Ursina()

cube = Entity(model='cube', color=color.azure, scale=(1,1,1))
ground = Entity(model='plane', scale=(10,1,10), color=color.green, y=-1)

camera.position = (0, 3, -15)
camera.rotation_x = 10
DirectionalLight().look_at(Vec3(1,-1,1))
def update():
    if held_keys['a']:
        cube.x -= 2 * time.dt
    if held_keys['d']:
        cube.x += 2 * time.dt
    if held_keys['w']:
        cube.z += 2 * time.dt
    if held_keys['s']:
        cube.z -= 2 * time.dt
    if held_keys['q']:
        sys.exit()

app.run()