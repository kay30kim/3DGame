from ursina import *

app = Ursina()

player = Entity(model='cube', color=color.orange, scale=(1,1,1), position=(0,0,0))
# ground = Entity(model='plane', scale=(10,1,10), color=color.green, y=-1)

# camera.position = (0, 5, -15)
# camera.rotation_x = 30
# DirectionalLight().look_at(Vec3(1,-1,-1))

def update():
    speed = 5 * time.dt
    if held_keys['w']:
        player.z -= speed
    if held_keys['s']:
        player.z += speed
    if held_keys['a']:
        player.x -= speed
    if held_keys['d']:
        player.x += speed
    if held_keys['q']:
        sys.exit()

app.run()
