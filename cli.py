from testClient import Client

if __name__ == "__main__":
    client = Client('localhost', 12345)
    client.connect('name', 'l')