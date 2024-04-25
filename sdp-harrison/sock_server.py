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
                client.send('confirmation'.encode())
                role, name = message.split(':', 1)

                self.clients[name] = (role, client)

                print(role, name)

                if role == "l":
                    continue
                choice = client.recv(1024).decode()
                client.send('confirmation'.encode())
                
                destination = self.clients[choice][1]

                Thread(target=self.handle_client, args=(client,destination,)).start()

        except KeyboardInterrupt:
            print("Shutting down server")
            self.close_all_clients()
            self.shutdown()

    def handle_client(self, client, destination):
        while True:
            streamData = client.recv(128).decode()
            client.send(b'1')
            print(streamData)
            destination.send(streamData.encode())
            destination.recv(128).decode()

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.start()