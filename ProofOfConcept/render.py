import pygame as pg
import numpy as np
import config
import type_table as tt

#Creates a font from system fonts
def create_font():
    return pg.font.SysFont("consolas", config.CELL_SIZE) #pg.font.SysFont(name, size, bold=False, italic=False)


#draws one type's grid in grayscale: brighter # means more of that type
def draw(screen, world, font):
    row, col = world.shape

    for j in range(0, row, 1):
        y = (row - 1 - j) * config.CELL_SIZE #y position of cell, flipped so north is up

        for i in range(0, col, 1):
            x = i * config.CELL_SIZE #x position of cell

            #This handles the color of each cell
            value = world[j, i]
            clamped_value = max(0, min(value, config.MAX_DISPLAY_VALUE))
            brightness = int((clamped_value/config.MAX_DISPLAY_VALUE)*255)
            color = (brightness, brightness, brightness)

            glyph = font.render("#", True, color)
            screen.blit(glyph, (x, y))


#draws every type at once: each cell shows the glyph of whatever type has the most there
def draw_world(screen, world_state, font):
    free = world_state["free"]
    bundled = world_state["bundled"]
    owner = world_state["owner"]
    types, rows, columns = free.shape

    for j in range(0, rows, 1):
        y = (rows - 1 - j) * config.CELL_SIZE #flipped so north is up

        for i in range(0, columns, 1):
            x = i * config.CELL_SIZE

            #cells that belong to a bundle show the bundle's main type at full brightness
            if (owner[j, i] != -1):
                amounts = bundled[:, j, i]
                full_brightness = True
            else:
                amounts = free[:, j, i]
                full_brightness = False

            #find the type with the most here, skipping the ambient (type 0)
            #np.argmax gives the position of the biggest value, +1 because we skipped the ambient
            t = 1 + np.argmax(amounts[1:])
            value = amounts[t]

            #skip cells with basically nothing in them
            if (value < 0.001):
                continue

            #square root brightness, so faint trails still show up instead of disappearing
            if full_brightness:
                brightness = 1
            else:
                brightness = min(1, (value / config.MAX_DISPLAY_VALUE) ** 0.5)

            r, g, b = tt.COLORS[t]
            color = (int(r * brightness), int(g * brightness), int(b * brightness))

            #bundled amounts use GLYPHS, free amounts use FREE_GLYPHS so you can tell them apart
            if full_brightness:
                symbol = tt.GLYPHS[t]
            else:
                symbol = tt.FREE_GLYPHS[t]
            glyph = font.render(symbol, True, color)
            screen.blit(glyph, (x, y))