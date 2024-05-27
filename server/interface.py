from datetime import datetime

from rich.theme import Theme
from rich.prompt import Confirm
from rich.console import Console

from pyfiglet import figlet_format


class Interface:
    def __init__(self) -> None:
        self.tFormat = "%H:%M:%S"
        self.__theme = Theme({
            'system': 'cyan italic bold',
            'license': 'green italic dim',
            'args': 'white dim',
            'logo': 'green bold',
            'admin': 'red',
            'user': 'green',
            'warning': 'yellow1'
        })

        self.console = Console(theme=self.__theme)

    def enter(self, prompt: str, style='system') -> str:
        return self.console.input(f"[{style}]{prompt}[/{style}]")

    def show(self, message: str, sender: str = 'system', style: str = 'system') -> None:
        now = datetime.now().strftime(self.tFormat)

        match sender:
            # System can be warning message or just information
            case 'system':
                # print('\n')
                self.console.print(f"[{style}]{now} {message}[/{style}]")
                # print('\n')
            case _:
                msg = f"[{style}]{now} {sender}:[/{style}]  {message}"
                # print('\n')
                self.console.print(msg)
                # print('\n')

    def show_logo(self, logo_text: str = 'local chat') -> None:
        logo = figlet_format(logo_text, font='larry3d')
        self.console.print(logo, style='logo')
        self.console.print('(c) by Cassidy Bell', style='license')

    def start_prompt(self) -> bool:
        confirm = Confirm(console=self.console)
        confirmation = confirm.ask("Do you want to start server?")
        self.clear_screen()
        return confirmation

    def clear_screen(self):
        ui.console.clear()


ui = Interface()
