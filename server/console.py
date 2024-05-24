from server import Server

from sys import argv
from threading import Thread


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "close application",
            'commands': "Show all available commands",

            'status': "Show current server status",
            'start': "Start server",
            'stop': "Stop server",
            'clients': "Show clients currently connected to server",
            'disconnect |nickname|': "Disconnect client with specific nickname",
            'send |nickname| |message|': "Send message to a specific client",
            'sendall |message|': "Broadcast message to all connected clients",
            'ban |nickname| |n|': "Ban client for n minutes or forever (omitted n)",
            'banned': "Show all banned clients at the moment",
            'unban |ip|': "Unban client by IP",
            'unbanall': "Unban all clients",

            'nickname |old_nick| |new_nick|': "Change nickname to a specific client"
        }

    def show_commands(self):
        """Show all available commands"""

        for command, description in self.__commands.items():
            print(f"{command} {description}")

    def commands_handler(self):
        """Enter and execute commands"""

        try:
            while self.__command != 'exit':
                self.__command = input("Enter command /> ")

                # Parse command and arguments
                if len(self.__command.split()) >= 2:
                    command = self.__command.split()[0]
                    args = self.__command.split()[1:]
                else:
                    command = self.__command
                    args = None

                # Execute commands
                match command:
                    case 'commands': self.show_commands()
                    case 'status': server.status()
                    case 'start': Thread(target=server.start).start()
                    case 'stop': server.stop()
                    case 'clients': server.clients()  # Not implemented
                    case 'disconnect':
                        if args is None:
                            print("Nickname can not be empty")
                        else:
                            server.close_connection(args[0], server.CLOSE_MSG)
                    case 'send':
                        if args is None or len(args) < 2:
                            print("Nickname and message can not be empty")
                        else:
                            message = ' '.join(args[1:])
                            server.send(args[0], message)
                    case 'sendall':
                        if args is None:
                            print("Message can not be empty")
                        else:
                            message = ' '.join(args[0:])
                            server.broadcast(message)
                    case 'ban':
                        if args is None:
                            print("Nickname can not be empy")
                        elif len(args) < 2:
                            server.ban(args[0])
                        else:
                            try:
                                ban_duration = int(args[1])
                                server.ban(args[0], ban_duration)
                            except ValueError:
                                print("Ban duration must be integer")
                    case 'banned': server.show_banned()
                    case 'unban':
                        if args is None:
                            print("IP address can not be empy")
                        else:
                            server.unban(args[0])
                    case 'unbanall': server.unban_all()
                    case 'nickname':  # Not implemented
                        if len(args) < 2:
                            print("Previous nick and new nick can not be empty")
                        else:
                            pass

        except KeyboardInterrupt:
            if server.isActive:
                server.stop()
            self.__command = 'exit'


if __name__ == '__main__':
    # Set server port manually or use 6061 by default
    if len(argv) > 1:
        server = Server(port=int(argv[1]))
    else:
        server = Server(port=6061)

    admin_console = Console()
    admin_console.show_commands()
    admin_console.commands_handler()
