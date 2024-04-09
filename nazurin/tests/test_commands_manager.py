import unittest
from textwrap import dedent

from aiogram.filters import Command
from aiogram.types import BotCommand

from nazurin.commands import CommandsManager


class TestCommandsManager(unittest.TestCase):
    def setUp(self) -> None:
        self.manager = CommandsManager()
        return super().setUp()

    def register_commands(self):
        self.manager.register(
            Command("first", "alternative"),
            description="First Command",
            help_text="First Command Help Text",
        )
        self.manager.register(
            Command("second"),
            args="ARG",
            description="Second Command",
        )

    def test_resolve_names(self):
        names = ["first", "second"]
        self.assertEqual(self.manager.resolve_names(Command(*names)), names)

    def test_command_list(self):
        self.manager.reset()
        self.register_commands()
        self.assertEqual(
            list(self.manager.list()),
            [
                BotCommand(command="alternative", description="First Command"),
                BotCommand(command="first", description="First Command"),
                BotCommand(command="second", description="Second Command"),
            ],
        )

    def test_help_text(self):
        self.manager.reset()
        self.register_commands()
        self.assertEqual(
            self.manager.help_text(),
            "/alternative, /first — First Command\n/second ARG — Second Command",
        )

    def test_command_help(self):
        self.manager.reset()
        self.register_commands()
        self.assertEqual(
            self.manager.help("alternative"),
            dedent(
                """
            First Command
            <b>Usage:</b> /alternative, /first

            First Command Help Text
            """,
            ),
        )
        self.assertEqual(
            self.manager.help("second"),
            dedent(
                """
            Second Command
            <b>Usage:</b> /second ARG
            """,
            ),
        )
        self.assertIsNone(self.manager.help("third"))
