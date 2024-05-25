from rich.console import Console
from rich.theme import Theme
from rich.prompt import Confirm


class Interface:
    def __init__(self) -> None:
        self.__theme = Theme({})

        self.console = Console(
            width=100, theme=self.__theme)  # Max 30 characrer

    def enter(self, prompt):
        pass

    def show(self, prompt):
        pass

    def logo(self):
        pass

    def start_prompt(self) -> bool:
        return Confirm.ask("Do you want to start server?")


ui = Interface()
