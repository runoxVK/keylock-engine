import world

def fresh(rows=1, columns=1):
    return world.create_world(rows=rows, columns=columns)

# --- Test 1: Bundles grip free material (binding uses free + bundled) ---
# s's key fits g's lock with fit 0.9, and the ambient's lock with fit 0.2.
state = fresh()
world.add_bundle(state, 0, [(0, 0)], 3, 2.0)        # bundle 0: 2 units of g
print("binding of s:", world.binding(state, 2)[0, 0])          # expect 2.0  (0.2 + 2 x 0.9)

# --- Test 2: A source inside a bundle keeps its product ---
# The ambient's key fits e's lock (fit 0.5), and e's product is s.
# Since e is bundled, the s it produces lands inside the bundle (destination rule).
state = fresh()
world.add_bundle(state, 0, [(0, 0)], 1, 1.0)        # bundle 0: 1 unit of e
state = world.reactions(state)
print("bundled e:", state["bundled"][1, 0, 0])               # expect 1.0   (a converter, not used up)
print("bundled s:", state["bundled"][2, 0, 0])               # expect 0.05  (0.1 x 1 x 1 x 0.5)
print("free s:", state["free"][2, 0, 0])                     # expect 0.0   (nothing produced loose)

# --- Test 3: A bundle absorbs free material ---
# Free s fits bundled g's lock (0.9): 0.1 x 1 x 2 x 0.9 = 0.18 absorbed.
# Free s also decays into the ambient: 0.1 x 1 x 1 x 0.2 = 0.02.
# g has no product, so the absorbed s simply disappears.
state = fresh()
world.add_bundle(state, 0, [(0, 0)], 3, 2.0)        # bundle 0: 2 units of g
state["free"][2, 0, 0] = 1.0                        # 1 unit of free s
state = world.reactions(state)
print("free s:", state["free"][2, 0, 0])                     # expect 0.8   (1 - 0.18 - 0.02)
print("bundled g:", state["bundled"][3, 0, 0])               # expect 2.0   (unchanged)

# --- Test 4: Bundles don't move during flow ---
state = fresh(rows=1, columns=3)
world.add_bundle(state, 0, [(1, 0)], 1, 5.0)        # bundle in the middle cell
state = world.flow(state)
print("bundled e after flow:", state["bundled"][1, 0])      # expect [0. 5. 0.]
print("owner:", state["owner"][0])                           # expect [-1  0 -1]