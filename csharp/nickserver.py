class ClientInformation:
    def __init__(self):
        self.sending = False
        self.listening = []

    def set_sending_mode(self, mode):
        self.sending = mode
    
    def add_listener(self, listener_name):
        self.listening.append(listener_name)

class Server:
    def __init__(self):
        self.tcp_socket = None
        self.udp_socket = None
        self.host = None
        self.port = None
        # {name: client information}
        self.clients = {}

    def start(self, host, port):
        # Starts both sockets for listening
        id = 0
        while True:
            # Receive client connection
            
            self.clients += ClientInformation(id, 'sample_name')
            id += 1

            #if UDP
            # Start UDP Thread
            #if TCP
            # Start TCP Thread
        return

    def UDPConnectThread(self):
        # UDP Thread
        return

    def TCPConnectThread(self):
        # TCP Thread
        return