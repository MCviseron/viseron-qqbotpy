# viseron-qqbotpy

一个基于 **asyncio + aiohttp** 的 QQ 机器人 Python SDK，针对
[QQ 机器人开放平台 API v2](https://bot.q.qq.com/wiki/develop/api-v2/) 重新设计。

它参考了旧版 qq-botpy 的 API 形状，但内部实现是重写的：共享 HTTP 会话、
无中断的 access_token 刷新、由 Hello 事件驱动的心跳、更清晰的错误与事件模型。

## 特性

- 使用 appid + secret 获取 access token，并支持 **过期前 60 秒无缝刷新**
- WebSocket 网关：Identify / Resume / Heartbeat / 分片 / 断线重连
- 覆盖频道、群聊、单聊、身份组、成员、消息、表情、日程、论坛、音频、公告、
  接口权限、富媒体上传、入群审批、指令面板、自定义菜单等 API
- 事件模型为 dataclass，同时保留完整原始 payload（raw 字段）
- 可选 Webhook Ed25519 签名验证

## 使用文档

完整使用文档见 docs/ 目录：

- docs/getting-started.md：安装、快速开始、Intents、直接调用 API
- docs/core.md：SDK 基础能力，如 Client、TokenManager、BotAPI、日志、异常等
- docs/events.md：事件监听、事件表、事件对象字段
- docs/features.md：常见功能实现示例
- docs/api-reference.md：API 方法参考
- docs/ext.md：命令装饰器、颜色转换等扩展
- docs/webhook.md：Webhook 签名验证
- docs/publish.md：构建、上架 PyPI、安装与下载方式

## 安装

    cd viseron-botpy
    pip install -e .

开发模式安装额外依赖：

    pip install -e ".[dev]"

## 快速开始

    import os
    from pathlib import Path

    from viseron_qqbotpy import Client, Intents, Message, configure_logging, load_env

    # 读取项目根目录的 .env
    load_env(Path(__file__).resolve().parents[1] / ".env")

    # 使用 SDK 默认日志格式，并写入 logs/viseron-botpy.log
    configure_logging()

    APPID = os.getenv("APPID", "")
    APPSECRET = os.getenv("APPSECRET", "")


    class MyBot(Client):
        async def on_ready(self):
            print("机器人已上线")

        async def on_at_message_create(self, message: Message):
            await message.reply(content=f"收到: {message.content}")


    if __name__ == "__main__":
        bot = MyBot(intents=Intents.default())
        bot.run(appid=APPID, secret=APPSECRET)

更多事件与用法见 examples/ 和 docs/。

## 事件订阅

创建客户端时传入 Intents：

    intents = Intents.default()          # 公域事件
    intents = Intents.all()              # 全部事件（需私域权限）
    intents = Intents(guilds=True, public_guild_messages=True)

网关事件名会映射为 on_<event_type小写>，例如：

- AT_MESSAGE_CREATE -> on_at_message_create
- GROUP_AT_MESSAGE_CREATE -> on_group_at_message_create
- C2C_MESSAGE_CREATE -> on_c2c_message_create
- INTERACTION_CREATE -> on_interaction_create
- GROUP_MEMBER_ADD -> on_group_member_add
- READY / RESUMED -> on_ready / on_resumed（无参数）

## 直接调用 API

在 Client 子类中，可以直接使用 self.api：

    class MyBot(Client):
        async def on_ready(self):
            guilds = await self.api.me_guilds()
            print(guilds)

如果只需要 HTTP API，不连接 WebSocket：

    import asyncio

    from viseron_qqbotpy import BotAPI, HTTPClient, TokenManager


    async def main():
        token = TokenManager("你的 AppID", "你的 AppSecret")
        http = HTTPClient(token)
        api = BotAPI(http)

        me = await api.me()
        print(me)

        await http.close()
        await token.close()


    asyncio.run(main())

## Access Token 刷新机制

- 平台 access token 默认 7200 秒有效。
- 在 token 剩余有效期进入最后 60 秒时，SDK 会透明地获取新 token 并切换；
  此时新旧 token 都有效，因此不会中断正在执行的请求。
- 如果刷新失败但旧 token 尚未过期，SDK 会继续使用旧 token，并在下一次调用时重试。
- 可通过 TokenManager 单独使用该能力。

## Webhook 签名验证

    from viseron_qqbotpy.webhook import verify_signature, sign_validation

    ok = verify_signature(
        secret="AppSecret",
        timestamp=request.headers["X-Signature-Timestamp"],
        body=request.body.decode(),
        signature_hex=request.headers["X-Signature-Ed25519"],
    )

## 项目结构

    src/viseron_qqbotpy/
      client.py       # Client 入口
      api.py          # OpenAPI 封装
      gateway.py      # WebSocket 网关/分片/重连
      token.py        # access token 无缝刷新
      http.py         # HTTP 客户端
      env.py          # .env 文件加载
      logging.py      # 默认日志与 configure_logging
      dispatcher.py   # 事件解析与分发
      models.py       # 事件 dataclass
      types.py        # payload 类型提示
      flags.py        # Intents / Permission
      errors.py       # 异常体系
      webhook.py      # 可选 Webhook 签名
      ext/            # 命令、颜色、频道跳转等扩展

## License

MIT
