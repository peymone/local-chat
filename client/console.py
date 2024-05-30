from sys import argv
from threading import Thread

from client import Client


class Console:
    def __init__(self) -> None:
        self.__command = None
        self.__commands = {
            'exit': "close application",
            'commands': "show all available commands",

            'start': "start client",
            'stop': "stop client",
            'send message': "send message to all clients",
        }

    def show_commands(self):
        """Show all available commands"""

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

                print(cmd, end=' ')
                print(args, end=' ' * indentation)

            else:
                print(command, end=' ' * indentation)

            print(description)

        print('\n')

    def commands_handler(self, cmd=None):
        """Enter and execute commands"""

        try:
            while self.__command != 'exit':
                self.__command = input('Enter command /> ')

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
                    case 'start': Thread(target=client.start).start()
                    case 'stop': client.stop()
                    case 'send':
                        if args is None:
                            print("message can not be empty")
                        else:
                            message = ' '.join(args)
                            client.send(message)

        except KeyboardInterrupt:
            self.__command = 'exit'

        print('\n')


if __name__ == '__main__':
    admin_console = Console()

    if len(argv) > 1:
        client = Client(argv[1], int(argv[2]))
    else:  # TEST ONLY
        client = Client('192.168.0.111', 6061)

    admin_console.commands_handler()
