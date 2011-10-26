
import servers


class Head(object):
    """ head of the beast """
    def __init__(self,config):
        self.config = config
        self.servers = []
        self.bb_client = None

        self.setup_bb_client()

    def setup_bb_client(self):
        pass

    def start_servers(self):
        # find all the server classes
        for attr in dir(servers):
            o = getattr(servers,attr)
            if issubclass(o,servers.ServerBase):
                # check and see if it's one which is active
                server_config = self.config.get(attr)
                if server_config and server_config.get('active') == 'True':
                    # passes the test, start'r up
                    server_instance = o(server_config,self.bb_client)
                    self.servers.append(server_instance)

    def stop_servers(self):
        for server in self.servers:
            server.close()


