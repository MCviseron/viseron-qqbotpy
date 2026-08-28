# 快速开始

本文档假设你已经有一个 QQ 开放平台的机器人 AppID 和 AppSecret。

## 1. 安装

进入项目目录并安装：

    cd viseron-botpy
    pip install -e .

如果需要开发测试依赖：

    pip install -e ".[dev]"

如果需要 Webhook 签名验证：

    pip install -e ".[webhook]"

如果使用了conda控制：

    在当前conda环境下python -m pip install -e .

## 2. 第一个机器人

创建文件 bot.py：

    import logging

    from viseron_qqbotpy import Client, Intents, Message

    logging.basicConfig(level=logging.INFO)

    class MyBot(Client):
        async def on_ready(self):
            print("机器人已上线")

        async def on_at_message_create(self, message: Message):
            # 回复频道里 @ 机器人的消息
            await message.reply(content="你好，我是机器人")

    if __name__ == "__main__":
        bot = MyBot(intents=Intents.default())
        bot.run(appid="你的 AppID", secret="你的 AppSecret")

运行：

    python bot.py

说明：

- Client 是入口类，继承它并实现 on\_ 开头的事件回调。
- Intents 控制要订阅哪些事件。
- run 是阻塞入口，内部使用 asyncio.run 启动机器人。
- Message 事件对象带有 reply 方法，可以快捷回复。

## 2.1 从 .env 读取 AppID 和 AppSecret

os.getenv 不会自动读取 .env 文件。SDK 提供了 load_env，可以先把 .env 中的配置写入环境变量。

示例：

    import logging
    import os
    from pathlib import Path

    from viseron_qqbotpy import Client, Intents, Message, load_env

    logging.basicConfig(level=logging.INFO)

    # 读取项目根目录的 .env
    load_env(Path(__file__).resolve().parents[1] / ".env")

    APPID = os.getenv("APPID", "")
    APPSECRET = os.getenv("APPSECRET", "")


    class MyBot(Client):
        async def on_ready(self):
            print("机器人已上线")

        async def on_at_message_create(self, message: Message):
            await message.reply(content="你好，我是机器人")


    if __name__ == "__main__":
        bot = MyBot(intents=Intents.default())
        bot.run(appid=APPID, secret=APPSECRET)

.env 文件格式：

    APPID=你的AppID
    APPSECRET=你的AppSecret

注意：

- APPID 和 APPSECRET 必须是字符串，不能是 None 或数字。
- 如果直接传入，写成 bot.run(appid="102791796", secret="你的AppSecret")。
- 如果 APPID 是 None，SDK 会直接抛出清晰的 TypeError，而不是等到请求 token 时才报 appid invalid。
- 运行中按 Ctrl+C，SDK 会打印退出信息，不会抛出长串 KeyboardInterrupt 堆栈。

## 3. 异步场景

如果代码本身已经在 asyncio 事件循环中，不要使用 run，而是使用 start：

    import asyncio

    from viseron_qqbotpy import Client, Intents

    class MyBot(Client):
        pass

    async def main():
        bot = MyBot(intents=Intents.default())
        await bot.start(appid="AppID", secret="AppSecret")

    asyncio.run(main())

也可以使用 async with：

    async def main():
        bot = MyBot(intents=Intents.default())
        async with bot:
            await bot.start(appid="AppID", secret="AppSecret")

## 4. Intents 事件订阅

Intents 是位掩码。常用方式：

    from viseron_qqbotpy import Intents

    # 公域机器人常用：监听公域消息、频道、成员、互动等
    intents = Intents.default()

    # 监听全部已知事件，需要对应私域权限
    intents = Intents.all()

    # 不订阅任何事件
    intents = Intents.none()

    # 自定义订阅
    intents = Intents(
        guilds=True,
        guild_members=True,
        public_guild_messages=True,
        group_and_c2c_event=True,
    )

常用 intent 位：

- guilds：频道和子频道事件
- guild_members：频道成员事件
- guild_messages：私域消息事件，仅私域机器人可用
- guild_message_reactions：消息表情表态事件
- direct_message：私信事件
- group_and_c2c_event：群聊和单聊事件
- interaction：互动事件
- message_audit：消息审核事件
- forums：论坛事件，仅私域机器人可用
- audio_action：音频事件
- public_guild_messages：公域消息事件

## 5. 直接调用 API

除了在事件回调中使用 message.reply，也可以通过 client.api 调用接口：

    class MyBot(Client):
        async def on_ready(self):
            guilds = await self.api.me_guilds()
            print("我加入的频道：", guilds)

如果只使用 HTTP API，不连接 WebSocket，可以独立创建：

    import asyncio

    from viseron_qqbotpy import BotAPI, HTTPClient, TokenManager

    async def main():
        token = TokenManager("AppID", "AppSecret")
        http = HTTPClient(token)
        api = BotAPI(http)

        me = await api.me()
        print(me)

        await http.close()
        await token.close()

    asyncio.run(main())

## 6. Access Token 自动刷新

SDK 会自动管理 access_token：

- 首次调用 API 时，使用 AppID + AppSecret 获取 token。
- token 默认 7200 秒有效。
- 当 token 剩余有效期进入最后 60 秒时，SDK 会透明获取新 token 并切换。
- 在最后 60 秒内新旧 token 都有效，因此不会中断正在执行的请求。
- 如果刷新失败但旧 token 仍未过期，SDK 会继续使用旧 token，并在后续请求中重试。

开发者通常不需要手动处理 token。如果需要单独使用 TokenManager：

    from viseron_qqbotpy import TokenManager

    async def main():
        manager = TokenManager("AppID", "AppSecret")
        token = await manager.get_access_token()
        print(token)
        await manager.close()
