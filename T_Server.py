import socket
import decimal
import random
from Dum_freq import gen_freq_rInt
server_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # our socket object
server_soc.bind((socket.gethostname(), 1234)) #tuple of an IP and a port. .bind() ties a name to a socket
                                              #socket.gethostname() fetches the name of machine hosting the server, in this local host

server_soc.listen(5)#a queue of unaccepted connections that system allows before refusing new connections.
try: 
    while True: #loop that keeps the listen command constantly on and allows for any avaible connection to link
        clientsocket, address = server_soc.accept() #gets info of the client socket and ip address of client 
        print(f'\nconnnection from {address} has been establsished.\n')
        val_gen = gen_freq_rInt(50) 
        clientsocket.sendall(bytes('Welcome to the server!\n', "utf-8")) #send the info to the client socket in form of utf-8 bytes
        for i in range(len(val_gen)):
            clientsocket.send(bytes(f'Freq (HZ): {val_gen[i][0]}, random value: {val_gen[i][0]:}\n', "utf-8"))        
        clientsocket.close()#once the data stream is fully done, close the client server
except Exception as e:
    print(f"Error sending data: {e}")