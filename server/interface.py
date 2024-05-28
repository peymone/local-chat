from datetime import datetime

# Used for custom rerminal interface
from rich.theme import Theme
from rich.prompt import Confirm
from rich.console import Console

# Used for draw text in 3d
from pyfiglet import figlet_format


class Interface:
    """Class for custom UI - colors, logo, etc."""

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
        """Custom input method with prompt and color"""

        return self.console.input(f"[{style}]{prompt}[/{style}]")

    def show(self, message: str, sender: str = 'system', style: str = 'system') -> None:
        """Custom print method with color and time"""

        now = datetime.now().strftime(self.tFormat)

        match sender:
            # System can be warning message or just information
            case 'system':
                self.console.print(f"[{style}]{now} {message}[/{style}]")
            case _:
                msg = f"[{style}]{now} {sender}:[/{style}]  {message}"
                self.console.print(msg)

    def show_logo(self, logo_text: str = 'local chat') -> None:
        """Show logo with pyfiglet lib"""

        logo = figlet_format(logo_text, font='larry3d')
        self.console.print(logo, style='logo')
        self.console.print('(c) by Cassidy Bell', style='license')

    def start_prompt(self) -> bool:
        """Starting choice for turning on the server"""

        confirm = Confirm(console=self.console)
        confirmation = confirm.ask("Do you want to start server?")
        self.clear_screen()
        return confirmation

    def clear_screen(self):
        """Clear the screen of characters"""

        ui.console.clear()


ui = Interface()
