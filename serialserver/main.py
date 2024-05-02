import serial
from threading import Thread
import time

class SerialServer:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = serial.Serial(port, baudrate, timeout=1)
        self.clients = {}  

    def start(self):
        print(f"Serial server started on {self.port} with baudrate {self.baudrate}")
        try:
            Thread(target=self.listen_serial).start()
        except KeyboardInterrupt:
            print("Shutting down server")
            self.shutdown()

    def listen_serial(self):
        while True:
            if self.serial_conn.in_waiting:
                message = self.serial_conn.readline().decode().strip()

                print(f"Received message: {message}")

    def shutdown(self):
        self.serial_conn.close()
        print("Serial connection closed")

if __name__ == "__main__":
    serial_server = SerialServer('/dev/ttyUSB0', 9600)  # Example port and baudrate
    serial_server.start()
