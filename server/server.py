from threading import Thread
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

    def status(self) -> None:
        """Show current server status"""

        if self.isActive:
            print(f"Server is already working on port {self.port}")
        else:
            print("Server is not working at the moment")

    def start(self) -> None:
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

                # Start receiving messages from client
                receive_thread = Thread(
                    target=self.receive, args=(client_socket, nickname))
                receive_thread.start()

            except OSError:  # Raise when server is stopped but still accepting connections
                pass

    def stop(self) -> None:
        """Close active connections and server socket"""

        self.isActive = False  # Stop accepting connections

        # Close active connections
        if len(self.clients) > 0:
            for client_data in self.clients.values():
                client_data[0].send(self.CLOSE_MSG.encode())
                client_data[0].close()  # Close client socket

            self.clients = dict()  # Clear clients data

        self.server_socket.close()  # Close server socket

    def receive(self, socket, nickname: str) -> None:
        """Processing messages from the client"""

        while nickname in self.clients:
            try:
                message = socket.recv(1024).decode()

                if message == self.CLOSE_MSG:  # Close connection if CLOSE_MSG received
                    pass
                else:  # Show message and broadcat to other clients
                    print(f"{nickname}: {message}")

            except ConnectionAbortedError:  # Raise when server is stopped but still receiving messages
                pass


if __name__ == '__main__':

    # Set server port manually or use 6061 by default
    if len(argv) > 1:
        server = Server(port=int(argv[1]))
    else:
        server = Server(port=6061)
