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
        # do we wanna loop a few times?
        if count:
            for i in xrange(count):
                cls._loop_all()

        # or all the time?
        else:
            while True:
                cls._loop_all()

    @classmethod
    def _loop_all(cls):
        to_remove = []
        # go through all the instances
        for inst_ref in cls.instances:
            instance = inst_ref()
            # if the ref is to something which still exists
            # call it's loop
            if instance is not None:
                instance.loop()
            else:
                # if it doesnt exist mark it for removal
                to_remove.append(inst_ref)

        # get rid of dead refs
        for inst_ref in to_remove:
            cls.instances.remove(inst_ref)

    # child should over ride this and do their loop work
    def loop(self):
        """ one loop, child class should override """
        pass

class TestLoopable(Loopable):
    def loop(self):
        print 'loop'
