import argparse
import socket
import threading


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))

    def listen(self):
        self.sock.listen(5)
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listen_client, args=(client, address)).start()

    def listen_client(self, client, address):
        size = 1024
        while True:
            try:
                data = client.recv(size)
                if data:
                    # Set the response to echo back the received data
                    response = data
                    client.send(response)
                    print("Data: ", data)
                    print("Address: ", address)
                    client.close()
                    return True
                else:
                    raise socket.error('Client disconnected')
            except Exception as e:
                print(e)
                client.close()
                return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port to run the socket server on')
    args = parser.parse_args()
    ThreadedServer('', args.port).listen()
