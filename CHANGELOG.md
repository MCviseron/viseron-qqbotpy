# Changelog

本项目的所有重要变更都会记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added

- 暂无。

## [0.4.2] - 2026-11-13

### Added

- 新增 docs/automation.md：QQ 文档同步自动化任务定义、任务卡字段、版本规则和验收标准。
- docs/publish.md 增加完整手动发布流程，覆盖 ChatClone-BotPy 环境、测试、构建、twine 检查、TestPyPI、PyPI、发布后验证和 tag 推送。
- README 与 docs/README.md 增加自动化任务文档入口。
- 新增 GitHub Actions 自动发布（Trusted Publishing / OIDC，无需在仓库保存任何 API Token）：
  `.github/workflows/publish-testpypi.yml`（推 main 或手动触发发 TestPyPI）与
  `.github/workflows/publish-pypi.yml`（推 `v*` tag 自动发正式 PyPI），
  两者都先跑 pytest、版本一致性检查、build、twine check，再交给 pypa/gh-action-pypi-publish 上传。
- 新增 `scripts/check_release.py`：校验 pyproject 与 __init__ 版本一致、版本号无本地标记、
  tag 必须等于 `v<version>`；CI 与本地共用。
- docs/publish.md 新增第 9 节，说明 Trusted Publishing 原理、两个 workflow、
  PyPI / TestPyPI 的 pending publisher 四个字段、推荐发布流程与常见失败。

## [0.4.1] - 2026-10-31

### Added

- 对齐平台文档 2026-10-28 新增的图文卡片消息：post_group_message / post_c2c_message 新增 card 参数，配合 msg_type=8 使用；卡片结构为 {"type": "tuwen", "content": {title, description, url, pic_url}}。
- 对齐平台文档 2026-10-26 新增的群聊 @全部成员：新增常量 AT_EVERYONE（值 `<qqbot-at-everyone />`），放进文本消息的 content 或 Markdown 消息的 markdown.content 即可 @全部成员。
- types 新增 MessageCard、MessageCardContent 类型提示，并从主包导出 AT_EVERYONE。
- 新增 tests/test_message_card.py：6 个离线测试，覆盖群聊/单聊卡片请求体、card 缺省时不发送、AT_EVERYONE 常量值，以及文本与 Markdown 中的 @全部成员透传。

### Changed

- docs/api-reference.md 第 8、9 节补充 msg_type 取值（新增 8=图文卡片）与 card 参数。
- docs/features.md 新增 3.8 发送图文卡片、3.9 @全部成员。
- docs/core.md 类型辅助章节补充 MessageCard / MessageCardContent / AT_EVERYONE。
- README 特性列表补充图文卡片与 @全部成员一行。
- 版本号提升到 0.4.1（pyproject.toml 与 __init__.py）。

## [0.4.0] - 2026-10-24

### Added

- 对齐平台文档 2026-10-21 新增的素材管理接口：prepare_media_image（申请上传，返回 upload_id / presigned_url / expires_in）、complete_media_image（完成上传，返回 image_id / url / ttl / preview_url）、get_media_images（分页查询有效图片）、delete_media_image（删除图片并释放配额）。
- 新增 put_presigned_image：向预签名地址直传图片二进制并返回 ETag，Content-Type 与 prepare 声明保持一致。
- 新增 upload_markdown_image：一步完成 prepare → PUT → complete，直接返回 complete 结果（含 qqbot-media:// 引用）。
- 新增 guess_image_content_type：按扩展名推断 png / jpeg / gif / webp 的 MIME 类型，未知扩展名抛 ValueError。
- types 新增 MediaImagePrepare、MediaImageComplete、MediaImage、MediaImageList 类型提示。
- 新增 tests/test_media_api.py：14 个离线测试，覆盖四个接口的路径与请求体、MIME 推断、以及 upload_markdown_image 的三步流程（PUT 用桩替换，不联网）。

### Changed

