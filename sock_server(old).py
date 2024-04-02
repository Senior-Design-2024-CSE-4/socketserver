import socket
from threading import Thread
import time
import json
from pymongo import MongoClient


class Server:
    c_connect = MongoClient('mongodb://localhost:27017/')
    db = c_connect['naviBeltDB']
    global collection 
    collection = db['naviBelt_data']

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

                destination, dest_address = self.server.accept()

                print(f"Connected with {dest_address}")

                # message = client.recv(1024).decode()
                # role, name = message.split(':', 1)

                # self.clients[name] = (role, client)

                # if role == "l":
                #     continue

                # client.send((str(self.clients.keys()).encode()))
                
                # choice = client.recv(1024).decode()
                # print(self.clients, choice)
                # destination = self.clients[choice][1]

                # Thread(target=self.handle_client, args=(client,role,destination,)).start()

                # self.listen_client(client)
                # self.send_client(client)

                self.handle_client(client=client, destination=destination)

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
    
    # def handle_client(self, client, role, destination):

    #     while True:
    #         streamData = client.recv(1024)
    #         destination.sendall(streamData)
    #         if not streamData:
    #             break
    #         #print(f"Received Data from: {client}, the data: {streamData}")

    def handle_client(self, client, destination):
        # while True:
        #     streamData=client.recv(1024)
            
        #     if streamData is None:
        #         break
        #     print(streamData)
        #     destination.send(streamData)
        #     client.send('1'.encode())
        #     destination.recv(1024)
        with open("sample3.json", 'w') as fd:
            while True:
                
                streamData = client.recv(128).decode() # Receives data from the IMU
                seconds = time.time()
                Dictiornary = {"orientation":streamData, "Device": "IMU", "seconds": seconds}
               # print("about to send into MongoDB") 
                collection.insert_many([Dictiornary]) #Have to fix this line being inserted into the database
               # print("Sent to the DB")
            
                json_object = json.dumps(streamData, indent =4)
                fd.write(json_object)
                #print("Data streamed is" + streamData)
                client.send(b'1') #
                # if len(streamData) < 10:
                #     leng = len(streamData)
                #     zeros = 10-leng
                #     for i in range(zeros):
                #         streamData+='0'
                destination.send(streamData.encode())# Sends an enconded representation of the IMU signal
                destination.recv(128).decode()

    def listen_client(self, client):
        # start = time.time()
        # # count = 0
        # while True:
        streamData = client.recv(128).decode()
        # if not streamData:
        #     break
        # print(f"Received Data from: {client}, the data: {streamData}")
        # print(f"{streamData}\r", end="", flush=True)
            # count += 1
            # print(f"{round(count/(time.time()-start), 8)}, {count}, {time.time()-start}\r", end='', flush=True)
        client.send(b'1')
        return streamData


    def send_client(self, client, data):
        data = f"{1}"
        client.send(data.encode())
        client.recv(128).decode()

    def send_to_client(self, client_id, message):
        if client_id in self.clients:
            client = self.clients[client_id]
            client.send(message.encode())
    #def create_json(d):
     #   json_object = json.dumps(d, indent =4)
      #  outfile.write(json_object)

if __name__ == "__main__":
    server = Server('127.0.0.1', 12345)
    server.start()