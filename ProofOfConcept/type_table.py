import numpy as np
import config

#the fire world: wood that burns, embers that keep it burning, heat that spreads, stone that doesn't burn, and ice that melts into water
NAMES = [
    "ambient",   # 0 - the background
    "wood",      # 1 - structure material, burns when heat touches it
    "ember",     # 2 - what burning wood turns into, gives off heat until it burns out
    "heat",      # 3 - free stuff that spreads and cools down
    "stone",     # 4 - structure material, heat does nothing to it
    "ice",       # 5 - structure material, melts when heat touches it
    "water",     # 6 - what ice melts into, soaks up heat and embers
]
NONE = -1   # marks "no product"
NUM_TYPES = len(NAMES)

# Keys: one row per type, in the same order as NAMES.
#every type's key points along its own axis, so LOCKS[r][q] reads as how strongly r responds to q
#positive = fit (absorbs and holds), negative = clash (wears down)
KEYS = np.eye(NUM_TYPES)

# Locks: one row per type, in the same order as NAMES.
#columns:   amb  wood ember heat stone ice  water
LOCKS = np.array([
    [0.0, 0.0, 0.2, 0.2, 0.0, 0.0, 0.0],  # ambient - embers slowly burn out, heat slowly cools
    [0.0, 0.6, 0.6,-1.0, 0.0, 0.0, 0.0],  # wood - holds itself and its embers together, CLASHES with heat (burns)
    [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # ember - taps the ambient, so embers give off heat
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  # heat - fits nothing
    [0.0, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0],  # stone - holds itself together, nothing else touches it
    [0.0, 0.0, 0.0,-0.6, 0.0, 0.6, 0.0],  # ice - holds itself together, CLASHES with heat (melts)
    [0.0, 0.0, 0.6, 0.6, 0.0, 0.0, 0.0],  # water - soaks up embers and heat (puts fire out)
], dtype=float)

# Products: the index of the type each type produces, or NONE.
PRODUCTS = np.array([
    NONE,   # ambient
    2,      # wood - burning turns it into embers (they stay inside the wood)
    3,      # ember - gives off heat
    NONE,   # heat
    NONE,   # stone
    6,      # ice - melting turns it into water (water doesn't fit ice, so it gets released and flows away)
    NONE,   # water
], dtype=int)

# Valences: nothing in this world moves on its own
VALENCES = np.array([
    0,      # ambient
    0,      # wood
    0,      # ember
    0,      # heat
    0,      # stone
    0,      # ice
    0,      # water
], dtype=int)

#what bundled amounts of each type look like on screen (display only, the laws never see these)
GLYPHS = [
    " ",   # ambient - never drawn
    "#",   # wood
    "*",   # ember (a burning wood cell shows * once it has more ember than wood left)
    "^",   # heat
    "%",   # stone
    "=",   # ice
    "~",   # water
]

#what free amounts of each type look like (bundled amounts use GLYPHS)
FREE_GLYPHS = [
    " ",   # ambient - never drawn
    ",",   # wood - loose wood from a collapsed structure
    ".",   # ember - sparks that fell out of burnt-through wood
    "^",   # heat
    ",",   # stone - loose stone
    ",",   # ice - loose ice
    "~",   # water
]

#color of each type as (red, green, blue)
COLORS = [
    (0, 0, 0),         # ambient
    (170, 110, 60),    # wood - brown
    (255, 150, 40),    # ember - orange
    (255, 70, 40),     # heat - red
    (160, 160, 170),   # stone - gray
    (170, 230, 255),   # ice - pale blue
    (60, 120, 255),    # water - blue
]

AFFINITY = np.zeros((NUM_TYPES, NUM_TYPES))
FIT = np.zeros((NUM_TYPES, NUM_TYPES))
CLASH = np.zeros((NUM_TYPES, NUM_TYPES))


for q in range(0, NUM_TYPES, 1):
    for r in range(0, NUM_TYPES, 1):
        AFFINITY[q,r] = np.dot(KEYS[q],LOCKS[r])
        FIT[q,r] = max(0, AFFINITY[q,r]- config.DEAD_ZONE)
        CLASH[q,r] = max(0, -AFFINITY[q,r] - config.DEAD_ZONE)

#Checks to make sure all values are valid:

#Every key and lock has exactly DIM numbers, and there is one per type.
assert KEYS.shape == (NUM_TYPES, config.DIM), "KEYS must have one row of DIM numbers per type"
assert LOCKS.shape == (NUM_TYPES, config.DIM), "LOCKS must have one row of DIM numbers per type"

# One product and one valence per type.
assert PRODUCTS.shape == (NUM_TYPES,), "PRODUCTS must have one entry per type"
assert VALENCES.shape == (NUM_TYPES,), "VALENCES must have one entry per type"

# One glyph, one free glyph, and one color per type.
assert len(GLYPHS) == NUM_TYPES, "GLYPHS must have one entry per type"
assert len(FREE_GLYPHS) == NUM_TYPES, "FREE_GLYPHS must have one entry per type"
assert len(COLORS) == NUM_TYPES, "COLORS must have one entry per type"

# No type produces the ambient (Axiom S4).
assert not np.any(PRODUCTS == 0), "No type may have the ambient as its product"

# The ambient produces nothing (Axiom S4).
assert PRODUCTS[0] == NONE, "The ambient's product must be NONE"

# Every product is NONE or a valid type index.
assert np.all((PRODUCTS == NONE) | ((PRODUCTS > 0) & (PRODUCTS < NUM_TYPES))), "Each product must be NONE or a valid type index"

# Valences are only -1, 0, or +1.
assert np.all(np.isin(VALENCES, [-1, 0, 1])), "Valences must be -1, 0, or +1"

# Fit and clash are never both positive (Definition 3).
assert not np.any((FIT > 0) & (CLASH > 0)), "A pair cannot both fit and clash"