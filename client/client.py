import socket

from interface import ui


class Client:
    """Class for creating and managing connections"""

    def __init__(self, server_host: str, server_port: int, nickname: str) -> None:
        self.server_host = server_host
        self.server_port = server_port
        self.nick = nickname
        self.isActive = False
        self.BANNED_MSG = 'BANNED'
        self.CLOSE_MSG = 'CLOSE_CONNECTION'

    def __activityCheck(func):
        """Decorator for checking client activity before call other functions"""

        def wrapper(*args, **kwargs):

            if (func.__name__ != 'start') and (args[0].isActive == False):
                ui.show("Client is not working at the moment", style='warning')
            elif (func.__name__ == 'start') and args[0].isActive:
                ui.show("Client is already working", style='warning')
            else:
                func(*args, **kwargs)

        return wrapper

    @__activityCheck
    def start(self) -> None:
        """Create client socket and connect to the server"""

        # Сreate a client socket to communicate with the server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:  # Try to connect to the server and send first messages
            self.client_socket.connect((self.server_host, self.server_port))
            self.client_socket.send(self.nick.encode())
            print('\n')
            ui.show(
                f"Сlient successfully connected to the server on {self.server_host}:{self.server_port}")

            # Start message receiving loop
            self.isActive = True
            self.__receive()

        except ConnectionRefusedError:
            print('\n')
            ui.show("Server is not working at the moment", style='warning')

    @__activityCheck
    def stop(self) -> None:
        """Close client socket"""

        self.isActive = False
        self.client_socket.close()
        print('\n')
        ui.show("Client was stopped")
        print('\n')

    @__activityCheck
    def send(self, message: str) -> None:
        """Send message to the server"""

        self.client_socket.send(message.encode())

    def __receive(self):
        """Recieve messages from the server"""

        # Receive messages from the server while the connection is established
        while self.isActive:
            try:
                message = self.client_socket.recv(1024).decode()

                # Message processing
                match message:
                    case self.BANNED_MSG:
                        unban_date = self.client_socket.recv(1024).decode()
                        self.stop()
                        ui.show(
                            f"You was ban by admin until {unban_date}", style='ban')
                    case self.CLOSE_MSG:
                        self.stop()
                        ui.show("Server was stopped or break connection")
                    case _:
                        sender = message[:message.index(':')]
                        msg = ' '.join(message.split()[1:])

                        if sender == 'admin':
                            ui.show(msg, sender=sender, style=sender)
                        else:
                            ui.show(msg, sender=sender, style='user')

            except ConnectionResetError:  # Raise when client socket is closed by server
                ui.show("Server was stopped or break connection")
            except ConnectionAbortedError:  # Raise when client socket is closed by client
                pass
