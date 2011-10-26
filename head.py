import sys, os.path
import lib.loopable as loopable
import asyncore

# this guy manages the servers
class Head(object):
    """ head of the beast """
    def __init__(self,config):
        self.config = config
        self.servers = []
        self.bb_client = None

        # setup the blackboard client
        self.setup_bb_client()


    def loop(self,count=None):
        if count:
            for i in xrange(count):
                self._loop()
        else:
            while True:
                self._loop()

    def _loop(self):
        # loop asyncore
        asyncore.loop(count=1)

        # loop loopable
        loopable.Loopable.loop(count=1)

    def setup_bb_client(self):
        pass

    def start_servers(self):
        """ starting is initializing """

        # go through the servers, starting them
        for cls in self.find_servers():

            # check and see if it's one which is active
            server_config = self.config.get(cls.__name__)
            if server_config and server_config.get('active') == 'True':
                # passes the test, start'r up
                server_instance = cls(server_config,self.bb_client)
                self.servers.append(server_instance)

    def find_servers(self):
        """ finds server objs in the servers dir """

        # find the modules in the servers dir
        module_names = [ os.path.basename(f)[:-3] for f in
                         glob.glob(os.path.dirname(__file__)+"/servers/*.py") ]

        # import the modules
        modules = [__import__('servers.%s'%m) for m in module_names]

        # find the server objects
        server_classes = []
        for module in modules:
            for attr in dir(module):
                o = getattr(module,attr)
                if issubclass(o,BaseServer):
                    server_classes.append(o)

        return server_classes

    def stop_servers(self):
        for server in self.servers:
            server.close()


