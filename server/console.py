from server import Server
from logger import logger
from interface import ui

from sys import argv
from threading import Thread


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "close application",
            'clear': "clear the screen of characters",
            'commands': "show all available commands",

            'status': "show current server status",
            'start': "start server",
            'stop': "stop server",
            'clients': "show clients currently connected to server",
            'disconnect nickname': "disconnect client with a specific nickname",
            'send nickname message': "send message to a specific client",
            'sendall message': "broadcast message to all connected clients",
            'ban nickname n': "ban client for n minutes or forever (omitted n)",
            'banned': "show all banned clients at the moment",
            'unban ip': "unban client by IP",
            'unbanall': "unban all clients",
        }

    def show_commands(self):
        """Show all available commands"""

        print('\n')
        ui.console.print("List of available commands: ", style='system')
        print('\n')

        # Calculate the number of spaces from the longest command length
        spaces = 30
        maxCmd_spaces = len(max(self.__commands, key=len)) + spaces

        for command, description in self.__commands.items():
            # Сalculate the required number of spaces
            indentation = maxCmd_spaces - len(command)

            # Apply a custom interface to command arguments
            if len(command.split()) > 1:
                cmd = command.split()[0]
                args = ' '.join(command.split()[1:])

                ui.console.print(cmd, end=' ')
                ui.console.print(args, style='args', end=' ' * indentation)

            else:
                ui.console.print(command, end=' ' * indentation)

            ui.console.print(description)

        print('\n')

    def commands_handler(self, cmd=None):
        """Enter and execute commands"""

        logger.debug.debug("commands handler - start")

        try:
            while self.__command != 'exit':
                self.__command = ui.enter('Enter command /> ')

                # Parse command and arguments
                if len(self.__command.split()) >= 2:
                    command = self.__command.split()[0]
                    args = self.__command.split()[1:]
                else:
                    command = self.__command
                    args = None

                logger.debug.debug(f"commands entered: {command} {args}")

                # Execute commands
                match command:
                    case 'clear': ui.clear_screen()
                    case 'commands': self.show_commands()
                    case 'status': server.status()
                    case 'start': Thread(target=server.start).start()
                    case 'stop': server.stop()
                    case 'clients': server.show_connections()
                    case 'disconnect':
                        if args is None:
                            ui.show("Nickname can not be empty", style='warning')
                        else:
                            server.close_connection(args[0], server.CLOSE_MSG)
                    case 'send':
                        if args is None or len(args) < 2:
                            ui.show("Nickname and message can not be empty", style='warning')
                        else:
                            message = ' '.join(args[1:])
                            server.send(args[0], message)
                    case 'sendall':
                        if args is None:
                            ui.show("Message can not be empty", style='warning')
                        else:
                            message = ' '.join(args[0:])
                            server.broadcast(message)
                    case 'ban':
                        if args is None:
                            ui.show("Nickname can not be empy", style='warning')
                        elif len(args) < 2:
                            server.ban(args[0])
                        else:
                            try:
                                ban_duration = int(args[1])
                                server.ban(args[0], ban_duration)
                            except ValueError:
                                ui.show("Ban duration must be integer", style='warning')
                    case 'banned': server.show_banned()
                    case 'unban':
                        if args is None:
                            ui.show("IP address can not be empy", style='warning')
                        else:
                            server.unban(args[0])
                    case 'unbanall': server.unban_all()

        except KeyboardInterrupt:
            self.__command = 'exit'

        if server.isActive:
            server.stop()

        logger.debug.debug("commands handler - stop")
        ui.clear_screen()


if __name__ == '__main__':
    admin_console = Console()

    # Creare server object with custom port or default
    if len(argv) > 1:
        server = Server(port=int(argv[1]))
    else:
        server = Server(port=60065)

    # Start server immediately or display a list of commands
    if ui.start_prompt() is True:
        ui.show_logo()
        Thread(target=server.start).start()
        print('\n')
    else:
        ui.show_logo()
        admin_console.show_commands()

    # Start entering and processing commands
    admin_console.commands_handler()
