import socket
from threading import Thread
import time

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}

    def start(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"Server listening on {self.host}:{self.port}")

        while True:
            client, address = self.server.accept()
            
            print(f"Connected with {address}")

            message = client.recv(1024).decode()
            role, name = message.split(':', 1)

             
             

            client.send((str(self.clients).encode()))
            
            destination = message.decode()

            Thread(target=self.handle_client, args=(client,)).start()

    def handle_role(self, client):
        return None
    
    def handle_destination(self, client):
        return None
    
    def handle_client(self, client):
        self.handle_destination(client)
        while True:
            streamData = client.recv(1024)
            if not streamData:
                break
            print(f"Received Data from: {client}, the data: {streamData}")
        client.close()
        # del self.clients[]

    
    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            client = self.clients[client_id]
            client.send(message.encode())

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.start()