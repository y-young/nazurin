import dataclasses
from textwrap import dedent
from typing import Iterator, List, Optional

from aiogram.filters import Command
from aiogram.types import BotCommand


@dataclasses.dataclass
class NazurinCommand:
    names: List[str]
    args: str
    description: str
    help_text: str

    @property
    def usage(self) -> str:
        text = f"{', '.join(['/' + name for name in self.names])}"
        if self.args:
            text += f" {self.args}"
        return text

    @property
    def help(self) -> str:
        text = dedent(
            f"""
            {self.description}
            <b>Usage:</b> {self.usage}
            """,
        )
        if self.help_text:
            text += dedent(
                f"""
                {self.help_text}
                """,
            )
        return text


class CommandsManager:
    def __init__(self) -> None:
        self.commands: List[NazurinCommand] = []

    def register(
        self,
        *custom_filters,
        args="",
        description="",
        help_text="",
    ) -> None:
        names = self.resolve_names(*custom_filters)
        if not names:
            return
        command = NazurinCommand(
            names=names,
            args=args,
            description=description,
            help_text=help_text,
        )
        self.commands.append(command)

    def resolve_names(self, *custom_filters) -> List[str]:
        names = []
        for custom_filter in custom_filters:
            if isinstance(custom_filter, Command):
                names += custom_filter.commands
        return sorted(names)

    def list(self) -> Iterator[BotCommand]:
        for command in self.commands:
            for name in command.names:
                yield BotCommand(command=name, description=command.description)

    def help_text(self) -> str:
        return "\n".join(
            [
                f"{command.usage} — {command.description}"
                for command in sorted(self.commands, key=lambda x: x.names[0])
            ],
        )

    def help(self, command: str) -> Optional[str]:
        for cmd in self.commands:
            if command in cmd.names:
                return cmd.help
        return None

    def reset(self) -> None:
        self.commands = []
