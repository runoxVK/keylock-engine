import numpy as np
import config
import type_table as tt

#East, West, North, South (Think of like unit vectors)
NEIGHBOR_STEPS = ((1,0), (-1,0), (0,1), (0,-1))

NO_OWNER = -1

FREE = 0 #index for free amounts
BUNDLED = 1

ALLOWED_KINDS = ((FREE, FREE), (FREE, BUNDLED), (BUNDLED, FREE))

#the five displacements a bundle can choose from (Definition 9): stay, East, West, North, South
DISPLACEMENTS = ((0,0), (1,0), (-1,0), (0,1), (0,-1))

#random number generator for motion (random order of bundles and breaking ties)
#seeded so the same seed gives the exact same run every time
rng = np.random.default_rng(config.SEED)

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
    # put `amount` of type q into it as bundled amounts.

    #cells input represent coordinate points (i,j) and the input will take a list of whatever cell coordinates you want the bundle to occupy
    for i,j in cells:
        world["owner"][j,i] = label #this bundle now owns the cell
        world["bundled"][q, j, i] += amount #add the bundle's amount there   
            

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

#releases cells from a bundle if the local bond is weak enough
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

#removes cells from a bundle if a cell has no type in it
def cleanup(world):
    bundled = world["bundled"]
    new_owner = world["owner"].copy()
    rows, columns = new_owner.shape

    #loop over every cell
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):
            #check if its owned AND every bundled amount there is zero
            if (new_owner[j,i] != NO_OWNER and np.all(bundled[:, j, i] == 0)):
                new_owner[j,i] = NO_OWNER

    return {"free":world["free"], "bundled":world["bundled"], "owner": new_owner}

#connection between two neighboring cells of a bundle (Definition 6)
#this is the link in both directions added together: how well the stuff in one cell fits the stuff in the other
def connection(bundled, j, i, nj, ni):
    gx = bundled[:, j, i] #all the bundled amounts of every type at the first cell
    gy = bundled[:, nj, ni] #all the bundled amounts of every type at the second cell

    #gx @ FIT @ gy does the double sum: every amount at x times every fit times every amount at y
    #first term is the link from x to y, second term is the link from y to x
    return gx @ tt.FIT @ gy + gy @ tt.FIT @ gx


#splits a bundle into separate bundles if its cells are no longer attached to each other (Definition V.3)
def split(world):
    bundled = world["bundled"]
    owner = world["owner"]
    new_owner = owner.copy()
    rows, columns = owner.shape

    #keeps track of which cells we already put into a group
    visited = np.zeros((rows, columns), dtype=bool)

    #new bundles need a label nobody is using yet, so start one past the biggest label there is
    next_label = owner.max() + 1

    #labels that already have a group, so the first group keeps the original label and any extra group gets a new one
    labels_used = []

    #go to every owned cell we haven't grouped yet
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):
            if (owner[j,i] != NO_OWNER and not visited[j,i]):
                bundle_owner = owner[j,i] #the bundle this cell belongs to

                #flood fill: start at this cell and keep stepping to attached neighbors until there are none left
                group = [] #every cell in this group
                to_visit = [(i, j)] #cells we still need to look at
                visited[j,i] = True

                while len(to_visit) > 0:
                    ci, cj = to_visit.pop() #take a cell off the list
                    group.append((ci, cj))

                    #look at its four neighbors
                    for di, dj in NEIGHBOR_STEPS:
                        ni = ci + di
                        nj = cj + dj

                        #only continue if that neighbor actually exists on the grid
                        if (ni >= 0 and ni < columns) and (nj >= 0 and nj < rows):
                            #the neighbor has to be the same bundle and not already in a group
                            if (owner[nj,ni] == bundle_owner and not visited[nj,ni]):
                                #only attached if the connection is strong enough
                                if connection(bundled, cj, ci, nj, ni) >= config.BOND_THRESHOLD:
                                    visited[nj,ni] = True
                                    to_visit.append((ni, nj))

                #the first group of a bundle keeps its label, any group after that becomes its own new bundle
                if bundle_owner in labels_used:
                    for gi, gj in group:
                        new_owner[gj,gi] = next_label
                    next_label += 1
                else:
                    labels_used.append(bundle_owner)

    return {"free": world["free"], "bundled": world["bundled"], "owner": new_owner}


