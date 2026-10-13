import pygame as pg
import config
import render
import world
import type_table as tt

pg.init()

# Window and font
width = config.CELL_SIZE * config.COLUMNS
height = config.CELL_SIZE * config.ROWS
screen = pg.display.set_mode(size=(width, height))
font = render.create_font()


#builds the tiny world: a source of s in the middle, and a seeker a few cells east of it
def setup_world():
    state = world.create_world()

    middle = (config.COLUMNS // 2, config.ROWS // 2) #(column, row)
    seeker_start = (config.COLUMNS // 2 + 8, config.ROWS // 2 + 3) #8 columns east and 3 rows north of the source

    #bundle 0: the source, made of e (at least 2 units so it doesn't dissolve from rounding at the threshold)
    world.add_bundle(state, 0, [middle], 1, 10.0)

    #bundle 1: the seeker, made of g
    world.add_bundle(state, 1, [seeker_start], 3, 3.0)

    return state


state = setup_world()
display_type = config.DISPLAY_TYPE #which type the window shows, can be changed with the number keys
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
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                paused = not(paused)

            elif (event.key == pg.K_RIGHT) and paused:
                state = world.tick(state)
                tick_count += 1

            #R restarts the world from the beginning
            elif event.key == pg.K_r:
                state = setup_world()
                tick_count = 0

            #number keys pick which type is shown (0 = ambient, 1 = e, 2 = s, 3 = g)
            elif pg.K_0 <= event.key <= pg.K_9:
                chosen = event.key - pg.K_0
                if chosen < tt.NUM_TYPES:
                    display_type = chosen

    # 2. Spend banked time on ticks
    if not paused:
        while time_bank >= tick_interval:
            state = world.tick(state)
            tick_count += 1
            time_bank -= tick_interval

    # 3. Draw the frame
    screen.fill((0, 0, 0))
    total = state["free"][display_type] + state["bundled"][display_type] #free plus bundled amount of the shown type
    render.draw(screen, total, font)
    pg.display.flip()

    #window title shows which type is being drawn and the current tick
    pg.display.set_caption(f"Showing: {tt.NAMES[display_type]}   tick {tick_count}" + ("   (paused)" if paused else ""))

    # 4. Wait to hold the frame rate, and bank the elapsed time
    dt = clock.tick(config.FPS)
    if not paused:
        time_bank += dt

pg.quit()