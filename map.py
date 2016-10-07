import libtcodpy as libtcod
import tile
import rect
import object
import gui
import __main__

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

def coin_flip():
    # return random 0 or 1
    return libtcod.random_get_int(0, 0, 1)

def d100():
    # return 1-100
    return libtcod.random_get_int(0, 1, 100)

def d6(n=1):
    # return 1-6 per die
    dice = [libtcod.random_get_int(0, 1, 6) for i in range(n)]
    return sum(dice)

class Map:
    # the play field
    def __init__(self, width, height, objects):
        self.width = width
        self.height = height
        self.objects = objects
        self.fov_dirty = True # map is born needing fov
        self.fov_map = libtcod.map_new(width, height)
        self.map = [[ tile.Tile(True)
            for y in range(height)]
            for x in range(width)]

    def fov_init(self):
        # create initial fov according to generated level
        for y in range(self.height):
            for x in range(self.width):
                # fov map properties are opposite of tile map properties
                libtcod.map_set_properties(self.fov_map, x, y,
                    not self.map[x][y].block_sight, not self.map[x][y].blocked)

    def fov_recompute(self, pov):
        self.fov_dirty = False
        libtcod.map_compute_fov(self.fov_map, pov.x, pov.y, TORCH_RADIUS,
            FOV_LIGHT_WALLS, FOV_ALGO)

    def is_blocked(self, x, y):
        # return true if coordinate is blocked
        if self.map[x][y].blocked:
            return True

        # check all objects
        for object in self.objects:
            if object.blocks and object.x == x and object.y == y:
                return True

        return False

    def carve_rooms(self, num_rooms, min_room_size, max_room_size):
        rooms = []
        room_index = 0
        for r in range(num_rooms):
            w = libtcod.random_get_int(0, min_room_size, max_room_size)
            h = libtcod.random_get_int(0, min_room_size, max_room_size)
            x = libtcod.random_get_int(0, 0, self.width - w - 1)
            y = libtcod.random_get_int(0, 0, self.height - h - 1)

            new_room = rect.Rect(x, y, w, h)
            failed = False
            for other_room in rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break
            if failed: continue # next r

            # if we made it here then there are no overlaps
            self.create_room(new_room)
            self.populate_room(new_room)
            (new_x, new_y) = new_room.center()
            if room_index == 0:
                player_start = (new_x, new_y)
            else:
                # all rooms after first connect to previous room by tunnel
                (prev_x, prev_y) = rooms[room_index-1].center()
                if coin_flip() == 0:
                    # horizontal, then vertical
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # vertical, then horizontal
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)

            self.objects.insert(0, object.Object(self, new_x, new_y,
                chr(65+room_index), 'room_name', libtcod.white))
            rooms.append(new_room)
            room_index += 1
        return player_start

    def create_room(self, rect):
        # create a room according to the definition in the rectangle

        # go through the tiles in the room and unblock them
        # leave a one tile thick border for walls
        for x in range(rect.x1+1, rect.x2):
            for y in range(rect.y1+1, rect.y2):
                self.map[x][y].blocked = False
                self.map[x][y].block_sight = False

    def populate_room(self, rect):
        # place monsters and treasures within room defined by rectangle
        treasure_dice = rect.size() / 12
        max_monsters = rect.size() / 8
        num_monsters = libtcod.random_get_int(0, 0, max_monsters)
        for i in range(num_monsters):
            while True:
                # until we get a coordinate pair not in use
                (x, y) = rect.random_coord()
                if not self.is_blocked(x, y): break

            # we have useful coordinates
            if d100() < 80:
                monster = object.create_orc(self, x, y)
            else:
                monster = object.create_troll(self, x, y)
                # trolls have better treasure
                treasure_dice += 1
            self.objects.append(monster)

        treasure_value = d6(treasure_dice)
        while treasure_value > 0:
            while True:
                (x, y) = rect.random_coord()
                # treasure can stack on other objects, so ignore objects
                if not self.map[x][y].blocked: break
            treasure = d100()
            if treasure < 60:
                treasure_value -= 6
                item = object.create_healing_potion(self, x, y)
            elif treasure < 80:
                treasure_value -= 10
                item = object.create_scroll_zap(self, x, y)
            else:
                treasure_value -= 12
                item = object.create_scroll_confuse(self, x, y)

            self.objects.append(item)
            item.send_to_back() # draw last



    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.map[x][y].blocked = False
            self.map[x][y].block_sight = False
