from datetime import datetime, timedelta
from threading import Thread
import socket


class Server:
    """Class for creating and managing connections"""

    def __init__(self, port: int) -> None:
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.isActive = False
        self.clients = dict()
        self.banned = dict()
        self.tFormat = "%d.%m.%Y %H:%M:%S"
        self.CLOSE_MSG = 'CLOSE_CONNECTION'
        self.BANNED_MSG = 'BANNED'

        # Fill dictionary with current banned clients
        self.__checkBan_txt()

    def checkServer_isWorking(func):
        def wrapper(*args, **kwargs):
            if args[0].isActive:
                func(*args, **kwargs)
            else:
                print("Server is not working at the moment")
        return wrapper

    def checkServer_isNotWorking(func):
        def wrapper(*args, **kwargs):
            if args[0].isActive:
                print(f"Server is already working on port {args[0].port}")
            else:
                func(*args, **kwargs)
        return wrapper

    def status(self) -> None:
        """Show current server status"""

        if self.isActive:
            print(f"Server is working on port {self.port}")
        else:
            print("Server is not working at the moment")

    @checkServer_isNotWorking
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
                # Accept client connection and receive first message
                cSocket, cAddress = self.server_socket.accept()  # IO Blocking
                ip, port = cAddress[0], cAddress[1]
                nick = cSocket.recv(1024).decode()

                # Check if client was banned
                if self.__isBanned(ip):
                    cSocket.close()
                else:
                    # Save client data and start receiving messages
                    self.clients[nick] = cSocket, ip, port
                    Thread(target=self.__receive, args=(cSocket, nick)).start()

            except OSError:  # Raise when server is stopped but still accepting connections
                pass

    @checkServer_isWorking
    def stop(self) -> None:
        """Close active connections and server socket"""

        self.isActive = False  # Stop accepting connections

        # Close active connections
        if len(self.clients) > 0:
            for nickname in self.clients:
                self.close_connection(nickname, self.CLOSE_MSG)

        # Fill txt with currently banned clients and close server socket
        self.__createBan_txt()
        self.server_socket.close()
        print("Server was stopped")

    def __receive(self, cSocket: socket.socket, nickname: str) -> None:
        """Processing messages from the client"""

        client_ip = self.clients[nickname][1]

        # Receive messages from client while server client is not disconnected or banned
        while nickname in self.clients and self.__isBanned(client_ip) != True:
            try:
                message = cSocket.recv(1024).decode()

                if message == self.CLOSE_MSG:
                    self.close_connection(nickname)
                else:
                    self.broadcast(message, nickname)
                    print(f"{nickname}: {message}")

            except ConnectionAbortedError:  # Raise when server is stopped but still receiving messages
                pass

    @checkServer_isWorking
    def send(self, nickname: str, message: str, sender: str = 'admin') -> None:
        """Send message to a specific client"""

        if nickname in self.clients:
            client_socket = self.clients[nickname][0]
            client_socket.send(f"{sender}: {message}".encode())
        else:
            print(f"Client with name {nickname} is not connected")

    @checkServer_isWorking
    def broadcast(self, message: str, sender: str = 'admin') -> None:
        """Send message to all connected clients"""

        for nickname in self.clients:
            if nickname == sender:
                continue
            else:
                self.send(nickname, message, sender)

    @checkServer_isWorking
    def close_connection(self, nickname: str, reason: str = None, unban: str = None) -> None:
        """Close a connection to a specific client"""

        if nickname in self.clients:
            client_socket: socket.socket = self.clients[nickname][0]

            match reason:
                case self.CLOSE_MSG:
                    client_socket.send(reason.encode())
                case self.BANNED_MSG:
                    client_socket.send(reason.encode())
                    client_socket.send(unban.encode())
                case _: pass

            client_socket.close()
            del self.clients[nickname]
            print(f"Client {nickname} was disconnected")

        else:
            print(f"Client with name {nickname} is not connected")

    @checkServer_isWorking
    def ban(self, nickname: str, duration: int = -1) -> None:
        """Ban a specific client for n minutes or forever"""

        client_ip: str = self.clients[nickname][1]

        # Set date to unban
        if duration == -1:
            unban_date = datetime.max
        else:
            unban_date = datetime.now() + timedelta(minutes=duration)

        unban_date_str = unban_date.strftime(self.tFormat)

        # Ban client by IP with nickname
        if nickname in self.clients:
            self.close_connection(nickname, self.BANNED_MSG, unban_date_str)
            self.banned[client_ip] = unban_date
            print(f"{nickname} was banned until {unban_date_str}")
        else:
            print(f"Client with name {nickname} is not connected")

    @checkServer_isWorking
    def unban(self, ip: str) -> None:
        """Unban a specific client by IP"""

        if self.__isBanned(ip):
            del self.banned[ip]
            print(f"Client with IP {ip} was unbanned")
        else:
            print(f"Client with IP {ip} is not banned")

    @checkServer_isWorking
    def unban_all(self) -> None:
        """Unban all clients"""

        self.banned = dict()
        print("All clients was seccesfully unbanned")

    @checkServer_isWorking
    def show_banned(self) -> None:
        """Show all banned clients at the moment"""

        if len(self.banned) == 0:
            print("Total banned clients is 0")
        else:
            for ip, uban_date in self.banned.copy().items():
                if self.__isBanned(ip):
                    print(f"{ip} banned until {uban_date.strftime(self.tFormat)}")
                else:
                    del self.banned[ip]

    def __isBanned(self, ip: str) -> bool:
        """Check if user with specified IP have ban"""

        if ip in self.banned:
            if datetime.now() > self.banned[ip]:
                return False
            else:
                return True
        else:
            return False

    def __checkBan_txt(self) -> dict:
        """Fill banned dictionary"""

        try:
            with open('banned.txt', 'r') as file:
                for line in file.readlines():
                    delimiter_index = line.strip().find(':')
                    ip: str = line.strip()[:delimiter_index]
                    unban: str = line.strip()[delimiter_index+1:]

                    self.banned[ip] = datetime.strptime(unban, self.tFormat)

        except FileNotFoundError:
            pass

    def __createBan_txt(self) -> None:
        """Create txt with currently banned clients"""

        if len(self.banned) == 0:
            with open('banned.txt', 'w'):
                pass
        else:
            with open('banned.txt', 'w') as file:
                for ip, unban in self.banned.items():
                    unban_date = unban.strftime(self.tFormat)
                    file.write(f"{ip}:{unban_date}\n")
