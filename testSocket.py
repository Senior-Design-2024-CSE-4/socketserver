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

        try:
            while True:
                client, address = self.server.accept()
                
                print(f"Connected with {address}")

                message = client.recv(1024).decode()
                role, name = message.split(':', 1)

                self.clients[name] = (role, client)

                if role == "l":
                    continue

                client.send((str(self.clients.keys()).encode()))
                
                choice = client.recv(1024).decode()
                print(self.clients, choice)
                destination = self.clients[choice][1]

                Thread(target=self.handle_client, args=(client,role,destination,)).start()
        except KeyboardInterrupt:
            print("Shutting down server")
            self.close_all_clients()
            self.shutdown()

    def close_all_clients(self):
        for name, (role, client) in self.clients.items():
                client.close()
                print(f"Closed {name}")

    def shutdown(self):
        self.server.close()

    def handle_role(self, client, role, name):
        #self.clients[name] = (role, client)
        return None
    
    def handle_destination(self, client):
        return None
    
    def handle_client(self, client, role, destination):

        while True:
            streamData = client.recv(1024)
            destination.sendall(streamData)
            if not streamData:
                break
            #print(f"Received Data from: {client}, the data: {streamData}")

    def listen_client(self, client):
        while True:
            streamData = client.recv(1024)
            if not streamData:
                break
            print(f"Received Data from: {client}, the data: {streamData}")

    
    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            client = self.clients[client_id]
            client.send(message.encode())

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.start()