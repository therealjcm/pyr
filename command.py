import __main__

class Command:
    @staticmethod
    def MOVE_DOWN_LEFT():
        __main__.player.move(dx=-1, dy=1)
    @staticmethod
    def MOVE_DOWN():
        __main__.player.move(dx=0, dy=1)
    @staticmethod
    def MOVE_DOWN_RIGHT():
        __main__.player.move(dx=1, dy=1)
    @staticmethod
    def MOVE_LEFT():
        __main__.player.move(dx=-1, dy=0)
    @staticmethod
    def MOVE_RIGHT():
        __main__.player.move(dx=1, dy=0)
    @staticmethod
    def MOVE_UP_LEFT():
        __main__.player.move(dx=-1, dy=-1)
    @staticmethod
    def MOVE_UP():
        __main__.player.move(dx=0, dy=-1)
    @staticmethod
    def MOVE_UP_RIGHT():
        __main__.player.move(dx=1, dy=-1)

    def __init__(self, methodname, *args, **kwargs):
        self.method = None
        self.methodname = methodname
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        if self.method == None:
            print "debug: eval {}".format(self.methodname)
            self.method = eval(self.methodname)
        self.method(*self.args, **self.kwargs)
