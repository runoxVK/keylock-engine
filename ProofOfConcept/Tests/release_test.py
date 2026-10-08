import world
state = world.create_world(rows=1, columns=1)
world.add_bundle(state, 0, [(0, 0)], 1, 1.0)
state = world.tick(state)
print("bundled s:", state["bundled"][2, 0, 0])   # expect 0.0  (released)
print("free s:", state["free"][2, 0, 0])         # expect 0.05 (now loose)
print("bundled e:", state["bundled"][1, 0, 0])   # expect 1.0  (e fits itself, so it stays)