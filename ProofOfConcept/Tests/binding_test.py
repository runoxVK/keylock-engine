import world

state = world.create_world()

# 1. Binding of e (type 1): nothing present fits e's key, not even the ambient
E_e = world.binding(state, 1)
print("e binding, min and max:", E_e.min(), E_e.max())        # expect 0.0 0.0

# 2. Binding of s (type 2): the ambient holds s with fit 0.2 in every cell
E_s = world.binding(state, 2)
print("s binding, min and max:", E_s.min(), E_s.max())        # expect 0.2 0.2 (may show 0.19999999999999998)

# 3. Put 2 units of g (type 3) in one cell: g's lock holds s's key with fit 0.9
state[3, 5, 5] = 2
E_s = world.binding(state, 2)
print("s binding at (5,5):", E_s[5, 5])                        # expect 2.0  (0.2 + 2 x 0.9)
print("s binding next door at (5,6):", E_s[5, 6])              # expect 0.2  (only the ambient)