#dissolves a bundle if its total bond strength is below the threshold (Definition V.4)
def dissolve(world):
    bundled = world["bundled"]
    owner = world["owner"]
    new_free = world["free"].copy()
    new_bundled = world["bundled"].copy()
    new_owner = owner.copy()
    rows, columns = owner.shape

    #bond strength of every bundle, stored by label (a dictionary: bond[label] = that bundle's bond strength)
    bond = {}

    #add up the bond strength of every bundle (Definition 6)
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):
            if (owner[j,i] != NO_OWNER):
                bundle_owner = owner[j,i]
                gx = bundled[:, j, i]

                #start this bundle at zero the first time we see it
                if bundle_owner not in bond:
                    bond[bundle_owner] = 0

                #cohesion: how well the stuff in this cell holds itself together
                bond[bundle_owner] += gx @ tt.FIT @ gx

                #links: how well this cell fits each neighboring cell of the same bundle
                for di, dj in NEIGHBOR_STEPS:
                    ni = i + di
                    nj = j + dj
                    if (ni >= 0 and ni < columns) and (nj >= 0 and nj < rows):
                        if (owner[nj,ni] == bundle_owner):
                            gy = bundled[:, nj, ni]
                            bond[bundle_owner] += gx @ tt.FIT @ gy #only one direction, the neighbor adds the other direction when we get to it

    #now dissolve every bundle that is too weak
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):
            if (owner[j,i] != NO_OWNER):
                bundle_owner = owner[j,i]
                if bond[bundle_owner] < config.BOND_THRESHOLD:
                    #everything in this cell becomes free and the cell isn't owned anymore
                    new_free[:, j, i] += bundled[:, j, i]
                    new_bundled[:, j, i] = 0
                    new_owner[j,i] = NO_OWNER

    return {"free": new_free, "bundled": new_bundled, "owner": new_owner}

#lists every cell a bundle owns, as (column, row) pairs
def bundle_cells(owner, b):
    rows, columns = owner.shape
    cells = []
    for j in range (0, rows, 1):
        for i in range (0, columns, 1):
            if (owner[j,i] == b):
                cells.append((i, j))
    return cells


#checks if a bundle has at least one drive (Definition 8): a type with a nonzero valence and some amount in the bundle
def has_drive(bundled, cells):
    types = bundled.shape[0]
    for i, j in cells:
        for q in range (1, types, 1):
            if (tt.VALENCES[q] != 0 and bundled[q,j,i] > 0):
                return True
    return False


#response of every type to one cell, leaving out bundle b's own amounts (Definition 5)
#gives back a list: R[q] = how much of what q's lock fits is in that cell, not counting b itself
def response_excluding(world, b, nj, ni):
    #total amount of every type in that cell
    amounts_here = world["free"][:, nj, ni] + world["bundled"][:, nj, ni]

    #if bundle b owns that cell, take its own amounts back out so it isn't attracted to itself
    if (world["owner"][nj,ni] == b):
        amounts_here = amounts_here - world["bundled"][:, nj, ni]

    #amounts_here @ FIT does the sum over r of amount of r * how well r's key fits q's lock, for every q at once
    return amounts_here @ tt.FIT


#checks that every cell of the bundle would still be on the grid after moving by (di, dj)
def is_valid(cells, di, dj, rows, columns):
    for i, j in cells:
        ni = i + di
        nj = j + dj
        if not ((ni >= 0 and ni < columns) and (nj >= 0 and nj < rows)):
            return False
    return True


#desirability of moving bundle b by (di, dj) (Definition VI.1)
#for every cell of the bundle: each drive's amount * its valence * its response to the cell it would move into
def desirability(world, b, cells, di, dj):
    U = 0
    for i, j in cells:
        ni = i + di
        nj = j + dj

        g = world["bundled"][:, j, i] #every bundled amount at this cell of the bundle
        R = response_excluding(world, b, nj, ni) #every type's response to the cell it would move into

        #(g * VALENCES) is each type's amount times its pull, then @ R adds up pull * response over every type
        #types with valence 0 contribute nothing, so only drives count
        U += (g * tt.VALENCES) @ R
    return U


