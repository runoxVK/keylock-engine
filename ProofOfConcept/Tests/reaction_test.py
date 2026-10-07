import numpy as np
import config
import world

def one_cell():
    return world.create_world(rows=1, columns=1)

#Test 1: Decay (drain)
# s's key fits the ambient's lock with fit 0.2, so each tick the ambient absorbs
# 0.1 x 0.2 = 2% of s, and s has no product to replace it.
state = one_cell()
state[2] = 4 # 4 units of s
state = world.reactions(state)
print("decay, 1 tick:", state[2, 0, 0]) # expect 3.92  (4 x 0.98)
for _ in range(33):
    state = world.reactions(state)
print("decay, 34 ticks:", state[2, 0, 0]) # expect about 2.0, i.e. roughly halved
print("ambient:", state[0, 0, 0]) # expect 1.0, never used up

#Test 2: Source (tap)
# The ambient's key fits e's lock with fit 0.5, and e's product is s.
# With 2 units of e: 0.1 x 1 x 2 x 0.5 = 0.1 of s produced per tick, e unchanged.
state = one_cell()
state[1] = 2  # 2 units of e
state = world.reactions(state)
print("source, 1 tick: e =", state[1, 0, 0], " s =", state[2, 0, 0]) # expect e = 2.0, s = 0.1
state = world.reactions(state)
print("source, 2 ticks: s =", state[2, 0, 0]) # expect 0.198 (0.1 kept 98%, plus 0.1 new)

# Test 3: Clamping
# Make reactions very fast, so decay wants more s than exists: 10 x 4 x 1 x 0.2 = 8 > 4.
# Clamping should use up s exactly, never go negative.
config.REACTION_RATE = 10
state = one_cell()
state[2] = 4
state = world.reactions(state)
print("clamped:", state[2, 0, 0]) # expect 0.0, not -4.0
config.REACTION_RATE = 0.1