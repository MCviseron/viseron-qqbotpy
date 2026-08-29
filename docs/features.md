# 功能实现指南

本文档说明如何使用 SDK 实现常见功能。每个示例都包含：

- 功能说明：这个接口做什么。
- 参数来源：需要的 ID 或数据从哪里获取。
- 示例代码：可以直接复制后替换实际 ID。
- 返回内容或注意事项。

除特殊说明外，示例都假设代码写在 Client 子类中，因此可以直接使用 self.api 调用接口。

## 1. 频道消息

频道消息指 QQ 频道内子频道的消息。机器人发送消息前通常需要连接 WebSocket 网关并保持在线。

### 1.1 回复 @ 消息

功能说明：当有人在频道子频道中 @ 机器人时，平台会推送 AT_MESSAGE_CREATE 事件。SDK 会把它转换为 on_at_message_create 回调，并传入 Message 对象。这里演示在事件中直接回复该消息。

参数来源：

- message.channel_id：事件中的子频道 ID。
- message.id：事件中的消息 ID。
- 这些信息由 SDK 自动填充，reply 方法内部会使用它们。

示例：

    from viseron_qqbotpy import Client, Intents, Message


    class MyBot(Client):
        async def on_at_message_create(self, message: Message):
            # message 就是用户 @ 机器人的那条频道消息
            await message.reply(content="收到你的消息")


    bot = MyBot(intents=Intents.default())
    bot.run(appid="AppID", secret="AppSecret")

注意：必须订阅 public_guild_messages，Intents.default() 已经包含该事件。

### 1.2 主动发送消息

功能说明：不依赖用户消息，主动向某个子频道发送一条文本消息。

参数来源：

- channel_id：目标子频道 ID。可以从 on_at_message_create 事件的 message.channel_id 获取，也可以从 get_channels 返回的子频道列表中获取。

示例：

    class MyBot(Client):
        async def on_ready(self):
            await self.api.post_message(
                channel_id="子频道 ID",
                content="主动消息",
            )

注意：主动消息有频率限制，未配置时默认每天每个子频道可推送 20 条。

### 1.3 发送 Markdown

功能说明：向频道子频道发送 Markdown 格式消息。Markdown 内容放在 markdown 参数的 content 字段中。

参数来源：

- channel_id：目标子频道 ID。
- markdown.content：要发送的 Markdown 文本。

