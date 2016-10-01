import libtcodpy as libtcod
import __main__

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

PANEL_HEIGHT = 7
BAR_WIDTH = 20

PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

def init():
    global con, panel
    libtcod.console_set_custom_font('arial10x10.png',
        libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
        'pyr mainscreen', False)
    libtcod.sys_set_fps(LIMIT_FPS)
    con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)


def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    # bar background first
    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False,
        libtcod.BKGND_SCREEN)

    # now render the bar on top
    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    # display some info
    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE,
        libtcod.CENTER, '{}: {}/{}'.format(
            name, value, maximum
        )
    )

def render_all(map):
    # draw walls, floors and all the objects on this map
    if map.fov_dirty:
        map.fov_recompute(__main__.player)

        for y in range(map.height):
            for x in range(map.width):
                visible = libtcod.map_is_in_fov(map.fov_map, x, y)
                wall = map.map[x][y].block_sight
                if not visible:
                    if map.map[x][y].explored:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, '#',
                                color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_put_char_ex(con, x, y, '.',
                                color_dark_ground, libtcod.BKGND_SET)
                else:
                    map.map[x][y].explored = True
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, '#',
                            color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_put_char_ex(con, x, y, '.',
                            color_light_ground, libtcod.BKGND_SET)

    for object in map.objects:
        object.draw()

    # blit con to root console
    libtcod.console_blit(con, 0, 0, map.width, map.height, 0, 0, 0)

    # prepare to render gui panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    game_msgs = [("hello", libtcod.white), ("goodbye", libtcod.white)]
    # display messages, 1 line at a time
    y = 1
    for (line, color) in game_msgs:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE,
            libtcod.LEFT, line)
        y += 1

    render_bar(1, 1, BAR_WIDTH, 'HP', __main__.player.fighter.hp,
        __main__.player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    ## libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    # blit the bar to root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
