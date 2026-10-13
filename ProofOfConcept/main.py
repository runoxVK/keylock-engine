import pygame as pg
import config
import render
import world
import type_table as tt
import checks

pg.init()

# Window and font
width = config.CELL_SIZE * config.COLUMNS
height = config.CELL_SIZE * config.ROWS
screen = pg.display.set_mode(size=(width, height))
font = render.create_font()


#builds the fire world: a wooden building with a stone east wall, an ice wall to the west, and a fire starting on the west wall
def setup_world():
    state = world.create_world()

    #the building is a hollow rectangle from column 6 to 20 and row 4 to 15
    #the east wall (column 20) is stone, every other wall is wood
    wood_cells = []
    stone_cells = []
    for i in range(6, 21, 1):
        for j in range(4, 16, 1):
            if i == 20:
                stone_cells.append((i, j))
            elif i == 6 or j == 4 or j == 15:
                wood_cells.append((i, j))

    world.add_bundle(state, 0, wood_cells, tt.NAMES.index("wood"), 2.0) #bundle 0: all the wooden walls together
    world.add_bundle(state, 1, stone_cells, tt.NAMES.index("stone"), 2.0) #bundle 1: the stone wall

    #bundle 2: an ice wall a few cells west of the building
    ice_cells = []
    for j in range(2, 18, 1):
        ice_cells.append((3, j))
    world.add_bundle(state, 2, ice_cells, tt.NAMES.index("ice"), 2.0)

    #start the fire: a burst of heat right next to the west wall
    state["free"][tt.NAMES.index("heat"), 9, 5] += 20

    return state


state = setup_world()
display_type = config.DISPLAY_TYPE #0 shows everything, 1-6 show one type, can be changed with the number keys
tick_count = 0

clock = pg.time.Clock()
running = True
paused = False

# Fixed-rate ticking
tick_interval = 1000 / config.TICKS_PER_SEC   # milliseconds per tick
time_bank = 0

while running:
    # 1. Handle events
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        #clicking a cell drops a burst of heat there, so you can start fires anywhere
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            i = mouse_x // config.CELL_SIZE #column
            j = config.ROWS - 1 - mouse_y // config.CELL_SIZE #row, flipped because screen y goes down but rows go north
            state["free"][tt.NAMES.index("heat"), j, i] += 10

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                paused = not(paused)

            elif (event.key == pg.K_RIGHT) and paused:
                state = world.tick(state)
                checks.check_world(state) #stop right away if anything impossible happened
                tick_count += 1

            #R restarts the world from the beginning
            elif event.key == pg.K_r:
                state = setup_world()
                tick_count = 0

            #number keys pick what is shown (0 = everything, 1 to 6 = one type, in the order of NAMES)
            elif pg.K_0 <= event.key <= pg.K_9:
                chosen = event.key - pg.K_0
                if chosen < tt.NUM_TYPES:
                    display_type = chosen

    # 2. Spend banked time on ticks
    if not paused:
        while time_bank >= tick_interval:
            state = world.tick(state)
            checks.check_world(state) #stop right away if anything impossible happened
            tick_count += 1
            time_bank -= tick_interval

    # 3. Draw the frame
    screen.fill((0, 0, 0))
    if display_type == 0:
        render.draw_world(screen, state, font) #every type at once
    else:
        total = state["free"][display_type] + state["bundled"][display_type] #free plus bundled amount of one type
        render.draw(screen, total, font)
    pg.display.flip()

    #window title shows what is being drawn and the current tick
    shown = "everything" if display_type == 0 else tt.NAMES[display_type]
    pg.display.set_caption(f"Showing: {shown}   tick {tick_count}" + ("   (paused)" if paused else ""))

    # 4. Wait to hold the frame rate, and bank the elapsed time
    dt = clock.tick(config.FPS)
    if not paused:
        time_bank += dt

pg.quit()