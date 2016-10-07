import libtcodpy as libtcod
import map
import math
import gui
import __main__

ZAP_MAX_DISTANCE    = 10
CONFUSE_TURNS       = 10

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

def scroll_confuse(source):
    target = source.nearest_enemy(ZAP_MAX_DISTANCE)
    if target.ai == None:
        gui.message("{} is not a valid target for confuse".format(
            target.name
        ), libtcod.white)
        return 'canceled'
    else:
        old_ai = target.ai
        target.register_components(ai=ConfusedMonster(old_ai))
        gui.message("{} looks confused".format(
            target.name
        ), libtcod.light_lime)
        return 'completed'

def create_scroll_confuse(map, x, y):
    scroll = Object(map, x, y, '?', 'confusion scroll', libtcod.yellow)
    item_logic = Item(scroll_confuse)
    scroll.register_components(item=item_logic)
    return scroll

def healing_potion(subject):
    hp = libtcod.random_get_int(0, 1, 10)
    subject.fighter.heal(hp)
    gui.message("{} drinks a healing potion and is healed {} hp".format(
        subject.name, hp
    ), libtcod.pink)

def create_healing_potion(map, x, y):
    potion = Object(map, x, y, '!', 'healing potion', libtcod.violet)
    item_logic = Item(healing_potion)
    potion.register_components(item=item_logic)
    return potion

def scroll_zap(source):
    dmg = libtcod.random_get_int(0, 10, 20)
    target = source.nearest_enemy(ZAP_MAX_DISTANCE)
    if target == None:
        gui.message("There is nothing to zap", libtcod.darkest_cyan)
        return 'canceled'
    else:
        gui.message("{} zaps {} for {} damage".format(
            source.name, target.name, dmg
        ), libtcod.darkest_cyan)
        target.fighter.take_damage(dmg)
        return 'completed'

def create_scroll_zap(map, x, y):
    scroll = Object(map, x, y, '?', 'zap scroll', libtcod.darkest_cyan)
    item_logic = Item(scroll_zap)
    scroll.register_components(item=item_logic)
    return scroll

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

class ConfusedMonster:
    def __init__(self, old_ai, num_turns=CONFUSE_TURNS):
        self.old_ai = old_ai
        self.num_turns = num_turns
    def take_turn(self):
        # move/attack in random direction
        if self.num_turns > 0:
            x = libtcod.random_get_int(0, -1, 1)
            y = libtcod.random_get_int(0, -1, 1)
            self.owner.move(dx=x, dy=y)
            self.num_turns -= 1
        else:
            self.owner.ai = self.old_ai
            gui.message("{} is no longer confused!".format(
                self.owner.name
            ), libtcod.red)

class Item:
    def __init__(self, use_fn):
        self.use_fn = use_fn
    def use(self, subject):
        return self.use_fn(subject)

class PlayerInventory:
    def __init__(self):
        self.items = []

    def pick_up(self, item):
        # true if item successfully picked up
        if len (self.items) >= 26:
            gui.message("{} inventory full, cannot pick up {}".format(
                self.owner.name, item.name
            ), libtcod.dark_yellow)
            return False
        else:
            gui.message("{} picked up {}".format(
                self.owner.name, item.name
                ), libtcod.dark_green)
            self.items.append(item)
            return True

    def use(self, index, subject):
        item = self.items[index].item
        if item.use(subject) != 'canceled':
            del self.items[index]

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
        self.inventory = None
        self.item = None

    def register_components(self, **kwargs):
        if 'fighter' in kwargs:
            self.fighter = kwargs['fighter']
            self.fighter.owner = self
        if 'ai' in kwargs:
            self.ai = kwargs['ai']
            self.ai.owner = self
        if 'inventory' in kwargs:
            self.inventory = kwargs['inventory']
            self.inventory.owner = self
        if 'item' in kwargs:
            self.item = kwargs['item']
            self.item.owner = self

    def nearest_enemy(self, max_range):
        nearest = None
        nearest_dist = max_range + 1
        for object in self.map.objects:
            if not object.fighter or object == self: continue
            if not libtcod.map_is_in_fov(self.map.fov_map, object.x, object.y):
                continue
            distance = self.distance_to(object)
            if distance < nearest_dist:
                nearest = object
                nearest_dist = distance
        return nearest

    def pick_up(self):
        # pick up first item at current location
        for item in self.map.objects:
            if item.item != None and item.x == self.x and item.y == self.y:
                if self.inventory.pick_up(item):
                    self.map.objects.remove(item)
                    return ('pickup', 1)
        # if we got to the end then there was nothing picked up
        return ('pickup', 0)

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
        if libtcod.map_is_in_fov(self.map.fov_map, self.x, self.y) or self.name == 'room_name':
            # only draw what is visible to the player
            libtcod.console_set_default_foreground(gui.con, self.color)
            libtcod.console_put_char(gui.con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def clear(self):
        # erase the character that represents this object
        if libtcod.map_is_in_fov(self.map.fov_map, self.x, self.y) and self.name != 'room_name':
            libtcod.console_put_char_ex(gui.con, self.x, self.y, '.',
                libtcod.white, libtcod.BKGND_NONE)

    def send_to_back(self):
        # make sure we get drawn over by pretty much anything else
        self.map.objects.remove(self)
        self.map.objects.insert(0, self)
