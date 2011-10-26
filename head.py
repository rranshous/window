import sys, os.path
import lib.loopable as loopable
import asyncore
import servers

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
        # go through each attr on servers module
        for attr in dir(servers):
            cls_name = attr
            # check and see if it's one which is active
            server_config = self.config.get(cls_name)
            if server_config and server_config.get('active') == 'True':
                cls = getattr(servers,cls_name)
                # passes the test, start'r up
                server_instance = cls(server_config,self.bb_client)
                self.servers.append(server_instance)

    def stop_servers(self):
        for server in self.servers:
            server.close()


