import socket
BUFFER = 100
""" Sockets programing are connections that send data between 2 points or more on a network.
A sockect itself is just a node on a network that is associated with a port or IP """

client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # our socket object
client_soc.connect((socket.gethostname(), 1234)) #instead of binding, we connect to the other socket
                                                #for a remote or local network device, we would use a dif name

full_msg = ''
while True: #while is active as long there is a socket to connect to, 
    msg = client_soc.recv(BUFFER) # data received from the connected socket 
                            # there is a bufsize (in bytes), which is the max amount of data that is sent at time
    if len(msg) <= 0:
        break
    print(f"Received message chunk: {msg}\n")
    full_msg += msg.decode('utf-8') #combines the 8 byte messages into the s
print(full_msg)#decoding the byte object into a readable message 