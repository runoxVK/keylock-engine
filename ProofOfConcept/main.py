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


#builds a world with one source of s in the middle and four seekers around it
def setup_world():
    state = world.create_world()

    middle = (config.COLUMNS // 2, config.ROWS // 2) #(column, row)

    #bundle 0: the source, made of e
    world.add_bundle(state, 0, [middle], 1, 10.0)

    #bundles 1 to 4: seekers made of g, scattered around the source
    seeker_starts = [(5, 3), (34, 4), (8, 16), (31, 15)]
    for k in range(0, len(seeker_starts), 1):
        world.add_bundle(state, k + 1, [seeker_starts[k]], 3, 3.0)

    return state


state = setup_world()
display_type = config.DISPLAY_TYPE #0 shows everything, 1-3 show one type, can be changed with the number keys
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
                checks.check_world(state) #stop right away if anything impossible happened
                tick_count += 1

            #R restarts the world from the beginning
            elif event.key == pg.K_r:
                state = setup_world()
                tick_count = 0

            #number keys pick what is shown (0 = everything, 1 = e, 2 = s, 3 = g)
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