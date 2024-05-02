#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
count = 1

while True:
    #  Wait for next request from client
    message = socket.recv()
    if count == 1:
        start = time.time()
    # print(f"{message}\r", end="", flush=True)
    count += 1
    tims = time.time() - start + 0.00000001
    print(f"{round(count/(tims), 8)}, {count}, {tims}\r", end='', flush=True)

    socket.send(b"1")
