from lib.socket_handlers import SocketHandler
from lib.requests import StoreRequest, StoreRequest
from lib.loopable import Loopable
from base_server import BaseServer

## we need to save the stream down, we are going to save down streams in
## one hour chunks

# the dir / file structure is going to relate when / from whom the data
# came in.

# the dir structure is going to be (from storage root)
# /YEAR/MONTH/DAY/STREAMID/HOUR/MINUTE
# where each of those values is as long as it can be (2011 not 11)
# and the file of the name is MINUTE. hours will be in 24hr format
# /2011/11/02/1230421/07/22 <-- rel path from storage root

class StoreServer(BaseServer):
    """
    answers requests for storage, stores down the stream
    """

    def make_work_request(self):
        """
        try and find some storage work
        """
        request = StoreRequest()
        self.bb_client.read_wait(request, self.handle_request)

    def handle_request(self, t):
        """
        someone wants some storage!
        """

        # respect ur elders
        super(StoreServer,self).handle_request(t)

        # convert out tuple to a request
        request = StoreRequest(t)

        # come up w/ a response for them
        response = StoreResponse(key=request.key,
                                 url=self.get_url(),
                                 port=self.get_port())

        # now spin up a handler for that port
        handler = StoreHandler(self,(response.url,response.port))

        # send back our response
        self.bb_client.put(response)


class StoreHandler(object):
    """
    listens on given port storing the data down as it comes in
    """

    def __init__(self, server, stream_id, host_port):

        # the save path is our path to a disk
        self.save_path = None
        # the open file handler for the save path
        self.save_fh = None
        self.host_port = host_port
        self.stream_id = stream_id

        # figure out where we are saving this stream
        self.setup_save_point()

        # setup a stream handler for the data coming in
        self.in_handler = SocketHandler(self.host_port)

        # whenever the in handler gets data we want to handle it
        self.in_handler.on('receive',self.handle_data)

        # when the stream closes we want to close our file handler
        self.in_handler.on('close',self.handle_stop)


    def setup_save_point(self):
        """
        sets up a file for us to write to
        """

        # figure out the rel path we should save down
        n = datetime.datetime.now()
        r_path = os.sep.join([n.year,n.month,n.day, self.stream_id,
                              n.hour,n.minute])

        # get our full path
        save_root = self.server.config.get('stream_save_root')
        out_path = os.path.join(save_root,r_path)

        # setup the file handler
        self.setup_file_handler()

        # keep it around
        self.save_path = out_path

    def setup_file_handler(self):
        # we should already know where we are saving out to
        # just setup an appending file handler for there

        fh = open(self.save_path,'ab')

    def handle_data(self, d):
        """
        receives chunks of the data, appends it to the file
        """

        # write the data to our file handler
        self.save_fh.write(d)

    def handle_stop(self):
        """
        closes the save file handler
        """
        if self.save_fh:
            self.save_fh.close()
