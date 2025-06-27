from ursina import *

app = Ursina()

# 큐브 하나 만들기
cube = Entity(model='cube', color=color.azure, scale=(5,5,5))

# 키 입력 처리 함수
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