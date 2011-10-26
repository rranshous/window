import weakref

class Loopable(object):
    instances = []
    def __init__(self):
        print 'adding instance'
        self.instances.append(weakref.ref(self))

    @classmethod
    def loop_all(cls,count=None):
        """ loop forever if no count """
        print 'looping all'
        if count:
            for i in xrange(count):
                cls._loop_all()
        else:
            while True:
                cls._loop_all()

    @classmethod
    def _loop_all(cls):
        for inst_ref in cls.instances:
            instance = inst_ref()
            if instance is not None:
                instance.loop()
            else:
                cls.instances.remove(inst_ref)

    # child should over ride this and do their loop work
    def loop(self):
        """ one loop, child class should override """
        pass

class TestLoopable(Loopable):
    def loop(self):
        print 'loop'
