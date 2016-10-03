import libtcodpy as libtcod
import map
import math
import gui
import __main__

def monster_death(monster):
    gui.message('{} is dead!'.format(monster.name.capitalize()))
    monster.char = '%'
    monster.color = libtcod.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of {}'.format(monster.name)
    monster.send_to_back()

def create_orc(map, x, y):
    fighter = Fighter(hp=10, defense=0, power=3, ondeath=monster_death)
    ai = BasicMonster()
    orc = Object(map, x, y, 'o', 'orc', libtcod.desaturated_green, blocks=True)
    orc.register_components(fighter=fighter, ai=ai)
    return orc

def create_troll(map, x, y):
    fighter = Fighter(hp=15, defense=1, power=4, ondeath=monster_death)
    ai = BasicMonster()
    troll = Object(map, x, y, 'T', 'troll', libtcod.darker_green, blocks=True)
    troll.register_components(fighter=fighter, ai=ai)
    return troll

class BasicMonster:
    def take_turn(self):
        monster = self.owner
        if not libtcod.map_is_in_fov(monster.map.fov_map, monster.x, monster.y):
            return
        # we are in the fov map and can see each other
        if monster.distance_to(__main__.player) >= 2:
            monster.move_towards(__main__.player.x, __main__.player.y)
        else:
            # close enough to attack
            if __main__.player.fighter.hp > 0:
                monster.fighter.attack(__main__.player)


class Fighter:
    def __init__(self, hp, defense, power, **kwargs):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power

        self.death_function = kwargs.get('ondeath', None)
        self.color_dmg = kwargs.get('color_dmg', libtcod.orange)
        self.color_heal = kwargs.get('color_heal', libtcod.light_crimson)
        self.color_whiff = kwargs.get('color_whiff', libtcod.light_sea)

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            gui.message("{} attacks {} for {} hp damage!".format(
                self.owner.name.capitalize(), target.name, damage
            ), self.color_dmg)
            target.fighter.take_damage(damage)
        else:
            gui.message("{} attacks {} for no effect.".format(
                self.owner.name.capitalize(), target.name
            ), self.color_whiff)

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

    def heal(self, amount):
        gui.message("{} is healed for {}".format(self.owner.name, amount),
            self.color_heal)
        self.hp = min(self.hp+amount, self.max_hp)
        return ('heal', 0)

class Object:
    # Generic object: player, monster, item, stairs...

    def __init__(self, map, x, y, char, name, color, **kwargs):
        self.map = map
        self.x = x
        self.y = y
        self.char = char
        self.name = name
        self.color = color

        self.blocks = kwargs.get('blocks', False)
        self.fighter = None
        self.ai = None

    def register_components(self, **kwargs):
        if 'fighter' in kwargs:
            self.fighter = kwargs['fighter']
            self.fighter.owner = self
        if 'ai' in kwargs:
            self.ai = kwargs['ai']
            self.ai.owner = self


    def move(self, **kwargs):
        # move to or attack to indicated offset
        # return action description and number of actions it takes

        # attempt to find an attackable object at indicated offset
        x = self.x + kwargs['dx']
        y = self.y + kwargs['dy']
        target = None
        for object in self.map.objects:
            if object.x == x and object.y == y and object.fighter != None:
                target = object
                break

        if target is None:
            # try to move if we found no target
            self._moveto(x, y)
            action = 'move'
        else:
            # since we have a target we should attack it
            self.fighter.attack(target)
            action = 'fight'

        return (action, 1)

    def _moveto(self, x, y):
        # move to square if it is not blocked
        if not self.map.is_blocked(x, y):
            self.x = x
            self.y = y
            self.map.fov_dirty = True

    def move_towards(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self._moveto(self.x+dx, self.y+dy)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def wait(self):
        # spend 1 action doing nothing
        return ('wait', 1)

    def draw(self):
        # set the color and draw the character at its position
        libtcod.console_set_default_foreground(gui.con, self.color)
        libtcod.console_put_char(gui.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        libtcod.console_put_char_ex(gui.con, self.x, self.y, '.',
            libtcod.white, libtcod.BKGND_NONE)

    def send_to_back(self):
        # make sure we get drawn over by pretty much anything else
        self.map.objects.remove(self)
        self.map.objects.insert(0, self)
