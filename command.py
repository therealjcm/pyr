import __main__

class Command:
    @staticmethod
    def MOVE_DOWN_LEFT():
        return __main__.player.move(dx=-1, dy=1)
    @staticmethod
    def MOVE_DOWN():
        return __main__.player.move(dx=0, dy=1)
    @staticmethod
    def MOVE_DOWN_RIGHT():
        return __main__.player.move(dx=1, dy=1)
    @staticmethod
    def MOVE_LEFT():
        return __main__.player.move(dx=-1, dy=0)
    @staticmethod
    def MOVE_RIGHT():
        return __main__.player.move(dx=1, dy=0)
    @staticmethod
    def MOVE_UP_LEFT():
        return __main__.player.move(dx=-1, dy=-1)
    @staticmethod
    def MOVE_UP():
        return __main__.player.move(dx=0, dy=-1)
    @staticmethod
    def MOVE_UP_RIGHT():
        return __main__.player.move(dx=1, dy=-1)
    @staticmethod
    def HEAL_PLAYER():
        return __main__.player.fighter.heal(10)

    def __init__(self, methodname, *args, **kwargs):
        self.method = None
        self.methodname = methodname
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        if self.method == None:
            print "debug: eval {}".format(self.methodname)
            self.method = eval(self.methodname)
        return self.method(*self.args, **self.kwargs)
