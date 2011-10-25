

## we want to try and create
## a set of generic classes that facilitate easily
## reading to / writing to sockets
# something along the line of setting up pipelines

class SocketHandler(asyncore.dispatcher,Eventable):
    socket_types = {
        'tcp':(socket.AF_INET,socket.SOCK_STREAM),
        'udp':(socket.AF_INET,socket.SOCK_DGRAM)
    }

    def __init__(self, host_port, tcp=True, connect_out=False,
                       receive_callback=None, send_callback=None):

        self.host_port = host_port
        self.tcp = tcp
        self.connect_out = connect_out

        # callbacks if we have them
        self.receive_callback = receive_callback
        self.send_callback = send_callback

        # our out buffer
        self.out_data = ''

    def setup_connection(self):
        # create our socket
        self.create_socket(socket_types['tcp' if self.tcp else 'udp'])

        # do we want to listen or connect out?
        if self.connect_out:
            self.connect(self.host_port)
        else:
            self.bind(self.host_port)

    def handle_accept(self):
        conn, addr = self.accept()
        self.fire('accept')

    def handle_close(self):
        self.close()
        self.fire('close')

    def writable(self):
        # we'll always take more data
        return True

    def readable(self):
        # do we have anything to send ?
        return bool(len(self.data))

    def handle_write(self):
        # figure out what we are going to write
        read_len = min(self.blocksize,len(self.data))
        to_write = self.out_data[:read_len]

        # send it
        sent = self.send(to_write)
        self.out_data = self.out_data[sent:]

        # let everyone know what we sent
        self.fire('send',to_write)
        if self.send_callback:
            self.send_callback(to_write)

    def handle_read(self):
        # read in a block
        data = self.recv(self.blocksize)

        # let everyone know what we read
        self.fire('receive',data)
        if self.receive_callback:
            self.receive_callback(data)

    def push(self, d):
        self.out_data += d
