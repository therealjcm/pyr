import libtcodpy as libtcod
import object
import tile
import rect
import map
import sys
from command import Command
import gui

MAP_WIDTH = 80
MAP_HEIGHT = 43

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30

def player_death(player):
    global game_state
    game_state = 'dead'
    print 'You died!'
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
    key = libtcod.console_wait_for_keypress(True) # turn based

    if key.vk == libtcod.KEY_ESCAPE:
        return ('exit', 0)

    try:
        if key.vk == libtcod.KEY_CHAR:
            command = commands[key.c]
        else:
            command = commands[key.vk]
    except KeyError as err:
        print "error: unbound key pressed, code: {}".format(err)
        return ('error', 0)

    command()
    return ('play', 1)

# main
if __name__ != '__main__': sys.exit(0)

gui.init()

objects = []
the_map = map.Map(MAP_WIDTH, MAP_HEIGHT, objects)
(player_x, player_y) = the_map.carve_rooms(
    MAX_ROOMS, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
the_map.fov_init()

fighter = object.Fighter(hp=30, defense=2, power=5, death_function=player_death)
player = object.Object(the_map, player_x, player_y,
    '@', 'player', libtcod.white, blocks=True)
player.register_components(fighter=fighter)
objects.append(player)
game_state = 'playing'

while not libtcod.console_is_window_closed():
    turns = 0
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
        print "game over - press to continue"
        libtcod.console_wait_for_keypress(True)
        break
