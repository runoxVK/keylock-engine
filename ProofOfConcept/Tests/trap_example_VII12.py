import numpy as np
import config
import world

# Settings used by the example
config.HOP_RATE = 1
config.BINDING_SENSITIVITY = 1


# Stand-in for this test only: binding fixed at 0, 2, 0 for every type
def fake_binding(free, q):
    return np.array([[0.0, 2.0, 0.0]])

world.binding = fake_binding # flow will now use the fake


state = world.create_world(rows=1, columns=3)
state[1, 0, 0] = 8 # 8 units of type 1 in the left cell

state = world.flow(state)
print(state[1]) # expect [[6. 2. 0.]]

state = world.flow(state)
print(state[1]) # expect about [[4.568 3.364 0.068]]

for _ in range(1000):
    state = world.flow(state)
print(state[1]) # expect about [[0.852 6.296 0.852]]
print(state[1].sum()) # expect 8.0