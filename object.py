import libtcodpy as libtcod
import map
import __main__

class Object:
    # Generic object: player, monster, item, stairs...

    def __init__(self, map, x, y, char, name, color, blocks=False):
        self.map = map
        self.con = __main__.con
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color
        self.blocks = blocks

    def move(self, **kwargs):
        # move by the given amount if not blocked
        if not self.map.is_blocked(self.x + kwargs['dx'], self.y + kwargs['dy']):
            self.x += kwargs['dx']
            self.y += kwargs['dy']
            self.map.fov_dirty = True

    def wait(self):
        pass

    def draw(self):
        # set the color and draw the character at its position
        libtcod.console_set_default_foreground(self.con, self.color)
        libtcod.console_put_char(self.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char_ex(self.con, self.x, self.y, '.',
            libtcod.white, libtcod.BKGND_SET)
            #libtcod.white, libtcod.dark_blue)
