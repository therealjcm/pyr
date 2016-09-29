class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        # by default, if a tile is blocked it also blocks site
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

        # unexplored tiles are not shown
        self.explored = False
