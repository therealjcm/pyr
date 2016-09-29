import libtcodpy as libtcod
import object
import tile
import rect
import map
import sys
from command import Command

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

MAP_WIDTH = 80
MAP_HEIGHT = 45

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

commands = {
    ord('h'): Command.MOVE_LEFT,
    ord('l'): Command.MOVE_RIGHT,
    ord('j'): Command.MOVE_DOWN,
    ord('k'): Command.MOVE_UP,
    ord('y'): Command.MOVE_UP_LEFT,
    ord('u'): Command.MOVE_UP_RIGHT,
    ord('b'): Command.MOVE_DOWN_LEFT,
    ord('n'): Command.MOVE_DOWN_RIGHT,
    libtcod.KEY_UP: Command.MOVE_UP,
    libtcod.KEY_DOWN: Command.MOVE_DOWN,
    libtcod.KEY_LEFT: Command.MOVE_LEFT,
    libtcod.KEY_RIGHT: Command.MOVE_RIGHT,
    libtcod.KEY_KP9: Command.MOVE_UP_RIGHT,
    libtcod.KEY_KP8: Command.MOVE_UP,
    libtcod.KEY_KP7: Command.MOVE_UP_LEFT,
    libtcod.KEY_KP5: Command('__main__.player.wait'),
    libtcod.KEY_KP4: Command.MOVE_LEFT,
    libtcod.KEY_KP6: Command.MOVE_RIGHT,
    libtcod.KEY_KP1: Command.MOVE_DOWN_LEFT,
    libtcod.KEY_KP2: Command.MOVE_DOWN,
    libtcod.KEY_KP3: Command.MOVE_DOWN_RIGHT
}

def handle_keys():
    key = libtcod.console_wait_for_keypress(True) # turn based

    if key.vk == libtcod.KEY_ESCAPE:
        return True

    try:
        if key.vk == libtcod.KEY_CHAR:
            command = commands[key.c]
        else:
            command = commands[key.vk]
    except KeyError as err:
        print "error: unbound key pressed, code: {}".format(err)
        return False

    command()

# main
if __name__ != '__main__': sys.exit(0)

libtcod.console_set_custom_font('arial10x10.png',
    libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT,
    'pyr mainscreen', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

objects = []
the_map = map.Map(MAP_WIDTH, MAP_HEIGHT, objects)
(player_x, player_y) = the_map.carve_rooms(
    MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
the_map.fov_init()

player = object.Object(the_map, player_x, player_y,
    '@', 'player', libtcod.white, True)
objects.append(player)

while not libtcod.console_is_window_closed():
    the_map.render_all()
    libtcod.console_flush()

    for object in objects:
        object.clear()

    exit = handle_keys()
    if exit:
        break
