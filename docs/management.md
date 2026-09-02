# 面板与群管理

本文说明 SDK 提供的本地面板管理和群聊同步能力。

## 1. 群聊同步

### 自动初始化

Client 启动时会自动创建 groups.json：

    groups.json

默认路径为当前工作目录。也可以在创建 Client 时指定：

    bot = MyBot(
        intents=Intents.default(),
        group_store_path="data/groups.json",
        group_store_retention_days=30,
    )

参数说明：

- group_store_path：groups.json 路径，默认 ./groups.json。
- group_store_retention_days：退出群聊后，群记录保留天数，超过后自动删除，默认 30 天。

### 自动记录的事件

Client 内置自动记录以下事件：

- GROUP_ADD_ROBOT：机器人加入群聊时，写入群记录。
- GROUP_DEL_ROBOT：机器人退出群聊时，标记 active=false。
- GROUP_AT_MESSAGE_CREATE：群内有人 @ 机器人时，确保群记录存在。
- GROUP_MESSAGE_CREATE：群内产生消息时，确保群记录存在。

你不需要手动调用，SDK 会在调用你的 on_group_add_robot 等回调之前完成记录。

### groups.json 示例

    {
      "version": 1,
      "groups": {
        "群 OpenID": {
          "group_openid": "群 OpenID",
          "active": true,
          "added_at": "2026-08-30T12:00:00+00:00",
          "added_by": "操作者 OpenID",
          "last_seen": "2026-08-30T12:00:00+00:00",
          "name": "群名称"
        }
      }
    }

### 手动使用 GroupStore

    from viseron_qqbotpy import GroupStore, load_group_store

    store = load_group_store("groups.json")

    store.add_group("群 OpenID")
    store.ensure_group("群 OpenID")
    store.remove_group("群 OpenID")
    store.update_group_info("群 OpenID", {"name": "新群名"})

    active_groups = store.all_active_group_openids()

## 2. 指令面板管理

### 底层 API 和高层 API

底层 API 仍然可用：

- create_panel
- get_panel
- update_panel
- delete_panel
- update_panel_target

高层 API 提供：

- Panel：单个面板对象。
- PanelStore：本地配置和平台面板同步。
- load_panels：创建并加载 PanelStore。

### 本地文件

    panels/
      panels.json     # 你维护的面板配置
      store.json      # SDK 自动维护的 panel_id 映射

### 配置结构

panels.json 按 scope 分组。每个 scope 可以是一个对象，也可以是一个数组。

全局面板示例：

    {
      "group": {
        "target_type": "all",
        "remark": "群聊默认面板",
        "items": [
          {
            "type": "command",
            "name": "签到",
            "desc": "每日签到"
          }
        ]
      }
    }

特定群面板示例：

    {
      "group": {
        "key": "vip",
        "target_type": "specific",
        "remark": "VIP 群面板",
        "group_openids": ["群1", "群2"],
        "items": [
          {
            "type": "command",
            "name": "帮助",
            "desc": "查看帮助"
          }
        ]
      }
    }

每群一个面板示例：

    {
      "group": [
        {
          "key": "group_001",
          "target_type": "specific",
          "group_openids": ["群1"],
          "remark": "群1专用面板",
          "items": []
        },
        {
          "key": "group_002",
          "target_type": "specific",
          "group_openids": ["群2"],
          "remark": "群2专用面板",
          "items": []
        }
      ]
    }

### 启动同步

在 Client.on_ready 或启动逻辑中执行：

    from viseron_qqbotpy import load_panels


    class MyBot(Client):
        async def on_ready(self):
            store = await load_panels(self.api, root_dir="panels")
            await store.sync_from_config()

sync_from_config 会：

- 根据 store.json 中保存的 panel_id 查找面板。
- 找不到时按 scope + target_type + remark 匹配已有面板。
- 仍找不到时创建新面板并保存 panel_id。
- 如果本地 items 或 remark 与平台不一致，则更新面板。
- 如果 target_type 为 specific，则同步 user_openids 和 group_openids。

### 手动使用 Panel

    from viseron_qqbotpy import Panel

    # 创建
    panel = await Panel.create(
        self.api,
        scope="group",
        target_type="specific",
        group_openids=["群 OpenID"],
        remark="功能面板",
    )

    # 添加指令和链接
    panel.add_command("签到", desc="每日签到")
    panel.add_link("官网", desc="打开官网", url="https://example.com")

    # 保存
    await panel.save()

    # 查询
    panel = await Panel.get(self.api, panel_id=panel.panel_id)

    # 增删关联对象
    await panel.add_targets(groups=["新群 OpenID"])
    await panel.remove_targets(groups=["旧群 OpenID"])

    # 删除
    await panel.delete()
