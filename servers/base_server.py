
class BaseServer(object):
    def __init__(self, config, bb_client):
        self.config = config
        self.bb_client = bb_client
        self.make_work_requeset()

    def make_work_request(self):
        """
        puts a waiting read request in to the black board
        waiting for another process to need our help
        """
        pass

    def handle_request(self, t):
        """
        our work request got a hit! now we have to
        fulfill the request
        """
        self.make_work_request()


