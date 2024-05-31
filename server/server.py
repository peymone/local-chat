from datetime import datetime, timedelta
from threading import Thread
from time import sleep
import socket

from interface import ui
from logger import logger
from security import security


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

    def __activityCheck(func):
        def wrapper(*args, **kwargs):

            if (func.__name__ != 'start') and (args[0].isActive == False):
                ui.show("Server is not working at the moment", style='warning')
            elif (func.__name__ == 'start') and args[0].isActive:
                ui.show(f"Server is already working on port {args[0].port}", style='warning')
            else:
                func(*args, **kwargs)

        return wrapper

    def status(self) -> None:
        """Show current server status"""

        if self.isActive:
            ui.show(f"Server is working on port {self.port}")
        else:
            ui.show("Server is not working at the moment")

    @__activityCheck
    def start(self) -> None:
        """Create a server socket and accept connections"""

        logger.debug.debug("server_start thread - start")
        self.isActive = True

        # Create a server socket and enable listen mode - IPv4, TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        ui.show(f"Server was started on port {self.port}")
        logger.log.info(f"Server was started on port {self.port}")

        # Accept connections from clients while server is working
        while self.isActive:
            try:
                logger.debug.debug("accept connections loop - start")

                # Accept client connection and receive first message
                cSocket, cAddress = self.server_socket.accept()  # IO Blocking
                ip, port = cAddress[0], cAddress[1]

                # Public key exchange for encryption
                cSocket.send(security.getSerialized_publicKey())
                public_key = cSocket.recv(1024)

                # Receive first message and save client data
                nick = security.decrypt(cSocket.recv(1024))
                self.clients[nick] = cSocket, ip, port, public_key

                logger.debug.debug(f"connection accepted - {nick} {ip}:{port}")

                if self.__isBanned(ip):  # Check if client was banned
                    self.close_connection(nick, self.BANNED_MSG)
                else:  # Start receiving messages

                    ui.show(f"{nick} {ip}:{port} established connection with server")
                    logger.log.info(f"{nick} {ip}:{port} established connection with server")

                    Thread(target=self.__receive, args=(cSocket, nick)).start()

            except OSError:  # Raise when server is stopped but still accepting connections
                pass

        # Show it when loop is stopped
        ui.show("Server has been stopped")
        logger.log.info("Server has been stopped")
        logger.debug.debug("server_start thread - stop")

    @__activityCheck
    def stop(self) -> None:
        """Close active connections and server socket"""

        logger.debug.debug("stop method called")

        # Close active connections
        if len(self.clients) > 0:
            for nick in self.clients.copy():
                self.close_connection(nickname=nick, reason=self.CLOSE_MSG)

        # Fill txt with currently banned clients and close server socket
        self.isActive = False
        self.__createBan_txt()
        self.server_socket.close()

    def __receive(self, cSocket: socket.socket, nickname: str) -> None:
        """Processing messages from the client"""
        client_ip = self.clients[nickname][1]
        logger.debug.debug(f"receive thread - start |{nickname} {client_ip}|")

        # Receive messages from the client while the connection is established
        while nickname in self.clients and self.__isBanned(client_ip) != True:
            try:
                # Receive message and decrypt
                message = security.decrypt(cSocket.recv(1024))

                # Message processing
                if message == self.CLOSE_MSG:  # No need actually
                    logger.debug.debug(f"CLOSE_MSG received for {nickname}")
                    self.close_connection(nickname)
                else:
                    self.broadcast(message, nickname)
                    ui.show(message, nickname, 'user')
                    logger.log.info(f"{nickname}: {message}")
            except ConnectionAbortedError:  # Raise when client socket is closed by server
                pass
            except ConnectionResetError:  # Raise when client socket is closed by client
                self.close_connection(nickname)

        logger.debug.debug(f"receive thread - stop |{nickname} {client_ip}|")

    @__activityCheck
    def send(self, nickname: str, message: str, sender: str = 'admin') -> None:
        """Send message to a specific client"""

        if nickname in self.clients:
            client_socket = self.clients[nickname][0]
            public_key = self.clients[nickname][-1]

            # Encrypt and send message
            decrypted = security.encrypt(f"{sender}: {message}", public_key)
            client_socket.send(decrypted)

            logger.log.info(f"{sender}: {message}")
        else:
            ui.show(f"Client with name {nickname} is not connected")

    @__activityCheck
    def broadcast(self, message: str, sender: str = 'admin') -> None:
        """Send message to all connected clients"""

        if len(self.clients) == 0:
            ui.show("Server have no connected clients at the moment")
        else:
            for nickname in self.clients:
                if nickname == sender:
                    continue
                else:
                    self.send(nickname, message, sender)

    @__activityCheck
    def close_connection(self, nickname: str, reason: str = None) -> None:
        """Close a connection to a specific client"""

        if nickname in self.clients:
            client_socket: socket.socket = self.clients[nickname][0]
            ip: str = self.clients[nickname][1]
            public_key = self.clients[nickname][-1]

            logger.debug.debug(f"close connection |{nickname} - {reason}|")

            # Send reason message to client
            match reason:
                case self.CLOSE_MSG:  # Close connection by server
                    client_socket.send(security.encrypt(reason, public_key))

                case self.BANNED_MSG:  # Close connection when banned
                    unban_date = self.__getUnban_date(ip)
                    client_socket.send(security.encrypt(reason, public_key))
                    sleep(1)
                    client_socket.send(security.encrypt(unban_date, public_key))

                case _: pass

            # Close client socket and clear connected clients dict
            client_socket.close()
            del self.clients[nickname]

            logger.debug.debug(f"close connection - stop |{nickname}|")

            if reason == self.BANNED_MSG:
                ui.show(f"{nickname}: {ip} was banned until {unban_date} or tryed to connect")
                logger.log.info(f"{nickname}: {ip} was banned until {unban_date} or tryed to connect")
            else:
                ui.show(f"Client {nickname} was disconnected")
                logger.log.info(f"Client {nickname} was disconnected")
        else:
            ui.show(f"Client with name {nickname} is not connected")

    @__activityCheck
    def show_connections(self) -> None:
        """Show current active connections"""

        if len(self.clients) > 0:
            for nickname, data in self.clients.items():
                ui.show(f"{nickname} - IP {data[1]}, PORT {data[2]}")
        else:
            ui.show("Server have no connected clients at the moment")

    @__activityCheck
    def ban(self, nickname: str, duration: int = -1) -> None:
        """Ban a specific client for n minutes or forever"""

        # Set date to unban
        if duration == -1:
            unban_date = datetime.max
        else:
            unban_date = datetime.now() + timedelta(minutes=duration)

        # Ban client by IP with nickname
        if nickname in self.clients:
            client_ip: str = self.clients[nickname][1]
            self.banned[client_ip] = unban_date
            self.close_connection(nickname, self.BANNED_MSG)
        else:
            ui.show(f"Client with name {nickname} is not connected")

    @__activityCheck
    def unban(self, ip: str) -> None:
        """Unban a specific client by IP"""

        if self.__isBanned(ip):
            del self.banned[ip]
            ui.show(f"Client with IP {ip} was unbanned")
            logger.log.info(f"Client with IP {ip} was unbanned")
        else:
            ui.show(f"Client with IP {ip} is not banned")

    @__activityCheck
    def unban_all(self) -> None:
        """Unban all clients"""

        self.banned = dict()
        ui.show("All clients was seccesfully unbanned")
        logger.log.info("All clients was seccesfully unbanned")

    @__activityCheck
    def show_banned(self) -> None:
        """Show all banned clients at the moment"""

        if len(self.banned) == 0:
            ui.show("Total banned clients is 0")
        else:
            for ip in self.banned.copy():
                if self.__isBanned(ip):
                    ui.show(f"{ip} banned until {self.__getUnban_date(ip)}")
                else:
                    del self.banned[ip]

    def __isBanned(self, ip: str) -> bool:
        """Check if user with specified IP have ban"""

        if ip in self.banned.copy():
            if datetime.now() > self.banned[ip]:
                del self.banned[ip]
                return False
            else:
                return True
        else:
            return False

    def __getUnban_date(self, ip: str) -> str:
        """Get date to unban"""

        return self.banned[ip].strftime(self.tFormat)

    def __checkBan_txt(self) -> dict:
        """Fill banned dictionary"""

        try:
            with open('data/banned.txt', 'r') as file:
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
            with open('data/banned.txt', 'w'):
                pass
        else:
            with open('data/banned.txt', 'w') as file:
                for ip, unban in self.banned.items():
                    unban_date = unban.strftime(self.tFormat)
                    file.write(f"{ip}:{unban_date}\n")