- docs/api-reference.md 新增第 13 节「素材管理（Markdown 图片）」，原错误类型章节顺延为第 14 节。
- docs/features.md 新增第 15 节素材管理，含一键上传、Markdown 引用、分步调用、查询与删除。
- docs/core.md 的类型辅助章节补充 4 个素材管理 TypedDict。
- README 特性列表补充 Markdown 素材管理一行。
- 版本号统一提升到 0.4.0（pyproject.toml 与 __init__.py）。

## [0.3.0] - 2026-10-01

### Added

- 新增 upload_group_media：封装群聊富媒体分片上传完整流程，依次完成预上传、分片 PUT、分片完成和文件合并，调用后直接返回 files 接口结果。
- 新增 upload_c2c_media：封装单聊富媒体分片上传完整流程，调用后直接返回 files 接口结果。
- 新增 Panel / PanelItem：面向对象的指令面板封装，支持创建、查询、增删指令与链接、保存、关联对象增删、刷新和删除。
- 新增 PanelStore / load_panels：以本地 panels/panels.json 为配置源把面板同步到平台，并用 panels/store.json 记录 scope:key 与 panel_id 的映射。
- 新增 GroupStore / load_group_store：本地群聊状态管理，把机器人加入过的群记录到 groups.json，并在启动时清理超期记录。
- Client 新增 group_store_path 和 group_store_retention_days 参数，用于自动管理 groups.json。
- Client 自动记录群事件：GROUP_ADD_ROBOT、GROUP_DEL_ROBOT、GROUP_AT_MESSAGE_CREATE、GROUP_MESSAGE_CREATE 会在回调触发前写入 groups.json。
- Client 在群记录缺少群名称等资料时，自动调用 get_group_info 补全群信息。
- 新增 docs/management.md，说明面板与群管理、本地配置同步。
- 新增 tests/test_panel.py 和 tests/test_group_store.py。
- post_group_file / post_c2c_file 的 url 参数改为可选，支持分片上传合并场景。
- 对齐平台文档 2026-09-03 新增的群成员管理接口：get_group_members（获取群成员列表，每页最多 30 条）、get_group_member（获取群成员信息）、batch_remove_group_members（群成员批量移除，单次最多 20 个）、get_group_member_blacklist（群黑名单查询）、update_group_member_blacklist（群黑名单操作，op 取 add / del）。
- types 新增 GroupMember、GroupMemberList、GroupBlacklistUser、GroupMemberBlacklist、GroupMuteRule、GroupMuteScheduleRule、GroupMuteRecurringRule、GroupMemberMuteState、GroupRestrictChatSetting 类型提示。
- 新增 tests/test_group_api.py：离线校验群成员管理与分享链接接口的路径、方法、参数与请求体。

### Changed

- upload_group_media 参数简化为只传 group_openid，upload_c2c_media 参数简化为只传 user_openid。
- get_panels 改为必传 scope，按场景查询指令面板列表。
- load_panels 只加载本地状态，不再自动同步平台；需要创建或更新平台面板时必须显式调用 sync_from_config。
- GroupStore.update_group_info 直接保存平台返回的完整群信息，不再额外生成重复的别名字段。
- groups.json 的时间字段统一使用 UTC+8 时区。
- docs/features.md 补充本地文件分片上传封装和面板高层用法，并修正指令面板示例的 target_type 与 items.type 取值，与 Panel 高层 API 保持一致。
- 对齐平台文档 2026-09-16 的字段修正：create_url_link 的请求字段由 url_link 改为 callback_data（最长 32 字符），响应结构为 {"data": {"url": ...}}；url_link 保留为已废弃的兼容别名。
- docs/features.md 新增 10.8-10.12 群成员管理与群黑名单用法，并重写第 13 节分享链接。
- docs/api-reference.md 第 10 节补充群成员管理接口，第 11 节更新 create_url_link 签名。

### Fixed

- 修复 get_panels 不传 scope 时查询结果不符合预期的问题，现在缺少 scope 会直接报错。
- 修复 groups.json 中群信息存在重复别名字段的问题。
- 修复 create_url_link 发送了平台不存在的 url_link 字段的问题，现在按文档发送 callback_data。
- 修复 pyproject.toml 版本号停留在 0.2.0、与 viseron_qqbotpy.__version__ 不一致的问题，两者统一为 0.3.0。

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
