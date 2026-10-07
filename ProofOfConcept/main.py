import pygame as pg
import config
import render
import world

pg.init()

width = config.CELL_SIZE * config.COLUMNS
height = config.CELL_SIZE * config.ROWS
screen = pg.display.set_mode(size=(width, height))
font = render.create_font()
state = world.create_world()

clock = pg.time.Clock()
isRunning = True
paused = False

while isRunning:
    pg.event.get() #gets user input etc.
    screen.fill((0, 0, 0))
    render.draw(screen, state, font)
    pg.display.flip() #shows the render on screen
    clock.tick(config.FPS) #a slight wait function for steady FPS   

pg.quit()