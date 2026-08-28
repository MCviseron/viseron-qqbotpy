# 扩展工具

viseron_qqbotpy.ext 提供一些常用扩展能力。

## 1. 命令装饰器

Commands 用于解析消息中的命令：

    from viseron_qqbotpy import Client, Intents, Message
    from viseron_qqbotpy.ext import Commands


    class MyBot(Client):
        @Commands("ping", "hello")
        async def handle_command(self, message: Message, params):
            await message.reply(content="pong")

        async def on_at_message_create(self, message: Message):
            # 这里简化处理：直接调用被装饰的方法
            await self.handle_command(message, [])

装饰器支持前缀，默认是 /。所以 /ping 和 /hello 都会匹配。也可以传入 prefix：

    @Commands("help", prefix="!")
    async def help_command(self, message, params):
        await message.reply(content="帮助内容")

params 是命令名后面的参数列表。

## 2. 颜色转换

    from viseron_qqbotpy.ext import convert_color

    # RGB 元组
    color = convert_color((255, 0, 0))

    # 十六进制字符串
    color = convert_color("#FF0000")

    # 整数直接返回
    color = convert_color(16711680)

转换结果可以用于身份组 color 等字段。

## 3. 频道跳转

    from viseron_qqbotpy.ext import escape_channel_jump, parse_channel_jump

    # 生成频道跳转文本
    text = escape_channel_jump("子频道 ID")

    # 从消息内容中解析频道跳转
    pairs = parse_channel_jump("欢迎来到 <#123456> 频道")
    for raw, channel_id in pairs:
        print(raw, channel_id)

## 4. YAML 配置读取

    from viseron_qqbotpy.ext import load_yaml

    config = load_yaml("config.yaml")
    print(config)

需要安装 PyYAML：

    pip install -e ".[ext]"

## 5. APScheduler 定时任务

    from viseron_qqbotpy.ext import create_scheduler

    scheduler = create_scheduler()
    scheduler.add_job(my_async_func, "interval", seconds=60)
    scheduler.start()

需要安装 APScheduler：

    pip install -e ".[ext]"
