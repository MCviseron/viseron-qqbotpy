# Changelog

本项目的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- 新增 upload_group_media：封装群聊富媒体分片上传流程，调用后直接返回 files 接口结果。
- 新增 upload_c2c_media：封装单聊富媒体分片上传流程，调用后直接返回 files 接口结果。
- post_group_file / post_c2c_file 的 url 参数改为可选，支持分片上传合并场景。

## [0.2.0] - 2026-08-30

### Added

- 新增 configure_logging，可配置 SDK 日志级别、控制台格式、文件路径、是否输出控制台/写入磁盘。
- 新增 SDK 默认日志配置：控制台使用彩色格式，并自动写入 logs/viseron_qqbotpy.log。
- 新增 load_env，用于读取 .env 文件。
- 新增 env.py 模块，并在主包导出 load_env。
- 新增 TokenManager 无缝刷新单元测试：窗口内刷新、刷新失败回退旧 token、并发只刷新一次。
- 新增 docs/core.md，说明 SDK 基础能力。
- 新增 docs/publish.md，说明构建、上架 PyPI 与安装方式。
- 新增 .gitignore 对 logs/、.pypirc、*.pem、*.key 等敏感或生成文件的忽略。
- 新增 CHANGELOG.md，建立版本记录。

### Changed

- 日志消息前缀统一为 [viseron_qqbotpy]。
- 默认日志文件从 logs/viseron-botpy.log 改为 logs/viseron_qqbotpy.log。
- 控制台日志格式调整为 [LEVEL] (filename:lineno)funcName 黄色，消息白色。
- README 快速开始示例改为使用 load_env 和 configure_logging。
- README 直接调用 API 示例改为完整可运行示例。
- docs/features.md 每个功能示例补充功能说明、参数来源、返回内容和注意事项。
- docs/events.md 事件表新增事件说明列。
- docs 目录结构新增 core.md 和 publish.md。
- HTTPClient.close 仅关闭自身创建的 session。
- GatewayShard 改为显式关闭 WebSocket session。

### Fixed

- 修复日程创建/修改接口 payload 字段名错误：reminder_id 改为 remind_type。
- 修复文档中群成员禁言示例：op 和 mute_expire_at 格式错误。
- 修复 README 中直接调用 API 示例 bot 未定义的问题。

### Removed

- 移除旧日志前缀 [viseron-botpy]。
- 移除 README 中旧版 logging.basicConfig 示例。

## [0.1.0] - 2026-08-29

### Added

- 新增现代 asyncio + aiohttp 架构的 QQ 机器人 Python SDK。
- 新增 Client 入口，支持 run、start、async with 三种启动方式。
- 新增 TokenManager，支持 access_token 自动获取、缓存与过期前 60 秒无缝刷新。
- 新增 HTTPClient，统一 Authorization 头、响应解析和错误归一化。
- 新增 BotAPI，覆盖频道、子频道、身份组、成员、消息、私信、群聊、单聊、表情表态、日程、论坛、音频、公告、接口权限、富媒体上传、入群审批、指令面板、自定义菜单等接口。
- 新增 WebSocket 网关，支持 Identify、Resume、Heartbeat、分片、断线重连。
- 新增 EventDispatcher 与事件 dataclass 模型，所有模型保留 raw 原始 payload。
- 新增 Intents 与 Permission 位掩码。
- 新增 Webhook Ed25519 签名验证工具。
- 新增 ext 扩展：命令装饰器、颜色转换、频道跳转、YAML 配置读取、APScheduler 调度器。
- 新增使用文档 docs/，包含快速开始、基础能力、事件、功能指南、API 参考、扩展、Webhook、构建发布。
- 新增 README.md、pyproject.toml、examples 和 tests。
- 新增 PyPI 构建配置，支持生成 wheel 与 sdist。

### Changed

- access_token 请求地址更新为 https://api.bot.qq.com/app/getAppAccessToken。
- Authorization 头格式统一为 QQBot {access_token}。
- 网关心跳间隔改为使用 Hello 事件下发的 heartbeat_interval。
- 事件分发统一按小写事件名映射到 on_xxx 回调。

### Fixed

- 修复 AppID / AppSecret 为 None、数字或空字符串时直接请求导致 appid invalid 的问题，现在入口会提前抛出 TypeError。
- 修复运行中按 Ctrl+C 抛出长串 KeyboardInterrupt 的问题，现在会打印退出信息。
- 修复外部调用 close 时 start 可能抛出 CancelledError 的问题。
- 修复 WebSocket 会话在关闭时可能未及时清理的问题。
- 修复 os.getenv 不会自动读取 .env 导致的 None 凭据问题，新增 load_env。
- 修复并校准事件表、Intents 位和 API 路径，使其对齐最新 API v2 文档。
