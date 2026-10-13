import world

state = world.create_world(rows=1, columns=8)
world.add_bundle(state, 0, [(0, 0)], 1, 2.0)   # bundle 0: the source, 2 units of e
world.add_bundle(state, 1, [(6, 0)], 3, 2.0)   # bundle 1: the seeker, 2 units of g

for t in range(60):
    state = world.tick(state)
    g_column = world.bundle_cells(state["owner"], 1)
    print("tick", t + 1, " seeker at:", g_column, "  free s:", state["free"][2, 0].round(3))