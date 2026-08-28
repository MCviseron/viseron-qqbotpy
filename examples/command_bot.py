"""Command-decorator example using the optional ext module."""

from __future__ import annotations

import logging

from viseron_qqbotpy import Client, Intents, Message
from viseron_qqbotpy.ext import Commands


class CommandBot(Client):
    @Commands("ping", "hello")
    async def ping(self, message: Message, params: list):
        await message.reply(content="pong")

    async def on_at_message_create(self, message: Message):
        # Handlers decorated with @Commands are still regular methods; call
        # them explicitly when the message matches your command routing.
        await self.ping(message, [])


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    bot = CommandBot(intents=Intents.default())
    # Replace with your own credentials before running.
    bot.run(appid="your-appid", secret="your-secret")


if __name__ == "__main__":
    main()
