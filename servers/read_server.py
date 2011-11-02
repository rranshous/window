from lib.socket_handlers import SocketHandler
from lib.requests import ReadRequest, ReadResponse
from lib.loopable import Loopable
from base_server import BaseServer


# we are going to be reading data back from it's storage spot
# and streaming it @ someone else


class ReadServer(BaseServer):

    def make_work_request(self):
        request = ReadRequest()
        self.bb_client.read_wait(request, self.handle_request)

    def handle_request(self, t):
        super(ReadServer,self).handle_request(t)

        request = ReadRequest(t)
        response = ReadResponse(key=request.key,
                                url=self.get_url(),
                                port=self.get_port())

        handler = ReadHandler(self, stream_id, request.offset,
                              (response.url,response.port))


class ReadHandler(object):
    chunk_size = 1024

    def __init__(self, server, stream_id, offset, host_port):
        # abs path to file to be read
        self.read_path = None
        self.server = server
        self.stream_id = stream_id
        self.host_port = host_port

        # number of seconds in the past we should read from the stream
        self.offset = offset

        # we need to find the correct file to read from
        self.setup_read_point()

        # now we need to setup a read handler from that file
        # at the given offset
        self.setup_file_handler()

        # now setup our socket handler to listen on given host / port
        self.out_handler = SocketHandler(self.host_port)

        # whenever data is sent from the socket we want to
        # send more
        self.out_handler.on('send', self.handle_send)

        # prime the socket with some data
        self.send_data(self.chunk_size)

    def setup_read_point(self):
        # figure out the date/tim ewe're reading from
        epoch = time.time() - self.offset
        s = datetime.fromtimestamp(epoch)
        # get it's rel path
        r_path = os.sep.join([s.year,s.month,s.day, self.stream_id,
                              s.hour,s.minute])
        # where's it actually saved?
        save_root = self.server.config.get('stream_save_root')
        path = os.path.join(save_root,r_path)
        self.read_path = path

    def setup_file_handler(self):
        # open a file handler to the file
        self.read_fh = open(self.read_path,'rb')

        # now seek to the offset we want


    def handle_send(self, d):
        # we want there to always be data waiting to go out
        # so when we send some, read in the next chunk and
        # send it to the socket to go out
        data_len = len(d)
        self.send_data(data_len)

    def send_data(self, l):
        # we want ot send the next chunk of data of len l
        data = self.fh.read(l)
        self.out_fh.push(data)


def find_video(storage_root,stream_id,dt):
    """
    returns the abs path to the video file at the given
    date time for the given stream off the given storage root
    if the file is not found returns none
    """

    # start by finding the hour we want
    r_hr_path = os.sep.join([dt.year,dt.month,dt.day,stream_id,s.hour])
    hr_path = os.path.abspath(storage_root,r_hr_path)
    if not os.path.exists(hr_path):
        return None

    # now that we know the folder for the hour exists, lets see if we can
    # find the video file for the exact time we want
    # to estimate
