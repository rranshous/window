from socket_handlers import SocketHandler
from requests import RawRequest, RawResponse, ConvertRequest, ConvertResponse

class UDPRawInputServer(object):
    """
    Server connects to to blackboard listening for requests:
      (key,'request','upd_raw_in', video_format)
        request for a url + port to stream raw video of given format to

    We in turn make a request for a conversion server to normalize
    the video
      (key,'request','tcp_convert_raw', source_video_format)
      we'll get a url + port, we than open a tcp connection and relay
    """

    def __init__(self,blackboard_host_port):
        # connect to the blackboard
        self.setup_bb_client(blackboard_host_port)

    def setup_bb_client(self,host_port):
        self.bb_client = BBClient(host_port)


        # put out our request listener on the board
        self.bb_client.get(RawRequest(), self.handle_request)

    def handle_request(self,t):
        # we have the request tuple
        request = RawRequest(t)

        # we need to find a converter which can take it
        self.find_converter(request)

    def find_converter(self,raw_request):
        # put out a request for a converter
        convert_request = ConvertRequest(key=key(),
                                         vformat=raw_request.vformat)

        self.bb_client.put(convert_request,
                           partial(self.hook_up_streams,raw_request))

    def hook_up_streams(self,raw_request,convert_response):
        convert_response = ConvertResponse(convert_response)

        # figure out what our response is going to be
        raw_response = RawResponse(key=raw_request.key,
                                   url=self.get_url(),
                                   port=self.get_free_port())


        # use the details we now have to setup the handler
        handler = RawVideoHandler(self,
                              ( raw_response.url, raw_response.port ),
                              ( convert_response.url, convert_response.port ))

        # and we're done

    def get_free_port(self):
        # return back an unused udp port
        pass

    def handle_udp_close(self,port):
        # one of the udp ports has been freed
        pass

    def get_url(self):
        # return back this hosts's url
        pass


class RawVideoHandler():
    """
    relays a udp stream to a tcp stream
    """

    def __init__(self,server,udp_host_port,target_host_port):

        # setup a handler to read in the udp
        self.udp_in_handler = SocketHandler(self.udp_host_port, tcp=False)

        # setup a handler to write out the tcp
        self.tcp_out_handler = SocketHandler(self.target_host_port,
                                             connect_out=True)

        # relay the udp data coming in to the tcp going out
        self.udp_in_handler.on('receive',self.tcp_out_handler.write)

        # when one closes, close the other
        self.tcp_out_handler.on('close',self.udp_in_handler.close)
        self.udp_in_handler.on('close',self.tcp_out_handler.close)

        # when the udp port closes release it as available
        self.udp_in_handler.on('close',
                               partial(server.handle_udp_close,
                                       udp_host_port[1]))
