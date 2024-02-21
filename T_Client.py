import socket
import mysql.connector
import getpass
import time 
BUFFER = 150
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
with open('output_msg.txt', 'w') as f:
    f.write(full_msg)



print(full_msg)#decoding the byte object into a readable message 


password = getpass.getpass("Enter password:")
db_connection = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = password,
    database = 'test_beltdb'
)
C_cursor = db_connection.cursor()
with open('output_msg.txt', 'r') as file:
    file.readline()
    for line in file:
        line_split = line.strip('\n').split(' ')
        print(line_split)
        query = "INSERT INTO freq VALUES(%s, %s) ;"
        val1 = int(line_split[2].strip(','))
        val2 = int(line_split[5])
        vals = (val1, val2)
        C_cursor.execute(query, vals)
    db_connection.commit()