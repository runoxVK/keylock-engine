import numpy as np
import config

NAMES = ["ambient", "e", "s", "g"]
NONE = -1   # marks "no product"
NUM_TYPES = len(NAMES)

# Keys: one row per type, in the same order as NAMES.
KEYS = np.array([
    [0.0, 1.0],   # ambient
    [0.0, 1.0],   # e - lines up with its own lock, so e holds itself together and can form a bundle
    [1.0, 0.0],   # s - lines up weakly with the ambient's lock, so it slowly decays
    [0.0, 1.0],   # g - lines up with the second part of its own lock, so g can form a bundle
], dtype=float)

# Locks: one row per type, in the same order as NAMES.
LOCKS = np.array([
    [0.3, 0.0],   # ambient
    [0.0, 0.6],   # e - lines up with the ambient's key, therefore produces its product
    [0.0, 0.0],   # s - fits nothing, so nothing in the world is changed by s's lock
    [1.0, 0.6],   # g - its first part lines up with s's key, so g absorbs s and, being a drive, is drawn toward it
], dtype=float)

# Products: the index of the type each type produces, or NONE.
PRODUCTS = np.array([
    NONE,   # ambient
    2,      # e - produces s, which is at index 2 in NAMES
    NONE,   # s
    NONE,   # g
], dtype=int)

# Valences: which way a type pulls the bundle it's in.
VALENCES = np.array([
    0,      # ambient - no pull
    0,      # e
    0,      # s
    1,      # g - pulls toward cells containing what its lock fits
], dtype=int)

AFFINITY = np.zeros((NUM_TYPES, NUM_TYPES))
FIT = np.zeros((NUM_TYPES, NUM_TYPES))
CLASH = np.zeros((NUM_TYPES, NUM_TYPES))


for q in range(0, NUM_TYPES, 1):
    for r in range(0, NUM_TYPES, 1):
        AFFINITY[q,r] = np.dot(KEYS[q],LOCKS[r])
        FIT[q,r] = max(0, AFFINITY[q,r]- config.DEAD_ZONE)
        CLASH[q,r] = max(0, -AFFINITY[q,r] - config.DEAD_ZONE)

#Checks to make sure all valeus are valid: 

#Every key and lock has exactly DIM numbers, and there is one per type.
assert KEYS.shape == (NUM_TYPES, config.DIM), "KEYS must have one row of DIM numbers per type"
assert LOCKS.shape == (NUM_TYPES, config.DIM), "LOCKS must have one row of DIM numbers per type"

# One product and one valence per type.
assert PRODUCTS.shape == (NUM_TYPES,), "PRODUCTS must have one entry per type"
assert VALENCES.shape == (NUM_TYPES,), "VALENCES must have one entry per type"

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