#reactions across facing pairs when a move is blocked (forms R4 and R5)
#facing is a list of (i, j, ni, nj): a cell of the pushing bundle and the cell of the other bundle in front of it
def contact(world, facing):
    bundled = world["bundled"]
    new_bundled = bundled.copy()
    types = bundled.shape[0]

    for i, j, ni, nj in facing:
        gx = bundled[:, j, i] #pusher's amounts
        gy = bundled[:, nj, ni] #other bundle's amounts

        #raw amounts in both directions
        #raw_xy[q,r]: pusher's q (key side) with the other's r (lock side)   (R4)
        #raw_yx[q,r]: the other's q (key side) with the pusher's r (lock side) (R5)
        raw_xy = np.zeros((types, types))
        raw_yx = np.zeros((types, types))
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                raw_xy[q,r] = config.REACTION_RATE * gx[q] * gy[r] * (tt.FIT[q,r] + tt.CLASH[q,r])
                raw_yx[q,r] = config.REACTION_RATE * gy[q] * gx[r] * (tt.FIT[q,r] + tt.CLASH[q,r])

        #demand on every type in each of the two cells, same idea as in reactions
        demand_x = np.zeros(types)
        demand_y = np.zeros(types)
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                demand_x[q] += raw_xy[q,r] #the first amount is always used up
                demand_y[q] += raw_yx[q,r]
                if (tt.CLASH[q,r] > 0): #in erosion, the second amount is used up too
                    demand_y[r] += raw_xy[q,r]
                    demand_x[r] += raw_yx[q,r]

        #factors: scale down if there isn't enough to go around
        factor_x = np.ones(types)
        factor_y = np.ones(types)
        for t in range (0, types, 1):
            if (demand_x[t] > 0):
                factor_x[t] = min(1, gx[t] / demand_x[t])
            if (demand_y[t] > 0):
                factor_y[t] = min(1, gy[t] / demand_y[t])

        #apply both directions
        new_x = gx.copy()
        new_y = gy.copy()
        for q in range (0, types, 1):
            for r in range (0, types, 1):
                is_clash = tt.CLASH[q,r] > 0
                product = tt.PRODUCTS[r]

                #pusher's q acting on the other's r (R4): product goes into the other bundle
                scale = factor_x[q]
                if is_clash:
                    scale = min(scale, factor_y[r])
                rho = raw_xy[q,r] * scale
                new_x[q] -= rho
                if is_clash:
                    new_y[r] -= rho
                if product != tt.NONE:
                    new_y[product] += rho

                #the other's q acting on the pusher's r (R5): product goes into the pusher
                scale = factor_y[q]
                if is_clash:
                    scale = min(scale, factor_x[r])
                rho = raw_yx[q,r] * scale
                new_y[q] -= rho
                if is_clash:
                    new_x[r] -= rho
                if product != tt.NONE:
                    new_x[product] += rho

        new_bundled[:, j, i] = new_x
        new_bundled[:, nj, ni] = new_y

    return {"free": world["free"], "bundled": new_bundled, "owner": world["owner"]}


#moves a bundle by (di, dj): every one of its amounts shifts one cell, free amounts stay where they are
def translate(world, b, cells, di, dj):
    new_bundled = world["bundled"].copy()
    new_owner = world["owner"].copy()

    #copy the bundle's amounts out first, since old and new cells can overlap
    saved = []
    for i, j in cells:
        saved.append(world["bundled"][:, j, i].copy())

    #clear the old cells
    for i, j in cells:
        new_bundled[:, j, i] = 0
        new_owner[j,i] = NO_OWNER

    #write the amounts into the new cells
    for k in range (0, len(cells), 1):
        i, j = cells[k]
        ni = i + di
        nj = j + dj
        new_bundled[:, nj, ni] = saved[k]
        new_owner[nj,ni] = b

    return {"free": world["free"], "bundled": new_bundled, "owner": new_owner}


#motion (Definition VI.1): bundles with drives move one at a time in a random order
def motion(world):
    rows, columns = world["owner"].shape

    #every bundle label in the world (np.unique lists each label once), leaving out NO_OWNER
    labels = []
    for b in np.unique(world["owner"]):
        if (b != NO_OWNER):
            labels.append(b)

    #random order, so no bundle always goes first
    rng.shuffle(labels)

    for b in labels:
        #bundles can change while others move, so look at this one's cells now
        cells = bundle_cells(world["owner"], b)
        if (len(cells) == 0 or not has_drive(world["bundled"], cells)):
            continue #skip bundles that are gone or have no drive

        #score every valid displacement
        options = []
        scores = []
        for di, dj in DISPLACEMENTS:
            if is_valid(cells, di, dj, rows, columns):
                options.append((di, dj))
                scores.append(desirability(world, b, cells, di, dj))

        #pick the best one, breaking ties at random
        best = max(scores)
        best_options = []
        for k in range (0, len(options), 1):
            if (scores[k] == best):
                best_options.append(options[k])
        di, dj = best_options[rng.integers(len(best_options))]

        #stay: nothing happens
        if (di == 0 and dj == 0):
            continue

        #look for facing pairs: cells of the bundle that would move into a cell owned by another bundle
        facing = []
        for i, j in cells:
            ni = i + di
            nj = j + dj
            other = world["owner"][nj,ni]
            if (other != NO_OWNER and other != b):
                facing.append((i, j, ni, nj))

        if (len(facing) > 0):
            world = contact(world, facing) #blocked: stay put, and react across the boundary
        else:
            world = translate(world, b, cells, di, dj) #way is clear: move

    return world


#one tick of the world, in the order from Part II
def tick(world):
    world = flow(world) #free stuff spreads
    world = reactions(world) #stuff reacts
    world = release(world) #bundles drop what they don't hold
    world = cleanup(world) #empty cells stop belonging to bundles
    world = split(world) #bundles that came apart become separate bundles
    world = dissolve(world) #bundles too weak to hold together fall apart
    world = motion(world) #bundles with drives move or push
    return world


