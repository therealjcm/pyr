import libtcodpy as libtcod

class Rect:
    # a rectangle on the map
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h

    def __str__(self):
        return "x1:{}, x2:{}, y1:{}, y2:{}".format(
            self.x1, self.x2, self.y1, self.y2
        )

    def center(self):
        # center of this rectangle as a tuple of tile coordinates
        x = (self.x1 + self.x2) / 2
        y = (self.y1 + self.y2) / 2
        return (x, y)

    def size(self):
        # do not count border in room size
        x = (self.x2 - self.x1) - 1
        y = (self.y2 - self.y1) - 1
        return x * y

    def random_coord(self):
        x = libtcod.random_get_int(0, self.x1+1, self.x2-1)
        y = libtcod.random_get_int(0, self.y1+1, self.y2-1)
        return (x, y)

    def intersect(self, other):
        # true if this rectangle intersects with another
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
