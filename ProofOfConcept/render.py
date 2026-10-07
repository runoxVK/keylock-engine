import pygame as pg
import config

def draw(screen, world, font):
    row, col = world.shape

    for j in range(0, row, 1):
        y=(row-1-j)*config.CELL_SIZE #y posiion of cell

        for i in range(0, col, 1):
            x=i*config.CELL_SIZE #x position of cell

            #This handles the color of each cell            
            value = world[j, i] 
            clamped_value = max(0, min(value, config.MAX_DISPLAY_VALUE))
            brightness = int((clamped_value/config.MAX_DISPLAY_VALUE)*255)
            color = (brightness, brightness, brightness)


            glyph = font.render("#", True, color)
            screen.blit(glyph, (x,y)) #maps the # on cell (x,y)

def create_font():
    #Creates a font from system fonts
    return pg.font.SysFont("consolas", config.CELL_SIZE) #pg.font.SysFont(name, size, bold=False, italic=False)

