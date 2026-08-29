# SDK 基础能力

本文列出 viseron-qqbotpy 主包提供的基础能力。这些能力直接从 viseron_qqbotpy 导入，不属于 ext 扩展工具。

ext 扩展工具单独记录在 docs/ext.md。

## 1. 客户端与入口

### Client

机器人客户端入口，负责 WebSocket 连接、事件分发、HTTP 客户端和 Token 管理。

导入：

    from viseron_qqbotpy import Client

作用：

- 继承 Client 并实现 on_ 事件回调。
- 使用 run 或 start 启动机器人。
- 内部提供 client.api、client.robot。

阻塞运行：

    class MyBot(Client):
        async def on_ready(self):
            print("机器人已上线")


    bot = MyBot(intents=Intents.default())
    bot.run(appid="102791796", secret="你的 AppSecret")

异步运行：

    import asyncio


    async def main():
        bot = MyBot(intents=Intents.default())
        await bot.start(appid="102791796", secret="你的 AppSecret")


    asyncio.run(main())

也可以使用 async with：

    async def main():
        bot = MyBot(intents=Intents.default())
        async with bot:
            await bot.start(appid="102791796", secret="你的 AppSecret")

手动关闭：

    await bot.close()

Ctrl+C 退出：

- run 会捕获 KeyboardInterrupt，打印退出信息，不再抛出长串堆栈。
- 使用 start 时，可自行捕获 KeyboardInterrupt 并调用 close。

### AppID 和 AppSecret 字符串校验

AppID 和 AppSecret 必须是字符串，不能是 None、数字或空字符串。

正确：

    bot.run(appid="102791796", secret="你的 AppSecret")

错误：

    bot.run(appid=None, secret="你的 AppSecret")
    bot.run(appid=102791796, secret="你的 AppSecret")

现在 run / start / TokenManager 都会校验，错误时会抛出：

    TypeError: appid 必须是字符串，且不能为空

### load_env

os.getenv 不会自动读取 .env 文件。SDK 提供 load_env 帮助加载 .env。

导入：

    from viseron_qqbotpy import load_env

用法：

    import os
    from pathlib import Path

    from viseron_qqbotpy import load_env

    # 读取当前目录的 .env
    load_env()

    # 或读取指定路径
    load_env(Path(__file__).resolve().parents[1] / ".env")

    appid = os.getenv("APPID", "")
    secret = os.getenv("APPSECRET", "")

.env 支持 KEY=VALUE 和 KEY:VALUE 两种格式：

    APPID=102791796
    APPSECRET=你的 AppSecret

load_env 会把解析结果写入 os.environ，并返回字典。

### BotAPI

HTTP API 封装，提供频道、群聊、单聊、成员、消息、论坛、日程等接口。

导入：

    from viseron_qqbotpy import BotAPI

作用：

- 在 Client 内通过 self.api 调用。
- 也可以和 HTTPClient、TokenManager 组合独立使用。

## 2. 鉴权

### TokenManager

负责使用 AppID 和 AppSecret 获取 access_token，并支持过期前 60 秒无缝刷新。

导入：

    from viseron_qqbotpy import TokenManager

常用方法：

- get_access_token：获取当前有效 token，必要时自动刷新。
- refresh：强制刷新 token。
- authorization：返回 Authorization 头值。
- close：关闭内部会话。

刷新规则：

- 首次调用时，使用 AppID + AppSecret 请求 token。
- token 默认 7200 秒有效。
- 当剩余有效期进入最后 60 秒时，SDK 会获取新 token 并切换。
- 最后 60 秒内新旧 token 都有效，因此切换不会中断正在执行的请求。
- 如果刷新失败，但旧 token 仍然有效，SDK 会继续使用旧 token，并在下次调用时重试。
- 如果旧 token 已经过期且刷新失败，会抛出 TokenError。

可以调整刷新窗口：

    manager = TokenManager("102791796", "你的 AppSecret", refresh_window=30)

单独使用：

    import asyncio

    from viseron_qqbotpy import TokenManager


    async def main():
        manager = TokenManager("102791796", "你的 AppSecret")
        token = await manager.get_access_token()
        print(token)
        await manager.close()


    asyncio.run(main())

### AccessToken

单个 access_token 的值和过期时间对象。

导入：

    from viseron_qqbotpy import AccessToken

常用属性：

- value：token 字符串。
- expires_at：过期时间戳。
- remaining：剩余有效秒数。
- expired：是否已过期。

## 3. HTTP 客户端

### HTTPClient

底层 aiohttp 客户端，负责添加 Authorization 头、解析响应、抛出 APIError。

导入：

    from viseron_qqbotpy import HTTPClient

作用：

- 一般不需要直接使用，Client 和 BotAPI 会内部创建。
- 独立使用 API 时需要创建它。

### Route

表示一个 HTTP 路由和方法。

导入：

    from viseron_qqbotpy import Route

作用：

- 一般不需要直接使用。
- 例如 Route("POST", "/guilds/{guild_id}/channels", guild_id="123")。

## 4. 权限位

### Intents

WebSocket 事件订阅位掩码。

导入：

    from viseron_qqbotpy import Intents

常用方式：

    intents = Intents.default()
    intents = Intents.all()
    intents = Intents.none()
    intents = Intents(guilds=True, public_guild_messages=True)

### Permission

子频道权限位，用于频道权限相关接口。

导入：

    from viseron_qqbotpy import Permission

常用方式：

    add = Permission(view_permission=True, speak_permission=True)
    remove = Permission(manager_permission=True)

