import socket
import time
from threading import Thread

class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listen = False
        self.send = False

    def connect(self, name='', choice=''):
        self.client.connect((self.host, self.port))
        self.client.connect((self.host, self.port))
        # put the name of the device in quotes
        self.name = 'name'
        # set mode in the device
        # s = send, l = listen, b = both
        mode = 'l'
        
        print(f"Connected to the server {self.host}:{self.port}")

        self.client.send(f"{mode}:{self.name}".encode())
        print(1)
        while self.listen or self.client:


            if self.listen:
                # Thread(target=self.listen_to_server).start()
                self.listen_to_server()
            if self.send:     
                # put the name of the device you want to send data to  
                destination = ""
                self.client.send(destination.encode())

    def listen_to_server(self):
        while True:
            data = self.client.recv(1024).decode()
            if not data:
                break
            print(f"Received from (Client): {data}")

    def handle_mode(self):
        choice = input("Will this device s for send, l for listen, or b for both? ")
        if choice == 's' or choice == 'b':
            self.send = True
        elif choice == 'l' or choice == 'b':
            self.listen = True
        
        return choice
    
    def send_data_stream(self):
        for i in range(1000):
            data = f"test packet {i}"
            self.client.sendall(data.encode())
            time.sleep(0.0005)

        self.client.close()

if __name__ == "__main__":
    client = Client('127.0.0.1', 12345)
    client.connect()