import libtcodpy as libtcod
import object
import tile
import rect
import map
import sys
from command import Command
import gui

KEY_TEXTINPUT = 66 # SDL2 textinput event

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

def debug_print(obj):
    print "----------------------"
    for k in dir(obj):
        if not k.startswith('__'):
            print "{}: {}".format(k, str(getattr(obj, k)))

def player_death(player):
    global game_state
    game_state = 'dead'
    gui.message('You died!', libtcod.red)
    player.char = '%'
    player.color = libtcod.dark_red
    player.send_to_back()

commands = {
    ord('h'): Command.MOVE_LEFT,
    ord('l'): Command.MOVE_RIGHT,
    ord('j'): Command.MOVE_DOWN,
    ord('k'): Command.MOVE_UP,
    ord('y'): Command.MOVE_UP_LEFT,
    ord('u'): Command.MOVE_UP_RIGHT,
    ord('b'): Command.MOVE_DOWN_LEFT,
    ord('n'): Command.MOVE_DOWN_RIGHT,
    ord('q'): Command.HEAL_PLAYER,
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
    # handle input, return action description and number of turns
    # to advance time

    if gui.key.vk == libtcod.KEY_NONE:
        return ('idle', 0)

    if gui.key.vk == KEY_TEXTINPUT:
        # SDL2 sends both keydown and textinput events when key with
        # printable representation is pressed
        return ('ignore', 0)

    if gui.key.vk == libtcod.KEY_ESCAPE:
        return ('exit', 0)

    try:
        if gui.key.vk == libtcod.KEY_CHAR:
            command = commands[gui.key.c]
        else:
            command = commands[gui.key.vk]
    except KeyError as err:
        gui.message("error: unbound key: {}".format(err))
        debug_print(gui.key)
        return ('error', 0)

    (action, turns) = command()
    return (action, turns)

# main
if __name__ != '__main__': sys.exit(0)

gui.init()

objects = []
the_map = map.Map(MAP_WIDTH, MAP_HEIGHT, objects)
(player_x, player_y) = the_map.carve_rooms(
    MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
the_map.fov_init()

fighter = object.Fighter(hp=30, defense=2, power=5, ondeath=player_death)
player = object.Object(the_map, player_x, player_y,
    '@', 'player', libtcod.white, blocks=True)
player.register_components(fighter=fighter)
objects.append(player)
game_state = 'playing'

gui.message("Welcome to the game, welcome to your doom!", libtcod.darkest_violet)

while not libtcod.console_is_window_closed():
    turns = 0

    event = libtcod.sys_check_for_event(
        libtcod.EVENT_KEY_PRESS|libtcod.EVENT_MOUSE,
        gui.key, gui.mouse
    )

    gui.render_all(the_map)
    libtcod.console_flush()

    for object in objects:
        object.clear()

    (action, turns) = handle_keys()
    if action == 'exit':
        break

    if turns > 0:
        for object in objects:
            if object.ai != None:
                object.ai.take_turn()

    if game_state == 'dead':
        gui.message("game over - press almost any key to continue", libtcod.yellow)
        gui.render_all(the_map)
        libtcod.console_flush()
        libtcod.console_wait_for_keypress(True)
        break
