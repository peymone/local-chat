from sys import argv
import socket


class Server:
    """Class for creating and managing connections"""

    def __init__(self, port: int) -> None:
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.isActive = False
        self.clients = dict()
        self.CLOSE_MSG = 'CLOSE_CONNECTION'

    def start(self):
        """Create a server socket and accept connections"""

        self.isActive = True

        # Create a server socket and enable listen mode - IPv4, TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        # Accept connections from clients while server is working
        while self.isActive:
            try:
                client_socket, client_address = self.server_socket.accept()  # IO Blocking
                nickname = client_socket.recv(1024).decode()
                self.clients[nickname] = (client_socket, client_address)

            except OSError:  # Raise when server is stopped but still accepting connections
                pass

    def stop(self) -> None:
        """Close active connections and server socket"""

        self.isActive = False  # Stop accepting connections

        # Close active connections
        for client_data in self.clients.values():
            client_data[0].send(self.CLOSE_MSG.encode())  # Send close message
            client_data[0].close()  # Close client socket

        self.clients = dict()  # Clear clients data
        self.server_socket.close()  # Close server socket


if __name__ == '__main__':

    # Set server port manually or use 6061 by default
    if len(argv) > 1:
        server = Server(port=int(argv[1]))
    else:
        server = Server(port=6061)
