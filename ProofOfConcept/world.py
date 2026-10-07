import numpy as np
import config
import type_table as tt

#East, West, North, South (Think of like unit vectors)
NEIGHBOR_STEPS = ((1,0), (-1,0), (0,1), (0,-1))

NO_OWNER = -1

FREE = 0 #index for free amounts
BUNDLED = 1

ALLOWED_KINDS = ((FREE, FREE), (FREE, BUNDLED), (BUNDLED, FREE))

#Create World function
#A world holds a cell grid per type, each type gets their own world grid for that type
def create_world(num_types=tt.NUM_TYPES, rows=config.ROWS , columns=config.COLUMNS):

    #This function will create a matrix of all zeros
    #free represents the free amounts of each type at each cell
    #Ex. free[q, j, i] = how much free type q is at row j, column i
    free = np.zeros((num_types, rows, columns), dtype=float)
    free[0] = 1 #setting the ambient to one

    bundled = np.zeros(free.shape) #analogous to the free array but now bundled
    owner = np.full((rows, columns), NO_OWNER, dtype=int) #which bundle owns every cell

    
    return {"free": free, "bundled": bundled, "owner": owner}

def binding(world, q):

    total = world["free"] + world["bundled"]
    types, rows, columns = total.shape
    E = np.zeros((rows, columns)) #the binding of type q at every cell of the grid

    for r in range(0, types, 1):
        E += total[r] * tt.FIT[q,r] #definiton of binding (amount of type r * the fit that q's key fits into r's lock)

    return E

def flow(world):
    free = world["free"]
    new = free.copy()
    types, rows, columns = free.shape

    for q in range (1, types, 1):#iterates through every types grid one at a time (we start at 1 to skip the ambient)
        E = binding(world, q)
        shares = (config.HOP_RATE/4)*free[q]*np.exp(-config.BINDING_SENSITIVITY * E) #multiply every cell in each types grid by the share rate and function of E

        #This loop now iterates through each individual cell of each type's grid
        for j in range (0, rows, 1):
            for i in range (0, columns, 1):
                for di, dj in NEIGHBOR_STEPS:
                    #Get each neighbors column and row
                    #For this cell, try each of the four directions
                    ni = i + di
                    nj = j + dj

                    #Only continue if that neighbor actually exists on the grid
                    if (ni >= 0 and ni< columns) and (nj >= 0 and nj < rows):
                        new[q, j, i] -= shares[j, i]      # this cell sends its share to the neighbor
                        new[q, j, i] += shares[nj, ni]    # and receives the neighbor's share

    return {"free": new, "bundled": world["bundled"], "owner": world["owner"]}

#reaction function is very dense - come back here to check
def reactions(world):

    #stacks free amounts and bundled amounts on top of eachother in a new dimension such that index zero will refer to the free array and index 1 refers to the bundled array
    amounts = np.stack((world["free"], world["bundled"]))

    #Reactions between free amounts (Part IV, form R1).
    #every amount used in a calculation comes from free
    new = amounts.copy()
    kinds, types, rows, columns = amounts.shape

    #Before introducing bundles: raw[q, r] is a 2D grid: how much type q (key side) would react with type r
    #After bundles: Then raw[k1, q, k2, r] is the grid for the pair "type q of kind k1, with type r of kind k2.
    raw = np.zeros((kinds, types, kinds, types, rows, columns))

    #for every allowed pair in allowe kinds (split into both specific kinds)
    for k1, k2 in ALLOWED_KINDS: 
        #go through every ordered pair of type (q, r). Both loops start at 0 so the ambient is included:
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                if not (k1 == FREE and k2 == FREE and q == r): # a free type never reacts with itself (Remark IV.3)
                    #definition of raw amount product
                    #pairs that neither fit nor clash get 0 and don't react.
                    raw[k1,q,k2,r] = config.REACTION_RATE * amounts[k1,q] * amounts[k2,r] * (tt.FIT[q,r] + tt.CLASH[q,r]) #definition of raw reaction amount
                    #represnts the raw reaction amount for every cell given a pair of types

    # demand[t] is a grid: in each cell, the total amount that all pairs together want to take from type t
    demand = np.zeros((types, rows, columns))
    #holds, in every cell, the total that all reactions want from type t.

    #goes through every pair (q,r) and records what that pair would use up
    for q in range (0, types, 1):
        for r in range (0, types, 1):
            if q != r:  
                if q != 0: #q is NOT the ambient
                    demand[q] += raw[q,r]   #q is always used up by its own reactions
                if tt.CLASH[q,r] > 0 and r != 0: #if the type pair is a clash and r is not ambient
                    demand[r] += raw[q,r]   #in erosion, r is worn down by the same amount

    #factors (Definition IV.4)
    #factor[t] says how much every reaction drawing on type t must be scaled down, in each cell
    #it starts at 1 everywhere, meaning "no scaling needed".
    factor = np.ones_like(free) #new array with same shape of free but filled with ones

    # Only cells where something is demanded can need scaling; elsewhere we leave the factor at 1
    has_demand = demand > 0

    #where there is demand: factor = min(1, amount available / amount demanded).
    factor[has_demand] = np.minimum(1, free[has_demand] / demand[has_demand])

    #apply reaction
    for q in range (0, types, 1):
        for r in range (0, types, 1):
            if q != r:
                is_clash = tt.CLASH[q, r] > 0   #true means erosion; otherwise absorption (or no reaction)

                #how much to shrink this reaction
                #amounts this pair uses up (its consumption set). Start at 1, then lower it.
                scale = np.ones((rows, columns))
                if q != 0: #q is used up, unless it's the ambient
                    scale = np.minimum(scale, factor[q])
                if is_clash and r != 0: #in erosion, r is used up too, unless it's the ambient
                    scale = np.minimum(scale, factor[r])
                rho = raw[q, r] * scale #how much actually reacts, in each cell

                #subtract from what this reaction uses up. The ambient is never reduced (Axiom A3).
                if q != 0:
                    new[q] -= rho
                if is_clash and r != 0:
                    new[r] -= rho

                #Add the product of r (the lock side). Since everything here is free
                #(form R1), the product is free too, in the same cell.
                product = tt.PRODUCTS[r]
                if product != tt.NONE:
                    new[product] += rho

    
    return new


def tick(world):
    return reactions(flow(world))

