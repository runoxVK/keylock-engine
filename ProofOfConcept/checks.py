import numpy as np
import world

#small tolerance for floating point rounding, amounts can come out like -0.0000000000000001 instead of exactly 0
TOLERANCE = 1e-9

#checks things that must ALWAYS be true about the world, no matter the type table or constants
#if any of these fail there is a bug, and the message says which rule got broken
def check_world(world_state):
    free = world_state["free"]
    bundled = world_state["bundled"]
    owner = world_state["owner"]

    #the ambient's free amount is exactly 1 in every cell (Axiom A3)
    #nothing is ever allowed to change it, so it should still be exactly 1, not just close to 1
    assert np.all(free[0] == 1), "the ambient's free amount changed, something wrote to the ambient (Axiom A3)"

    #the ambient is never bundled (Axiom S5)
    assert np.all(bundled[0] == 0), "the ambient ended up bundled (Axiom S5)"

    #no amount is negative (clamping guarantees this, Proposition IV.5)
    #we allow a tiny bit below zero for rounding, anything more than that is a real bug
    assert np.all(free >= -TOLERANCE), "a free amount went negative, check reactions and clamping"
    assert np.all(bundled >= -TOLERANCE), "a bundled amount went negative, check reactions and clamping"

    #unowned cells have no bundled amounts (Axiom S5)
    #unowned is a grid of True/False: True wherever no bundle owns the cell
    unowned = owner == world.NO_OWNER
    #bundled[:, unowned] picks every type's bundled amount at just the unowned cells
    assert np.all(bundled[:, unowned] == 0), "a cell with no owner still has bundled amounts (Axiom S5)"