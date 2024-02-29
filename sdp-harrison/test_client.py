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

    def connect(self):
        # self.name = input("What should the server call this device? ")
        self.client.connect((self.host, self.port))
        print(f"Connected to the server {self.host}:{self.port}")
        # choice = self.handle_mode()
        # self.client.send(f"{choice}:{self.name}".encode())

        # while self.listen or self.client:


        #     if self.listen:
        #         Thread(target=self.listen_to_server).start()
        #     if self.send:       
        #         clientList = self.client.recv(1024).decode()
        #         print(f"Available Clients {clientList}")
        #         destination = input("From the available clients which client will you like to send your data to? ")
        #         self.client.send(destination.encode())
        #         pause = input("ready to send? ")
        #         self.send_data_stream()

    def listen_to_server(self):
        # while True:
        #     data = self.client.recv(1024).decode()
        #     if not data:
        #         break
        #     print(f"Received from (Client): {data}")
        data = self.client.recv(10).decode()
        self.client.send('confirmation'.encode())
        return data

    def handle_mode(self):
        choice = input("Will this device s for send, l for listen, or b for both? ")
        if choice == 's' or choice == 'b':
            self.send = True
        elif choice == 'l' or choice == 'b':
            self.listen = True
        
        return choice
    
    def send_data_stream(self, data):
        # for i in range(1000):
        #     data = f"test packet {i}"
        #     self.client.sendall(data.encode())
        #     time.sleep(0.0005)

        # self.client.close()
        print(data)
        if data == '':
            self.client.send('1'.encode())
        else:
            self.client.send(data.encode())
        self.client.recv(1024)


if __name__ == "__main__":
    client = Client('127.0.0.1', 12345)
    client.connect()