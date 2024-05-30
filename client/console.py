from sys import argv
from threading import Thread

from client import Client
from interface import ui


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "close application",
            'clear': "clear the screen of characters",
            'commands': "show all available commands",

            'start': "start client",
            'stop': "stop client",
            'send message': "send message to all clients",
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

    def commands_handler(self):
        """Enter and execute commands"""

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

                # Execute commands
                match command:
                    case 'clear': ui.clear_screen()
                    case 'commands': self.show_commands()
                    case 'start': Thread(target=client.start).start()
                    case 'stop': client.stop()
                    case 'send':
                        if args is None:
                            ui.show("message can not be empty",
                                    style='warning')
                        else:
                            message = ' '.join(args)
                            client.send(message)

        except KeyboardInterrupt:
            self.__command = 'exit'

        if client.isActive:
            client.stop()

        ui.clear_screen()


if __name__ == '__main__':
    admin_console = Console()
    nickname = ui.enter("Enter your nickname: ")

    # Creare client object with custom port or default
    if len(argv) > 1:
        client = Client(argv[1], int(argv[2]), nickname)
    else:
        client = Client('192.168.0.111', 60065, nickname)

    # Start client immediately or display a list of commands
    if ui.start_prompt() is True:
        ui.show_logo()
        Thread(target=client.start).start()
        print('\n')
    else:
        ui.show_logo()
        admin_console.show_commands()

    # Start entering and processing commands
    admin_console.commands_handler()
