import numpy as np
import config
import type_table as tt

#East, West, North, South (Think of like unit vectors)
NEIGHBOR_STEPS = ((1,0), (-1,0), (0,1), (0,-1))


#Create World function
#A world holds a cell grid per type, each type gets their own world grid for that type
def create_world(num_types=tt.NUM_TYPES, rows=config.ROWS , columns=config.COLUMNS):

    #This function will create a matrix of all zeros
    #free represents the free amounts of each type at each cell
    free = np.zeros((num_types, rows, columns), dtype=float)
    free[0] = 1 #setting the ambient to one

    #Ex. free[q, j, i] = how much free type q is at row j, column i
    return free

def binding(free, q):
    types, rows, columns = free.shape
    E = np.zeros((rows, columns)) #the binding of type q at every cell of the grid

    for r in range(0, types, 1):
        E += free[r] * tt.FIT[q,r] #definiton of binding (free amount of type r * the fit that q's key fits into r's lock)

    return E

def flow(free):
    new = free.copy()
    types, rows, columns = free.shape

    for q in range (1, types, 1):#iterates through every types grid one at a time (we start at 1 to skip the ambient)
        E = binding(free, q)
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
    return new

#reaction function is very dense - come back here to check
def reactions(free):
    # Reactions between free amounts (Part IV, form R1).
    #every amount used in a calculation comes from free
    new = free.copy()
    types, rows, columns = free.shape

    #raw[q, r] is a 2D grid: how much type q (the key side) would react with type r
    raw = np.zeros((types, types, rows, columns))

    #go through every ordered pair (q, r). Both loops start at 0 so the ambient is included:
    for q in range (0, types, 1):
        for r in range (0, types, 1):
            if q != r:   # a free type never reacts with itself (Remark IV.3)
                #definition of raw amount product
                #pairs that neither fit nor clash get 0 and don't react.
                raw[q,r] = config.REACTION_RATE * free[q] * free[r] * (tt.FIT[q,r] + tt.CLASH[q,r]) #definition of raw reaction amount
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

