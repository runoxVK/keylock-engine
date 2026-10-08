import pygame as pg
import config
import render
import world
import type_table as tt

pg.init()

# Window, font, and world
width = config.CELL_SIZE * config.COLUMNS
height = config.CELL_SIZE * config.ROWS
screen = pg.display.set_mode(size=(width, height))
font = render.create_font()

state = world.create_world()
# Place bundle 0: one cell in the middle of the grid, holding 1 unit of type 1 (e).
middle = (config.COLUMNS // 2, config.ROWS // 2)   # (column, row)
world.add_bundle(state, 0, [middle], 1, 10.0)

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

    # 2. Spend banked time on ticks
    if not paused:
        while time_bank >= tick_interval:
            state = world.tick(state)
            time_bank -= tick_interval

    # 3. Draw the frame
    screen.fill((0, 0, 0))
    total = state["free"][config.DISPLAY_TYPE] + state["bundled"][config.DISPLAY_TYPE]
    render.draw(screen, total, font)
    pg.display.flip()

    # 4. Wait to hold the frame rate, and bank the elapsed time
    dt = clock.tick(config.FPS)
    if not paused:
        time_bank += dt

pg.quit()