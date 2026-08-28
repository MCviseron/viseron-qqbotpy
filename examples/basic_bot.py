"""Minimal echo bot.

Run from the project root::

    python examples/basic_bot.py

The .env file is loaded explicitly because os.getenv() does not read .env by
itself.  APPID and APPSECRET must both be strings.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from viseron_qqbotpy import Client, Intents, Message, load_env


class EchoBot(Client):
    async def on_ready(self):
        print("ready", self.robot)

    async def on_at_message_create(self, message: Message):
        await message.reply(content=f"echo: {message.content}")


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    # 从项目根目录的 .env 读取 APPID / APPSECRET
    load_env(Path(__file__).resolve().parents[1] / ".env")

    appid = os.getenv("APPID", "")
    secret = os.getenv("APPSECRET", "")
    if not appid or not secret:
        raise SystemExit("APPID/APPSECRET missing; set them in .env or environment")

    bot = EchoBot(intents=Intents.default())
    bot.run(appid=appid, secret=secret)


if __name__ == "__main__":
    main()
