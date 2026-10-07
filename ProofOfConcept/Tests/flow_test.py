import world

state = world.create_world(rows=1, columns=2)
state[1, 0, 0] = 10           # 10 units of type 1 (e) in the left cell

state = world.flow(state)
print(state[1])               # expect [[7.5 2.5]]

state = world.flow(state)
print(state[1])               # expect [[6.25 3.75]]

print(state[1].sum())         # expect 10.0
print(state[0])               # ambient: expect [[1. 1.]]