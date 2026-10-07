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


def flow(free):
    new = free.copy()
    types, rows, columns = free.shape

    for q in range (1, types, 1):#iterates through every types grid one at a time (we start at 1 to skip the ambient)
        shares = (config.HOP_RATE/4)*free[q] #multiply every cell in each types grid by the share rate

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


def tick(world):
    return flow(world)

