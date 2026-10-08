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

def add_bundle(world, label, cells, q, amount):
    # give each listed cell to bundle `label`,
    # put `amount` of type q into it as bundled material.

    #cells input represent coordinate points (i,j) and the input will take a list of whatever cell coordinates you want the bundle to occupy
    for i,j in cells:
        world["owner"][j,i] = label #this bundle now owns the cell
        world["bundled"][q, j, i] += amount #add the bundle's material there   
            

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

    # demand[k,t] is a grid: in each cell, the total amount that all pairs together want to take from type t of kind k
    demand = np.zeros((kinds, types, rows, columns))
    #holds, in every cell, the total that all reactions want from type t.

    for k1, k2 in ALLOWED_KINDS: 
        #goes through every pair (q,r) and records what that pair would use up
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                if not (k1 == FREE and k2 == FREE and q == r): 
                    if q != 0: #q is NOT the ambient
                        demand[k1,q] += raw[k1,q,k2,r]   #q is always used up by its own reactions
                    if tt.CLASH[q,r] > 0 and r != 0: #if the type pair is a clash and r is not ambient
                        demand[k2,r] += raw[k1,q,k2,r]   #in erosion, r is worn down by the same amount

    #factors (Definition IV.4)
    #factor[k,t] says how much every reaction drawing on type t (with kind k) must be scaled down, in each cell
    #it starts at 1 everywhere, meaning "no scaling needed".
    factor = np.ones_like(amounts) #new array with same shape of free but filled with ones

    # Only cells where something is demanded can need scaling; elsewhere we leave the factor at 1
    has_demand = demand > 0
    # [[False,  True],
    #  [False, False]]

    #where there is demand: factor = min(1, amount available / amount demanded).
    factor[has_demand] = np.minimum(1, amounts[has_demand] / demand[has_demand])

    #apply reaction
    for k1, k2 in ALLOWED_KINDS: 
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                if not (k1 == FREE and k2 == FREE and q == r): 
                    is_clash = tt.CLASH[q, r] > 0   #true means erosion; otherwise absorption (or no reaction)

                    #how much to shrink this reaction
                    #amounts this pair uses up (its consumption set). Start at 1, then lower it.
                    scale = np.ones((rows, columns))
                    if q != 0: #q is used up, unless it's the ambient
                        scale = np.minimum(scale, factor[k1,q])
                    if is_clash and r != 0: #in erosion, r is used up too, unless it's the ambient
                        scale = np.minimum(scale, factor[k2,r])
                    rho = raw[k1,q,k2,r] * scale #how much actually reacts, in each cell

                    #subtract from what this reaction uses up. The ambient is never reduced (Axiom A3).
                    if q != 0:
                        new[k1,q] -= rho
                    if is_clash and r != 0:
                        new[k2,r] -= rho

                    #product goes to the same kind as r, so a bundle keeps what it absorbs
                    #(form R1-R3), form in same cell
                    product = tt.PRODUCTS[r]
                    if product != tt.NONE:
                        new[k2,product] += rho

    
    return {"free": new[FREE], "bundled": new[BUNDLED], "owner": world["owner"]}

def release(world):
    bundled = world["bundled"]
    types, rows, columns = bundled.shape
    owner = world["owner"]
    new_free = world["free"].copy()
    new_bundled = world["bundled"].copy()

    #go to every owned cell, and every type in it
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):  
            #check if the cell is owned by a bundle
            if owner[j,i] != NO_OWNER:
                bundle_owner = owner[j,i] #set bundle to the bundle name

                #for each type t bundled in this cell (start at 1: the ambient is never bundled)
                for t in range (1, types, 1):
                    if bundled[t,j,i] > 0: #checks if there is more than zero of that type in the bundle
                        #local bond of type t at this cell
                        H = 0
          
                       #local bond (Definition 7): add up how well t fits, or is fitted by, each type u in this bundle here
                        for u in range(0, types, 1):
                            H += bundled[u,j,i]*(tt.FIT[t,u]+tt.FIT[u,t])
                        #neighbor check
                        for di, dj in NEIGHBOR_STEPS:
                            ni = i + di
                            nj = j + dj
                            #Only continue if that neighbor actually exists on the grid
                            if (ni >= 0 and ni< columns) and (nj >= 0 and nj < rows):
                                if (owner[nj,ni] == bundle_owner):
                                    #same as above but this time it is adding to the local bond by comparing to neighboring cells of the same bundle
                                    for u in range(0, types, 1):
                                        H += bundled[u,nj,ni]*(tt.FIT[t,u]+tt.FIT[u,t])

                        #now that H has been added up, we need to now use the Hold value to see if anything releases

                        if H == 0:
                            #if the hold is zero, release the bundled amount from the bundle turning it into a free amount
                            new_free[t,j,i] += bundled[t,j,i]
                            new_bundled[t,j,i] = 0
    return {"free": new_free, "bundled": new_bundled, "owner": owner}

                      


def tick(world):
    return release(reactions(flow(world)))

