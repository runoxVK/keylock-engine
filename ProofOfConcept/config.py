#World Config
COLUMNS = 40
ROWS = 20
CELL_SIZE = 20
TICKS_PER_SEC = 10
MAX_DISPLAY_VALUE = 3 #amount that shows as full brightness
FPS = 60

#Type table
DIM = 7 #dimension of signature space: one axis per type, so every key points along its own axis
DEAD_ZONE = 0.1

#For flow rate (D)
HOP_RATE = 0.4

#binding sensitivity (beta): how strongly being gripped slows spreading
BINDING_SENSITIVITY = 1

#reaction rate (kappa): how fast reactions happen
REACTION_RATE = 0.1

#bond threshold (theta): how strongly a bundle has to hold together to survive
BOND_THRESHOLD = 0.5

DISPLAY_TYPE = 0 #what the window shows at the start (0 = everything, 1 = e, 2 = s, 3 = g)

SEED = 1 #seed for the random number generator, so every run with the same seed plays out the same