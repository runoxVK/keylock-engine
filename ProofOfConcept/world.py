import numpy as np
import config

#Create World function that takes columns and rows as inputs with default values being the values set in config
def create_world(rows=config.ROWS , columns=config.COLUMNS): 
    #This function will create a matrix of all zeros using the numpy zeros function and the array is a floating point
    return np.zeros((rows, columns), dtype=float) #np.zeros((Tuple of rows and columns), dtype)

def tick(world):
    add = 1
    row, col = world.shape #world.shape = (row, col)


    #for i in range(start, end, step)
    for i in range(0, row, 2): 
        for j in range(0, col, 1):
            world[i,j] += add
        
    return world

