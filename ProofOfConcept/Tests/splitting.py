import world

# healthy wall: 2 units of e in each of three cells in a row
state = world.create_world(rows=1, columns=3)
world.add_bundle(state, 0, [(0, 0), (1, 0), (2, 0)], 1, 2.0)
state = world.split(state)
state = world.dissolve(state)
print("healthy owners:", state["owner"][0])          # expect [0 0 0]  (still one bundle)

# damaged wall: the middle cell worn down to 0.2
state = world.create_world(rows=1, columns=3)
world.add_bundle(state, 0, [(0, 0), (2, 0)], 1, 2.0)
world.add_bundle(state, 0, [(1, 0)], 1, 0.2)
state = world.split(state)
print("after split:", state["owner"][0])             # expect three different labels, like [0 1 2]
state = world.dissolve(state)
print("after dissolve:", state["owner"][0])          # expect [ 0 -1  2]  (middle piece dissolved)
print("free e in middle:", state["free"][1, 0, 1])   # expect 0.2  (its material became free)