示例：

    await self.api.post_message(
        channel_id="子频道 ID",
        markdown={"content": "# 标题
正文内容"},
    )

注意：填写 markdown 后，content 等文本字段应为空，避免消息内容冲突。

### 1.4 发送内嵌键盘

功能说明：在消息下方附带一个内嵌键盘，用户点击按钮后会触发互动事件。

参数来源：

- channel_id：目标子频道 ID。
- keyboard：键盘结构，包含 rows、buttons、render_data、action 等字段。
- action.data 是按钮点击后回传给机器人的数据。

示例：

    keyboard = {
        "content": {
            "rows": [
                {
                    "buttons": [
                        {
                            "id": "btn-1",
                            "render_data": {"label": "点我", "style": 1},
                            "action": {
                                "type": 2,
                                "data": "/hello",
                                "reply": True,
                                "enter": True,
                            },
                        }
                    ]
                }
            ]
        }
    }

    await self.api.post_message(
        channel_id="子频道 ID",
        content="请选择：",
        keyboard=keyboard,
    )

注意：按钮点击后会收到 INTERACTION_CREATE 事件，需要用 on_interaction_result 响应。

### 1.5 发送 Embed

功能说明：发送 Embed 结构化消息。Embed 是一种特殊的 Ark 消息，适合展示标题、描述和字段。

参数来源：

- channel_id：目标子频道 ID。
- embed：Embed 结构，包含 title、prompt、fields 等字段。

示例：

    embed = {
        "title": "标题",
        "prompt": "提示",
        "fields": [{"name": "字段内容"}],
    }

    await self.api.post_message(
        channel_id="子频道 ID",
        embed=embed,
    )

注意：embed、ark、markdown、content 等消息类型通常选择一种使用。

### 1.6 发送 Ark

功能说明：发送 Ark 模板消息。Ark 使用平台预设模板，通过 template_id 和 kv 键值对填充内容。

参数来源：

- channel_id：目标子频道 ID。
- ark.template_id：平台提供的 Ark 模板 ID。
- ark.kv：模板中的占位符和对应值。

示例：

    ark = {
        "template_id": 23,
        "kv": [
            {"key": "#TITLE#", "value": "标题"},
            {"key": "#DESC#", "value": "描述"},
        ],
    }

    await self.api.post_message(
        channel_id="子频道 ID",
        ark=ark,
    )

### 1.7 发送网络图片

功能说明：通过图片 URL 向子频道发送图片。平台会转存该图片。

参数来源：

- channel_id：目标子频道 ID。
- image：可公开访问的图片 URL。

示例：

    await self.api.post_message(
        channel_id="子频道 ID",
        image="https://example.com/image.png",
    )

### 1.8 发送本地图片

功能说明：上传本地图片文件并作为频道消息发送。

参数来源：

- channel_id：目标子频道 ID。
- file_image：本地图片路径，也可以是 bytes 或文件对象。

示例：

    await self.api.post_message(
        channel_id="子频道 ID",
        file_image="D:/images/test.png",
    )

也可以先读成 bytes 再发送：

    with open("test.png", "rb") as f:
        data = f.read()

    await self.api.post_message(
        channel_id="子频道 ID",
        file_image=data,
    )

注意：file_image 会使用 multipart/form-data 上传，不要与 image 同时使用。

### 1.9 引用回复

功能说明：发送一条引用某条历史消息的回复。回复消息下方会展示被引用消息。

参数来源：

- channel_id：目标子频道 ID。
- message_reference.message_id：被引用的消息 ID，可以从事件 message.id 或消息发送接口返回结果中获取。

示例：

    await self.api.post_message(
        channel_id="子频道 ID",
        content="这是引用回复",
        message_reference={"message_id": "被引用的消息 ID"},
    )

### 1.10 撤回消息

功能说明：撤回指定子频道中的一条消息。管理员可以撤回普通成员消息，频道主可以撤回所有人消息。

参数来源：

- channel_id：消息所在子频道 ID。
- message_id：要撤回的消息 ID。
- hidetip：是否隐藏撤回提示小灰条。

示例：

    await self.api.recall_message(
        channel_id="子频道 ID",
        message_id="消息 ID",
        hidetip=False,
    )

### 1.11 获取指定消息

功能说明：根据消息 ID，从指定子频道中查询单条频道消息的详情。这个接口用于获取某条已知消息的内容、作者、附件、时间等信息，而不是获取消息列表。

参数来源：

- channel_id：消息所在的子频道 ID。通常来自事件对象 message.channel_id，或子频道列表中某个子频道的 id。
- message_id：要查询的消息 ID。通常来自事件对象 message.id，或发送消息接口返回结果中的 id 字段。

示例：

    message = await self.api.get_message(
        channel_id="子频道 ID",
        message_id="消息 ID",
    )
    print(message)

返回内容：返回一个 Message 结构，常见字段包括 id、channel_id、guild_id、content、author、attachments、timestamp 等。

注意：该接口只查询单条消息，不是获取整个子频道的消息列表。QQ 机器人平台没有开放通用的历史消息列表拉取接口，因此需要先知道具体的 message_id。

## 2. 私信

私信是用户与机器人之间的一对一会话。机器人不能主动向任意用户发起私信，必须先有来源频道和用户 ID，创建私信会话后才能发送。

### 2.1 创建私信会话

功能说明：根据来源频道和用户 ID 创建私信会话，返回的 guild_id 就是后续发送私信时使用的会话 ID。

参数来源：

- guild_id：用户来源频道 ID。
- user_id：要私信的用户 ID。通常来自频道成员事件或消息事件中的 author.id。

示例：

    dms = await self.api.create_dms(
        guild_id="频道 ID",
        user_id="用户 ID",
    )
    print(dms)

返回内容：返回私信会话信息，其中 guild_id 字段用于 post_dms。

### 2.2 发送私信

功能说明：向已经创建好的私信会话发送消息。

参数来源：

- guild_id：私信会话 ID，来自 create_dms 返回结果中的 guild_id。
- content：消息内容。

示例：

    await self.api.post_dms(
        guild_id="私信会话 ID",
        content="你好",
    )

### 2.3 回复私信事件

功能说明：收到用户私信时，平台推送 DIRECT_MESSAGE_CREATE 事件。SDK 会传入 DirectMessage 对象，可直接使用 reply 回复。

参数来源：

- 事件对象内部已经包含 guild_id 和 message_id，reply 方法会自动使用。

示例：

    from viseron_qqbotpy import DirectMessage


    class MyBot(Client):
        async def on_direct_message_create(self, message: DirectMessage):
            await message.reply(content="已收到私信")

## 3. 群聊消息与单聊消息

群聊消息发送到群 OpenID，单聊消息发送到用户 OpenID。群和单聊中的用户标识与频道中的用户 ID 体系不同。

### 3.1 回复群 @ 消息

功能说明：当有人在群里 @ 机器人时，平台推送 GROUP_AT_MESSAGE_CREATE 事件。SDK 会传入 GroupMessage 对象，可直接回复。

参数来源：

- message.group_openid：事件中的群 OpenID。
- message.id：事件中的消息 ID。
- reply 方法会自动使用这些信息。

示例：

    from viseron_qqbotpy import GroupMessage


    class MyBot(Client):
        async def on_group_at_message_create(self, message: GroupMessage):
            await message.reply(content="收到群消息")

注意：需要订阅 group_and_c2c_event，Intents.default() 已包含。

### 3.2 主动发送群消息

功能说明：主动向指定群发送文本消息。

参数来源：

- group_openid：目标群 OpenID。可以从群事件 message.group_openid 获取，也可以从群管理接口返回中获取。
- msg_type：消息类型，0 表示纯文本。

示例：

    await self.api.post_group_message(
        group_openid="群 OpenID",
        msg_type=0,
        content="大家好",
    )

### 3.3 发送群 Markdown

功能说明：向指定群发送 Markdown 消息。

参数来源：

- group_openid：目标群 OpenID。
- msg_type：2 表示 Markdown。
- markdown.content：Markdown 内容。

示例：

    await self.api.post_group_message(
        group_openid="群 OpenID",
        msg_type=2,
        markdown={"content": "# 标题
正文"},
    )

### 3.4 撤回群消息

功能说明：撤回指定群中的一条消息。

参数来源：

- group_openid：消息所在群 OpenID。
- message_id：要撤回的消息 ID。

示例：

    await self.api.recall_group_message(
        group_openid="群 OpenID",
        message_id="消息 ID",
    )

### 3.5 回复单聊消息

功能说明：用户与机器人单聊时，平台推送 C2C_MESSAGE_CREATE 事件。SDK 会传入 C2CMessage 对象，可直接回复。

参数来源：

- message.author.user_openid：事件中的用户 OpenID。
- message.id：事件中的消息 ID。
- reply 方法会自动使用这些信息。

示例：

    from viseron_qqbotpy import C2CMessage


    class MyBot(Client):
        async def on_c2c_message_create(self, message: C2CMessage):
            await message.reply(content="已收到单聊消息")

### 3.6 主动发送单聊消息

功能说明：主动向指定用户发送单聊消息。

参数来源：

- openid：目标用户的 user_openid。可以从 C2C_MESSAGE_CREATE 事件的 message.author.user_openid 获取。
- msg_type：0 表示纯文本。

示例：

    await self.api.post_c2c_message(
        openid="用户 OpenID",
        msg_type=0,
        content="你好",
    )

### 3.7 撤回单聊消息

功能说明：撤回发送给指定用户的一条单聊消息。

参数来源：

- openid：用户 OpenID。
- message_id：要撤回的消息 ID。

示例：

    await self.api.recall_c2c_message(
        openid="用户 OpenID",
        message_id="消息 ID",
    )

## 4. 表情表态

表情表态是对频道消息添加或删除表情回应。

### 4.1 添加表情表态

功能说明：对指定子频道中的某条消息添加表情表态。

参数来源：

- channel_id：消息所在子频道 ID。
- message_id：要表态的消息 ID。
- emoji_type：表情类型，1 表示系统表情，2 表示 emoji 表情。
- emoji_id：表情 ID，参见平台表情列表。

示例：

    await self.api.put_reaction(
        channel_id="子频道 ID",
        message_id="消息 ID",
        emoji_type=1,
        emoji_id="表情 ID",
    )

### 4.2 删除表情表态

功能说明：删除指定消息上的某个表情表态。

参数来源：

- channel_id：消息所在子频道 ID。
- message_id：消息 ID。
- emoji_type：表情类型。
- emoji_id：表情 ID。

示例：

    await self.api.delete_reaction(
        channel_id="子频道 ID",
        message_id="消息 ID",
        emoji_type=1,
        emoji_id="表情 ID",
    )

### 4.3 获取表态用户列表

功能说明：获取对指定消息使用某个表情的用户列表。

参数来源：

- channel_id：消息所在子频道 ID。
- message_id：消息 ID。
- emoji_type 和 emoji_id：指定要查询的表情。
- limit：返回数量，1 到 100。

示例：

    result = await self.api.get_reaction_users(
        channel_id="子频道 ID",
        message_id="消息 ID",
        emoji_type=1,
        emoji_id="表情 ID",
        limit=20,
    )
    print(result)

返回内容：返回表态用户列表和分页 cookie 等信息。

## 5. 频道、子频道与权限

### 5.1 获取频道信息

功能说明：根据频道 ID 查询单个频道的详细信息，如名称、头像、所有者、成员数、描述等。

参数来源：

- guild_id：频道 ID。可以从事件对象 guild.id、message.guild_id 获取，也可以从 me_guilds 返回列表中获取。

示例：

    guild = await self.api.get_guild("频道 ID")

返回内容：返回 Guild 结构，包含 id、name、icon、owner_id、member_count 等字段。

### 5.2 获取我加入的频道列表

功能说明：查询当前机器人加入的所有频道。这是查找机器人所在频道 ID 的最常用方法。

参数来源：

- 无需额外参数，limit 控制返回数量。
- 如果频道数量很多，可传入 guild_id 作为分页游标。

示例：

    guilds = await self.api.me_guilds(limit=100)

返回内容：返回频道列表。列表中每个元素包含频道 ID 和名称，可用于后续频道相关操作。

### 5.3 获取子频道列表

功能说明：查询指定频道下的所有子频道。子频道是消息发送、日程、论坛等操作的 target。

参数来源：

- guild_id：频道 ID。来自 get_guild、me_guilds 或事件中的 guild_id。

示例：

    channels = await self.api.get_channels("频道 ID")

返回内容：返回子频道列表，每个子频道包含 id、name、type、sub_type 等字段。

### 5.4 创建子频道

功能说明：在指定频道下创建新的子频道。需要管理员权限。

参数来源：

- guild_id：目标频道 ID。
- name：新子频道名称。
- type：子频道类型。
- sub_type：子频道子类型。

示例：

    channel = await self.api.create_channel(
        guild_id="频道 ID",
        name="新子频道",
        type=0,
        sub_type=0,
    )

返回内容：返回创建后的子频道对象。

### 5.5 修改子频道

功能说明：修改指定子频道的名称、排序、分组、私密类型、发言权限等。

参数来源：

- channel_id：要修改的子频道 ID，来自 get_channels 或事件中的 channel.id。

示例：

    await self.api.update_channel(
        channel_id="子频道 ID",
        name="新名称",
    )

### 5.6 删除子频道

功能说明：删除指定子频道。

参数来源：

- channel_id：要删除的子频道 ID。

示例：

    await self.api.delete_channel("子频道 ID")

注意：删除后子频道中的消息和配置也会被移除，请谨慎操作。

### 5.7 子频道用户权限

功能说明：修改指定用户在某个子频道的权限，例如允许查看、发言、管理。

参数来源：

- channel_id：目标子频道 ID。
- user_id：目标用户 ID。
- add：要添加的权限，使用 Permission 对象。
- remove：要移除的权限，使用 Permission 对象。

示例：

    from viseron_qqbotpy import Permission

    add = Permission(view_permission=True, speak_permission=True)
    remove = Permission(manager_permission=True)

    await self.api.update_channel_user_permissions(
        channel_id="子频道 ID",
        user_id="用户 ID",
        add=add,
        remove=remove,
    )

## 6. 成员与身份组

### 6.1 获取成员

功能说明：查询指定频道中某个成员的详细信息。

参数来源：

- guild_id：频道 ID。
- user_id：成员用户 ID。通常来自消息事件中的 author.id，或成员列表中的 user.id。

示例：

    member = await self.api.get_guild_member(
        guild_id="频道 ID",
        user_id="用户 ID",
    )

返回内容：返回 Member 结构，包含 user、nick、roles、joined_at 等字段。

### 6.2 获取成员列表

功能说明：分页查询指定频道中的成员列表。

参数来源：

- guild_id：频道 ID。
- after：上一批返回的最后一个用户 ID，首次请求传 "0"。
- limit：每页数量，1 到 400。

示例：

    members = await self.api.get_guild_members(
        guild_id="频道 ID",
        after="0",
        limit=100,
    )

返回内容：返回成员列表。翻页时，将上一批最后一个成员的 user.id 作为下一次 after 参数。

### 6.3 删除成员

功能说明：把指定用户移出频道，可选择同时加入黑名单或撤回其历史消息。

参数来源：

- guild_id：频道 ID。
- user_id：要移除的用户 ID。
- add_blacklist：是否同时加入黑名单。
- delete_history_msg_days：撤回该成员消息的时间范围，可选 0、3、7、15、30、-1。

示例：

    await self.api.delete_guild_member(
        guild_id="频道 ID",
        user_id="用户 ID",
        add_blacklist=False,
        delete_history_msg_days=0,
    )

### 6.4 创建身份组

功能说明：在频道中创建身份组，用于管理成员权限和展示。

参数来源：

- guild_id：频道 ID。
- name：身份组名称。
- color：颜色值，可使用 ext.convert_color 转换。
- hoist：是否在成员列表中单独展示，0 否，1 是。

示例：

    role = await self.api.create_guild_role(
        guild_id="频道 ID",
        name="管理员",
        color=0,
        hoist=1,
    )

返回内容：返回创建后的身份组对象，包含 role_id。

### 6.5 修改身份组

功能说明：修改指定身份组的名称、颜色、是否单独展示等。

参数来源：

- guild_id：频道 ID。
- role_id：身份组 ID，来自 create_guild_role 返回结果或 get_guild_roles 列表。

示例：

    await self.api.update_guild_role(
        guild_id="频道 ID",
        role_id="身份组 ID",
        name="新名称",
    )

### 6.6 删除身份组

功能说明：删除频道中的指定身份组。

参数来源：

- guild_id：频道 ID。
- role_id：要删除的身份组 ID。

示例：

    await self.api.delete_guild_role(
        guild_id="频道 ID",
        role_id="身份组 ID",
    )

### 6.7 给成员添加身份组

功能说明：给指定成员添加身份组。

参数来源：

- guild_id：频道 ID。
- role_id：身份组 ID。
- user_id：成员用户 ID。
- channel_id：当身份组是子频道管理员时，需要指定具体子频道。

示例：

    await self.api.create_guild_role_member(
        guild_id="频道 ID",
        role_id="身份组 ID",
        user_id="用户 ID",
    )

### 6.8 移除成员身份组

功能说明：移除指定成员的某个身份组。

参数来源：

- guild_id：频道 ID。
- role_id：身份组 ID。
- user_id：成员用户 ID。

示例：

    await self.api.delete_guild_role_member(
        guild_id="频道 ID",
        role_id="身份组 ID",
        user_id="用户 ID",
    )

## 7. 禁言

### 7.1 全员禁言

功能说明：将频道内所有非管理员成员禁言。

参数来源：

- guild_id：频道 ID。
- mute_end_timestamp 和 mute_seconds 二选一，默认优先使用 mute_end_timestamp。

示例：

    await self.api.mute_all(
        guild_id="频道 ID",
        mute_seconds="60",
    )

### 7.2 取消全员禁言

功能说明：取消频道内所有成员的禁言状态。

参数来源：

- guild_id：频道 ID。

示例：

    await self.api.cancel_mute_all("频道 ID")

### 7.3 指定成员禁言

功能说明：禁言频道中的指定成员。

参数来源：

- guild_id：频道 ID。
- user_id：要禁言的成员用户 ID。
- mute_end_timestamp 和 mute_seconds 二选一。

示例：

    await self.api.mute_member(
        guild_id="频道 ID",
        user_id="用户 ID",
        mute_seconds="60",
    )

### 7.4 批量成员禁言

功能说明：一次禁言多个成员。

参数来源：

- guild_id：频道 ID。
- user_ids：要禁言的用户 ID 列表。

示例：

    await self.api.mute_multi_member(
        guild_id="频道 ID",
        user_ids=["用户1", "用户2"],
        mute_seconds="60",
    )

### 7.5 查询消息频率设置

功能说明：查询机器人在指定频道内的消息频率限制设置。

参数来源：

- guild_id：频道 ID。

示例：

    setting = await self.api.get_message_setting("频道 ID")
    print(setting)

返回内容：返回 disable_create_dm、disable_push_msg、channel_ids、channel_push_max_num 等配置。

## 8. 日程、论坛、精华、公告

### 8.1 创建日程

功能说明：在日程子频道中创建一条日程。

参数来源：

- channel_id：日程子频道 ID。
- name：日程名称。
- start_timestamp 和 end_timestamp：开始和结束时间戳，单位毫秒。
- jump_channel_id：日程开始后要跳转的子频道 ID。
- remind_type：提醒类型，如 0 无提醒，1 为 5 分钟前。

示例：

    schedule = await self.api.create_schedule(
        channel_id="日程子频道 ID",
        name="会议",
        start_timestamp="1700000000000",
        end_timestamp="1700003600000",
        jump_channel_id="跳转子频道 ID",
        remind_type="1",
    )

返回内容：返回创建后的日程对象，包含 schedule_id。

### 8.2 获取日程列表

功能说明：获取指定日程子频道中当天的日程列表，也可以传入 since 获取该时间之后的日程。

参数来源：

- channel_id：日程子频道 ID。
- since：可选，返回结束时间在 since 之后的日程。

示例：

    schedules = await self.api.get_schedules("日程子频道 ID")

### 8.3 修改日程

功能说明：修改指定日程的名称、时间、跳转子频道或提醒类型。

参数来源：

- channel_id：日程所在子频道 ID。
- schedule_id：日程 ID，来自创建日程返回结果或日程列表。
- 其他参数与创建日程相同。

示例：

    await self.api.update_schedule(
        channel_id="日程子频道 ID",
        schedule_id="日程 ID",
        name="新会议",
        start_timestamp="1700000000000",
        end_timestamp="1700003600000",
        jump_channel_id="跳转子频道 ID",
        remind_type="2",
    )

### 8.4 删除日程

功能说明：删除指定日程。

参数来源：

- channel_id：日程所在子频道 ID。
- schedule_id：要删除的日程 ID。

示例：

    await self.api.delete_schedule(
        channel_id="日程子频道 ID",
        schedule_id="日程 ID",
    )

### 8.5 发表帖子

功能说明：在论坛子频道中发表一个帖子。

参数来源：

- channel_id：论坛子频道 ID。
- title：帖子标题。
- content：帖子内容。
- format：内容格式。

示例：

    result = await self.api.post_thread(
        channel_id="论坛子频道 ID",
        title="帖子标题",
        content="帖子内容",
        format=1,
    )

返回内容：返回发表结果，其中包含帖子 ID。

### 8.6 获取帖子列表

功能说明：获取指定论坛子频道下的帖子列表。

参数来源：

- channel_id：论坛子频道 ID。

示例：

    threads = await self.api.get_threads("论坛子频道 ID")

### 8.7 删除帖子

功能说明：删除论坛子频道中的指定帖子。

参数来源：

- channel_id：论坛子频道 ID。
- thread_id：要删除的帖子 ID。

示例：

    await self.api.delete_thread(
        channel_id="论坛子频道 ID",
        thread_id="帖子 ID",
    )

### 8.8 添加精华消息

功能说明：把子频道中的一条消息设为精华消息。

参数来源：

- channel_id：消息所在子频道 ID。
- message_id：要设为精华的消息 ID。

示例：

    result = await self.api.put_pin(
        channel_id="子频道 ID",
        message_id="消息 ID",
    )

返回内容：返回当前子频道内所有精华消息 ID 列表。

### 8.9 获取精华消息

功能说明：获取指定子频道内的所有精华消息。

参数来源：

- channel_id：子频道 ID。

示例：

    pins = await self.api.get_pins("子频道 ID")

### 8.10 删除精华消息

功能说明：删除子频道中的指定精华消息。

参数来源：

- channel_id：子频道 ID。
- message_id：要删除的精华消息 ID。传 "all" 可删除全部精华消息。

示例：

    await self.api.delete_pin(
        channel_id="子频道 ID",
        message_id="消息 ID",
    )

### 8.11 创建频道公告

功能说明：把某个子频道中的一条消息设置为频道公告。

参数来源：

- guild_id：频道 ID。
- channel_id：消息所在子频道 ID。
- message_id：要设为公告的消息 ID。

示例：

    await self.api.create_announce(
        guild_id="频道 ID",
        channel_id="子频道 ID",
        message_id="消息 ID",
    )

### 8.12 删除频道公告

功能说明：删除频道公告。

参数来源：

- guild_id：频道 ID。
- message_id：要删除的公告消息 ID。传 "all" 删除全部公告。

示例：

    await self.api.delete_announce(
        guild_id="频道 ID",
        message_id="all",
    )

## 9. 音频控制

### 9.1 音频控制

功能说明：控制语音子频道中的音频播放状态。

参数来源：

- channel_id：语音子频道 ID。
- audio_control：音频控制参数，包括 audio_url、text、status 等。

示例：

    await self.api.update_audio(
        channel_id="语音子频道 ID",
        audio_control={"audio_url": "音频地址", "text": "状态文本", "status": 1},
    )

### 9.2 机器人上麦

功能说明：让机器人在指定语音子频道上麦。

参数来源：

- channel_id：语音子频道 ID。

示例：

    await self.api.on_microphone("语音子频道 ID")

### 9.3 机器人下麦

功能说明：让机器人在指定语音子频道下麦。

参数来源：

- channel_id：语音子频道 ID。

示例：

    await self.api.off_microphone("语音子频道 ID")

## 10. 群管理与入群审批

### 10.1 获取群基本信息

功能说明：查询指定群的基本信息。

参数来源：

- group_openid：群 OpenID。来自群事件的 message.group_openid，或群列表相关接口。

示例：

    info = await self.api.get_group_info("群 OpenID")

返回内容：返回群名称、群号、机器人状态等基本信息。

### 10.2 获取机器人群内状态

功能说明：查询机器人在指定群内的状态，例如是否被禁言、是否允许主动消息等。

参数来源：

- group_openid：群 OpenID。

示例：

    state = await self.api.get_group_bot_state("群 OpenID")

### 10.3 拉取入群申请列表

功能说明：拉取指定群的入群申请记录，用于后续审批。

参数来源：

- group_openid：群 OpenID。
- cursor：分页游标，首次请求可省略。
- limit：返回数量。

示例：

    result = await self.api.get_group_join_request_list(
        group_openid="群 OpenID",
        limit=10,
    )

返回内容：返回入群申请列表和分页游标。每条申请包含 member_openid 和 join_request_id，用于审批接口。

### 10.4 审批入群申请

功能说明：同意或拒绝指定群成员的入群申请。

参数来源：

- group_openid：群 OpenID。
- member_openid：申请成员的 member_openid，来自入群申请列表。
- op：审批操作，如 approve 或 reject。
- join_request_id：申请 ID，来自入群申请列表。
- reject_reason：拒绝原因，拒绝时使用。
- add_to_member_blacklist：拒绝时是否加入成员黑名单。

示例：

    await self.api.approve_group_join_request(
        group_openid="群 OpenID",
        member_openid="申请成员 OpenID",
        op="approve",
        join_request_id="申请 ID",
    )

### 10.5 设置群成员禁言

功能说明：对群成员进行禁言或解除禁言。

参数来源：

- group_openid：群 OpenID。
- members：需要操作的成员列表，每项包含 op、member_openid、mute_expire_at 等字段。
- op 可选 add、update、del。
  - add：增加禁言
  - update：更新禁言到期时间
  - del：解除禁言
- member_openid 是群成员 OpenID，不是 user_openid。
- mute_expire_at 使用 RFC3339 时间格式。

示例：

    members = [
        {
            "op": "add",
            "member_openid": "成员 OpenID",
            "mute_expire_at": "2026-08-29T12:00:00+08:00",
        }
    ]

    await self.api.set_group_restrict_chat_setting(
        group_openid="群 OpenID",
        members=members,
    )

### 10.6 查询群禁言状态

功能说明：查询指定群的禁言设置状态。

参数来源：

- group_openid：群 OpenID。

示例：

    setting = await self.api.get_group_restrict_chat_setting("群 OpenID")
    print(setting)

### 10.7 入群自动审批策略

功能说明：管理入群自动审批策略，包括查询、创建、修改、执行、删除。

参数来源：

- group_openids：策略作用的群 OpenID 列表。
- strategy_id：策略 ID，来自策略列表或创建结果。

示例：

    # 查询策略
    strategies = await self.api.get_group_join_approval_strategies()

    # 创建策略
    strategy = await self.api.create_group_join_approval_strategy(
        group_openids=["群 OpenID"],
        is_enable="1",
        remark="自动审批",
    )

    # 修改策略
    await self.api.update_group_join_approval_strategy(
        strategy_id="策略 ID",
        is_enable="0",
    )

    # 执行策略
    await self.api.execute_group_join_approval_strategy("策略 ID")

    # 删除策略
    await self.api.delete_group_join_approval_strategy("策略 ID")

## 11. 富媒体上传

富媒体上传用于向群聊或单聊发送图片、视频、语音等文件。完整流程通常包括预上传、分片上传、最后调用 files 接口发送。

### 11.1 群聊富媒体预上传

功能说明：向平台申请群聊富媒体上传任务，获取 upload_id 和分片上传信息。

参数来源：

- group_id：群 ID，不是 group_openid。
- file_type：媒体类型，1 图片，2 视频，3 语音。
- file_size：文件大小字符串。
- file_name：文件名。
- md5、sha1、md5_10m：文件的校验值，用于平台校验文件完整性。

示例：

    prepare = await self.api.post_group_upload_prepare(
        group_id="群 ID",
        file_type=1,
        file_size="12345",
        file_name="image.png",
        md5="文件 MD5",
        sha1="文件 SHA1",
        md5_10m="分片 MD5",
    )

返回内容：返回 upload_id、分片大小和上传地址等信息。

### 11.2 群聊分片上传完成

功能说明：上传完某个分片后，通知平台完成该分片。

参数来源：

- group_id：群 ID。
- upload_id：预上传返回的上传 ID。
- part_index：分片序号。
- block_size：分片大小。
- md5：分片 MD5。

示例：

    await self.api.post_group_upload_part_finish(
        group_id="群 ID",
        upload_id="上传 ID",
        part_index=1,
        block_size="12345",
        md5="分片 MD5",
    )

### 11.3 群聊富媒体上传

功能说明：使用已经上传好的资源 URL，向群聊发送富媒体消息。

参数来源：

- group_openid：目标群 OpenID。
- file_type：媒体类型。
- url：资源 URL。
- srv_send_msg：为 True 时直接发送消息，会占用主动消息频次。
- upload_id 和 file_name：可选，与上传任务关联。

示例：

    await self.api.post_group_file(
        group_openid="群 OpenID",
        file_type=1,
        url="资源 URL",
        srv_send_msg=False,
    )

### 11.4 单聊富媒体预上传

功能说明：向平台申请单聊富媒体上传任务。

参数来源：

- user_id：目标用户 ID，注意这里不是 user_openid。
- 其他参数与群聊预上传相同。

示例：

    await self.api.post_c2c_upload_prepare(
        user_id="用户 ID",
        file_type=1,
        file_size="12345",
        file_name="image.png",
        md5="文件 MD5",
        sha1="文件 SHA1",
        md5_10m="分片 MD5",
    )

### 11.5 单聊分片上传完成

功能说明：通知平台完成单聊富媒体的某个分片上传。

参数来源：

- user_id：目标用户 ID。
- upload_id：预上传返回的上传 ID。
- part_index：分片序号。
- block_size：分片大小。
- md5：分片 MD5。

示例：

    await self.api.post_c2c_upload_part_finish(
        user_id="用户 ID",
        upload_id="上传 ID",
        part_index=1,
        block_size="12345",
        md5="分片 MD5",
    )

### 11.6 单聊富媒体上传

功能说明：使用已经上传好的资源 URL，向用户发送单聊富媒体消息。

参数来源：

- openid：目标用户的 user_openid。
- file_type：媒体类型。
- url：资源 URL。
- srv_send_msg：为 True 时直接发送消息。

示例：

    await self.api.post_c2c_file(
        openid="用户 OpenID",
        file_type=1,
        url="资源 URL",
        srv_send_msg=False,
    )

## 12. 自定义菜单与指令面板

### 12.1 查询全局自定义菜单

功能说明：查询机器人当前的全局自定义菜单配置。

参数来源：

- 无需额外参数。

示例：

    menu = await self.api.get_menu()

返回内容：返回菜单结构，包含 items 等字段。

### 12.2 修改全局自定义菜单

功能说明：设置或更新机器人的全局自定义菜单。

参数来源：

- menu：菜单结构，包含 items 列表。每个 item 可配置名称、类型、发送内容或跳转链接。

示例：

    menu = {
        "items": [
            {
                "name": "帮助",
                "type": "send_message",
                "send_message": "帮助内容",
            }
        ]
    }

    await self.api.update_menu(menu)

### 12.3 查询指令面板列表

功能说明：查询已创建的指令面板列表。

参数来源：

- 无需额外参数。

示例：

    panels = await self.api.get_panels()

返回内容：返回指令面板列表，每个面板包含 panel_id。

### 12.4 创建指令面板

功能说明：创建新的指令面板，可指定作用范围和目标对象。

参数来源：

- scope：作用范围，如 group。
- target_type：目标类型，如 group。
- group_openids 或 user_openids：面板关联的群或用户。
- panel：面板内容，包含 items 列表。

示例：

    panel = await self.api.create_panel(
        scope="group",
        target_type="group",
        group_openids=["群 OpenID"],
        panel={
            "items": [
                {
                    "name": "签到",
                    "desc": "每日签到",
                    "type": "send_message",
                    "only_admin": False,
                }
            ]
        },
    )

返回内容：返回创建后的面板对象，包含 panel_id。

### 12.5 修改指令面板

功能说明：修改指定指令面板的内容。

参数来源：

- panel_id：面板 ID，来自面板列表或创建结果。
- panel：新的面板内容。

示例：

    await self.api.update_panel(
        panel_id="面板 ID",
        panel={"items": []},
    )

### 12.6 删除指令面板

功能说明：删除指定指令面板。

参数来源：

- panel_id：要删除的面板 ID。

示例：

    await self.api.delete_panel("面板 ID")

## 13. 分享链接

功能说明：生成一个 QQ 机器人分享链接，可用于引导用户添加机器人或进入会话。

参数来源：

- url_link：要生成的链接地址。

示例：

    result = await self.api.create_url_link("https://example.com")
    print(result)

返回内容：返回生成后的分享链接或链接 ID。

## 14. 互动事件响应

功能说明：用户点击消息按钮等互动操作后，平台推送 INTERACTION_CREATE 事件。机器人需要调用响应接口告知平台处理结果，否则用户侧可能一直等待。

参数来源：

- interaction.id：互动事件 ID，来自 Interaction 对象的 id 字段。
- code：处理结果，0 成功，1 操作失败，2 操作频繁，3 重复操作，4 没有权限，5 仅管理员操作。

示例：

    from viseron_qqbotpy import Interaction


    class MyBot(Client):
        async def on_interaction_create(self, interaction: Interaction):
            await self.api.on_interaction_result(
                interaction_id=interaction.id,
                code=0,
            )