## 5. 日志

SDK 会为自己的 logger 提供默认日志配置。

### 默认行为

第一次使用 SDK 日志时，SDK 会自动完成以下配置：

- 控制台输出格式为：

    [INFO]    (gateway.py:行号)函数名    [viseron-botpy]  日志信息

- 控制台中的 [INFO] 为黄色，后面的日志信息为白色。
- 同时在磁盘写入 logs/viseron-botpy.log。
- 日志文件使用 RotatingFileHandler，默认单文件 5 MB，最多保留 5 个旧文件。
- SDK 不会调用 logging.basicConfig，不会影响其他 logger。

### 使用默认日志

什么都不用配置，直接运行即可：

    from viseron_qqbotpy import Client, Intents

    bot = Client(intents=Intents.default())
    bot.run(appid="102791796", secret="你的 AppSecret")

### 自定义日志配置

SDK 提供 configure_logging：

    from viseron_qqbotpy import configure_logging

    configure_logging(
        level=logging.INFO,
        log_file="logs/my-bot.log",
        use_console=True,
        use_file=True,
    )

参数说明：

- level：日志级别，默认 INFO。
- log_file：日志文件路径，默认 logs/viseron-botpy.log。
- console_format：控制台格式，None 表示使用 SDK 默认格式。
- file_format：文件格式，None 表示使用 SDK 默认格式。
- use_console：是否输出到控制台。
- use_file：是否写入磁盘日志文件。

### 关闭磁盘日志

    configure_logging(use_file=False)

### 只写文件，不输出控制台

    configure_logging(use_console=False, use_file=True)

### get_logger

获取 SDK 或业务自己的 logger。

导入：

    from viseron_qqbotpy import get_logger

用法：

    logger = get_logger("my_bot")
    logger.info("启动成功")

说明：

- get_logger 不传参数时返回 SDK 内部使用的 viseron_qqbotpy logger。
- 业务自己的 logger 不会被 SDK 自动配置。

## 6. 事件模型

事件回调收到的对象，定义在 viseron_qqbotpy.models。

从主包导入：

    from viseron_qqbotpy import Message, DirectMessage, GroupMessage, C2CMessage

完整事件模型列表：

- User：用户对象
- Message：频道消息事件对象
- DirectMessage：私信消息事件对象
- GroupMessage：群消息事件对象
- C2CMessage：单聊消息事件对象
- MessageAudit：消息审核事件对象
- Guild：频道对象
- Channel：子频道对象
- Member：频道成员对象
- Reaction：表情表态事件对象
- Interaction：互动事件对象
- AudioAction：音频动作事件对象
- PublicAudio：音视频或直播子频道成员进出事件对象
- ForumThread：论坛主题事件对象
- OpenForumThread：开放论坛主题事件对象
- GroupManageEvent：群管理事件对象
- C2CManageEvent：单聊管理事件对象
- GroupMemberEvent：群成员事件对象
- GroupJoinRequestEvent：入群申请事件对象
- SubscribeMessageStatusEvent：订阅消息授权状态事件对象

这些模型都保留 raw 字段，可以访问平台下发的完整原始数据。

## 7. 异常

从主包导入：

    from viseron_qqbotpy import APIError

完整异常列表：

- ViseronError：SDK 所有异常的基类。
- APIError：OpenAPI 请求失败时抛出。
- AuthenticationFailedError：HTTP 401 认证失败。
- ForbiddenError：HTTP 403 无权限。
- NotFoundError：HTTP 404 接口或资源不存在。
- MethodNotAllowedError：HTTP 405 方法不允许。
- RateLimitError：HTTP 429 频率限制。
- ServerError：HTTP 5xx 服务端错误。
- TokenError：access_token 获取或刷新失败。
- WebSocketError：网关协议或连接错误。

APIError 常用属性：

- status：HTTP 状态码。
- code：平台业务错误码。
- trace_id：链路追踪 ID。
- message：错误消息。
- data：错误附带数据。

示例：

    from viseron_qqbotpy import APIError

    try:
        await self.api.get_guild("频道 ID")
    except APIError as exc:
        print(exc.status, exc.code, exc.trace_id, exc)

## 8. 类型辅助

TypedDict 类型提示，定义在 viseron_qqbotpy.types。

导入示例：

    from viseron_qqbotpy.types import MessageMarkdown, Keyboard, Embed

作用：

- 为消息和事件 payload 提供编辑器提示。
- 不是运行时必需，所有 API 也接受普通 dict。

## 9. Webhook 签名验证

Webhook 签名功能在主包 viseron_qqbotpy.webhook，但依赖 cryptography，需要安装可选依赖。

安装：

    pip install -e ".[webhook]"

导入：

    from viseron_qqbotpy.webhook import verify_signature, sign_validation

作用：

- verify_signature：验证平台回调请求签名。
- sign_validation：生成回调地址验证响应。

详细说明见 docs/webhook.md。

## 10. 基础能力与 ext 的边界

主包基础能力：

- Client
- BotAPI
- TokenManager / AccessToken
- HTTPClient / Route
- Intents / Permission
- load_env：加载 .env 文件
- get_logger
- 事件模型
- 异常
- types 类型提示
- webhook 签名验证

ext 扩展能力：

- Commands / command：命令装饰器
- load_yaml：YAML 配置读取
- convert_color / Color：颜色转换
- escape_channel_jump / parse_channel_jump：频道跳转
- create_scheduler：APScheduler 调度器

扩展能力详见 docs/ext.md。
