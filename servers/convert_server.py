from lib.socket_handlers import SocketHandler
from lib.requests import RawRequest, RawResponse, \
                         ConvertRequest, ConvertResponse
from lib.loopable import Loopable
from base_server import BaseServer

class ConvertServer(BaseServer):
    """
    waits for requests for convert servers
    passes converted stream to storage server
    """

    def __init__(self,config,bb_client):
        self.bb_client = bb_client

    def handle_request(self, t):
        # it should be a convert request
        request = ConvertRequest(t)

        # now that we have a request for conversion we need to find storage
        self.find_storage(request)

    def find_storage(self, convert_request):
        # put out a request for storage
        storage_request = StorageRequest(key=key())

        self.bb_client.put(storage_request,
                           partial(self.hook_up_streams,convert_request))

    def hook_up_streams(self, convert_request, storage_response):
        storage_response = StorageConvert(storage_response)

        # put our response back for conversion
        convert_response = ConvertResponse(key=convert_request.key,
                                           url=self.get_url(),
                                           port=self.get_port())


        # create a handler for the conversion
        handler = ConversionHandler(self, convert_request.vformat,
                               ( convert_response.url, convert_response.port ),
                               ( storage_response.url, storage_response.port ))

        # send back our response
        self.bb_client.put(convert_response)


class ConversionHandler(object):
    def __init__(self, server, vformat, in_host_port, out_host_port):

        self.in_host_port = in_host_port
        self.out_host_port = out_host_port
        self.vformat = vformat

        # setup our stream handlers
        self.in_handler = SocketHandler(in_host_port)
        self.out_handler = SocketHandler(out_host_port)

        # create a process for handling the conversion
        self.converter = VideoConverter(vformat)

        # data comes in, gets converted, and goes out
        self.in_handler.on('receive', self.converter.write)
        self.converter.on('read', self.out_handler.push)


class VideoConverter(object, Eventable, Loopable):
    self.blocksize = 1024

    def __init__(self, in_vformat):
        Eventable.__init__(self)
        Loopable.__init__(self)

        # store down our format
        self.in_vformat = in_vformat

        # setup a process to help us
        self.process = None
        self.setup_processes()

    def get_convert_command(self):
        return []

    def setup_process(self):
        self.process = Popen(get_convert_command(),
                             stdin=PIPE, stdout=PIPE)

    def write(self, data):
        self.process.stdin.write(data)
        self.fire('write',data)

    def loop(self):
        self.try_read()

    def try_read(self):
        # check for more data from our process
        data = self.process.stdout.read(self.blocksize)
        self.fire('read',data)

