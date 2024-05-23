from sys import argv
import socket


class Server:
    """Class for creating and managing connections"""

    def __init__(self, port: int) -> None:
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.isActive = False

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
            except OSError:  # Raise when server is stopped but still accepting connections
                pass

    def stop(self):
        """Close active connections and server socket"""

        self.isActive = False
        self.server_socket.close()


if __name__ == '__main__':

    # Set server port manually or use 6061 by default
    if len(argv) > 1:
        server = Server(port=int(argv[1]))
    else:
        server = Server(port=6061)
