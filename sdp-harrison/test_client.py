import socket
import time
from threading import Thread

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen = False
        self.send = False
        self.data=''
        self.send_data = ''

    def connect(self, name='', choice='', destination=''):
        # self.name = input("What should the server call this device? ")
        try:
            self.client.connect((self.host, self.port))
        except Exception as e:
            raise(e)
        # put the name of the device in quotes
        self.name = name
        # set mode in the device
        # s = send, l = listen, b = both
        mode = choice
        
        print(f"Connected to the server {self.host}:{self.port}")

        self.handle_mode(mode)

        self.client.send(f"{mode}:{self.name}".encode())
        self.client.recv(1024)


        if self.listen:
            print('ready to listen')
            
        if self.send:     
            # put the name of the device you want to send data to  
            self.client.send(destination.encode())
            self.client.recv(1024)
            print('received confirmation')

    def listen_to_server(self):
        data = self.client.recv(10).decode()
        self.client.send('confirmation'.encode())
        return data

    def handle_mode(self, choice):
        if choice == 's' or choice == 'b':
            self.send = True
        elif choice == 'l' or choice == 'b':
            self.listen = True
        
        return choice
    
    def send_data_stream(self, data=None):
        data = data
        if data == '':
            self.client.send('1'.encode())
        else:
            self.client.send(data.encode())
        self.client.recv(1024)


if __name__ == "__main__":
    client = Client('127.0.0.1', 12345)
    client.connect()