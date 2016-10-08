import libtcodpy as libtcod
import textwrap
import __main__
import pprint

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

PANEL_HEIGHT = 7
BAR_WIDTH = 20

INVENTORY_WIDTH = 50

PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 180, 50)

def init():
    global con, panel, game_messages, mouse, key
    libtcod.console_set_custom_font('arial10x10.png',
        libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
        'pyr mainscreen', False)
    libtcod.sys_set_fps(LIMIT_FPS)
    con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
    panel = libtcod.console_new(SCREEN_WIDTH, PANEL_HEIGHT)
    mouse = libtcod.Mouse()
    key = libtcod.Key()
    game_messages = []

def get_names_at_mouse(map):
    # if mouse pointer is not in FOV then nada
    if not libtcod.map_is_in_fov(map.fov_map, mouse.cx, mouse.cy):
        return ''

    names = [obj.name for obj in map.objects
        if obj.x == mouse.cx and obj.y == mouse.cy]
    names = ', '.join(names)
    return names.capitalize()

def message(text, color=libtcod.white):
    global game_messages
    # wrap the message as needed
    new_lines = textwrap.wrap(text, MSG_WIDTH)

    for line in new_lines:
        # check for overflow and remove oldest first if needed
        if len(game_messages) == MSG_HEIGHT:
            del game_messages[0]

        # add new line as a tuple of text and color
        game_messages.append((line, color))

class CoordPath:
    NW =    (-1, -1)
    N =     (0, -1)
    NE =    (1, -1)
    E =     (1, 0)
    SE =    (1, 1)
    S =     (0, 1)
    SW =    (-1, 1)
    W =     (-1, 0)
    directions = {
        ord('h'): W,
        ord('l'): E,
        ord('j'): S,
        ord('k'): N,
        ord('y'): NW,
        ord('u'): NE,
        ord('b'): SW,
        ord('n'): SE,
        libtcod.KEY_UP: N,
        libtcod.KEY_DOWN: S,
        libtcod.KEY_LEFT: W,
        libtcod.KEY_RIGHT: E,
        libtcod.KEY_KP9: NE,
        libtcod.KEY_KP8: N,
        libtcod.KEY_KP7: NW,
        libtcod.KEY_KP5: (0, 0),
        libtcod.KEY_KP4: W,
        libtcod.KEY_KP6: E,
        libtcod.KEY_KP1: SW,
        libtcod.KEY_KP2: S,
        libtcod.KEY_KP3: SE
    }
    def __init__(self, source):
        self.coord_list = []
        self.x = source.x
        self.y = source.y
    def length(self):
        return len(self.coord_list)
    def is_source(self, x, y):
        if self.x == x and self.y == y: return True
        return False

def mode_targeting(source, max_distance, filter=None):
    # returns list of coordinate tuples
    # displays highlighted path to current cursor
    global key, mouse
    path = CoordPath(source)
    (cursor_x, cursor_y) = (source.x, source.y)
    while True:
        libtcod.console_flush()
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
            key, mouse)
        if key.vk == libtcod.KEY_NONE: continue # next key
        if key.vk == __main__.KEY_TEXTINPUT: continue # discard text event
        if key.vk == libtcod.KEY_ESCAPE:
            # bail and redraw without path
            source.map.fov_dirty = True
            render_all(source.map)
            return []
        try:
            if key.vk == libtcod.KEY_CHAR:
                (dx, dy) = CoordPath.directions[key.c]
            else:
                (dx, dy) = CoordPath.directions[key.vk]
        except KeyError as err:
            message("error: unbound key: {}".format(err))
            (dx, dy) = (0, 0)

        # got a valid direction
        new_x = cursor_x + dx
        new_y = cursor_y + dy
        update_cursor = False

        if (new_x, new_y) in path.coord_list:
            # backtracking, remove the previous tile and update cursor
            path.coord_list.pop()
            update_cursor = True

        if (new_x, new_y) not in path.coord_list and path.length() < max_distance:
            update_cursor = True

        if (path.is_source(new_x, new_y)):
            if path.length() == 1:
                path = CoordPath(source)
                (cursor_x, cursor_y) = (source.x, source.y)
                source.map.fov_dirty = True
                render_all(source.map)
            continue # either way we restart the loop

        if update_cursor:
            cursor_x = new_x
            cursor_y = new_y

        if (cursor_x, cursor_y) not in path.coord_list:
            path.coord_list.append((cursor_x, cursor_y))
        source.map.fov_dirty = True
        render_all(source.map, path.coord_list)

    return path.coord_list


def menu(header, options, width):
    if len(options) > 26: raise ValueError('menu allows 26 options maximum')

    header_height = libtcod.console_get_height_rect(
        con, 0, 0, width, SCREEN_HEIGHT, header)
    height = len(options) + header_height

    window = libtcod.console_new(width, height)

    libtcod.console_set_default_foreground(window, libtcod.white)
    libtcod.console_print_rect_ex(window, 0, 0, width, height,
        libtcod.BKGND_NONE, libtcod.LEFT, header)

    y = header_height
    letter_index = ord('a')
    for option_text in options:
        text = "({}) {}".format(chr(letter_index), option_text)
        libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE,
            libtcod.LEFT, text)
        y += 1
        letter_index += 1

    # render to root console
    x = SCREEN_WIDTH/2 - width/2
    y = SCREEN_HEIGHT/2 - height/2
    libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)
    libtcod.console_flush()
    menu_key = libtcod.console_wait_for_keypress(True)

    index = menu_key.c - ord('a')
    if index >= 0 and index < len(options): return index
    return None

def inventory_menu(header):
    items = __main__.player.inventory.items
    if len(items) == 0:
        options = ['inventory is empty']
    else:
        options = [item.name for item in items]

    index = menu(header, options, INVENTORY_WIDTH)
    if index is None or len(items) == 0: return ('backpack', 0)
    # activate the item
    __main__.player.inventory.use(index, __main__.player)
    return ('backpack', 1)

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

def render_all(map, path=[]):
    # draw walls, floors and all the objects on this map
    if map.fov_dirty:
        map.fov_recompute(__main__.player)

        for y in range(map.height):
            for x in range(map.width):
                visible = libtcod.map_is_in_fov(map.fov_map, x, y)
                wall = map.map[x][y].block_sight
                if (x, y) in path:
                    bkgnd = libtcod.light_grey
                else:
                    bkgnd = libtcod.BKGND_SET
                if not visible:
                    if map.map[x][y].explored:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, '#',
                                color_dark_wall, bkgnd)
                        else:
                            libtcod.console_put_char_ex(con, x, y, '.',
                                color_dark_ground, bkgnd)
                else:
                    map.map[x][y].explored = True
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, '#',
                            color_light_wall, bkgnd)
                    else:
                        libtcod.console_put_char_ex(con, x, y, '.',
                            color_light_ground, bkgnd)

    for object in map.objects:
        object.draw()

    # blit con to root console
    libtcod.console_blit(con, 0, 0, map.width, map.height, 0, 0, 0)

    # prepare to render gui panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # display messages, 1 line at a time
    y = 1
    for (line, color) in game_messages:
        libtcod.console_set_default_foreground(panel, color)
        libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE,
            libtcod.LEFT, line)
        y += 1

    render_bar(1, 1, BAR_WIDTH, 'HP', __main__.player.fighter.hp,
        __main__.player.fighter.max_hp, libtcod.light_red, libtcod.darker_red)

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)
    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT,
        get_names_at_mouse(map))

    # blit the bar to root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)
