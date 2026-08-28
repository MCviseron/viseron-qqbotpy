# 事件监听

SDK 通过 WebSocket 接收事件。事件类型会转换为小写，并在前面加上 on_，作为 Client 的回调方法名。

例如：

- GUILD_CREATE -> on_guild_create
- AT_MESSAGE_CREATE -> on_at_message_create
- GROUP_MEMBER_ADD -> on_group_member_add

你只需要在 Client 子类中定义同名异步方法即可。

## 1. 完整事件表

频道与子频道：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| GUILD_CREATE | 机器人加入新频道 | on_guild_create | Guild |
| GUILD_UPDATE | 频道资料发生变更 | on_guild_update | Guild |
| GUILD_DELETE | 机器人退出频道或频道解散 | on_guild_delete | Guild |
| CHANNEL_CREATE | 子频道被创建 | on_channel_create | Channel |
| CHANNEL_UPDATE | 子频道资料发生变更 | on_channel_update | Channel |
| CHANNEL_DELETE | 子频道被删除 | on_channel_delete | Channel |

频道成员：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| GUILD_MEMBER_ADD | 新成员加入频道 | on_guild_member_add | Member |
| GUILD_MEMBER_UPDATE | 频道成员资料发生变更 | on_guild_member_update | Member |
| GUILD_MEMBER_REMOVE | 成员退出频道或被移出频道 | on_guild_member_remove | Member |

频道消息：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| AT_MESSAGE_CREATE | 频道中有人 @ 机器人 | on_at_message_create | Message |
| PUBLIC_MESSAGE_DELETE | 公域频道消息被删除或撤回 | on_public_message_delete | Message |
| MESSAGE_CREATE | 频道中产生新消息，仅私域机器人可订阅 | on_message_create | Message |
| MESSAGE_DELETE | 频道消息被删除或撤回，仅私域机器人可订阅 | on_message_delete | Message |

私信：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| DIRECT_MESSAGE_CREATE | 用户给机器人发送私信 | on_direct_message_create | DirectMessage |
| DIRECT_MESSAGE_DELETE | 私信消息被删除或撤回 | on_direct_message_delete | DirectMessage |

群聊与单聊：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| GROUP_AT_MESSAGE_CREATE | 群聊中有人 @ 机器人 | on_group_at_message_create | GroupMessage |
| GROUP_MESSAGE_CREATE | 群聊中产生新消息，全量模式 | on_group_message_create | GroupMessage |
| C2C_MESSAGE_CREATE | 用户与机器人单聊时发送消息 | on_c2c_message_create | C2CMessage |
| GROUP_ADD_ROBOT | 机器人被加入群聊 | on_group_add_robot | GroupManageEvent |
| GROUP_DEL_ROBOT | 机器人被移出群聊 | on_group_del_robot | GroupManageEvent |
| GROUP_MSG_REJECT | 群管理员关闭机器人主动消息 | on_group_msg_reject | GroupManageEvent |
| GROUP_MSG_RECEIVE | 群管理员开启机器人主动消息 | on_group_msg_receive | GroupManageEvent |
| GROUP_MEMBER_ADD | 新成员加入群聊 | on_group_member_add | GroupMemberEvent |
| GROUP_MEMBER_REMOVE | 成员退出群聊 | on_group_member_remove | GroupMemberEvent |
| GROUP_JOIN_REQUEST | 用户申请加入群聊 | on_group_join_request | GroupJoinRequestEvent |
| FRIEND_ADD | 用户添加机器人为好友 | on_friend_add | C2CManageEvent |
| FRIEND_DEL | 用户删除机器人好友 | on_friend_del | C2CManageEvent |
| C2C_MSG_REJECT | 用户关闭单聊主动消息 | on_c2c_msg_reject | C2CManageEvent |
| C2C_MSG_RECEIVE | 用户开启单聊主动消息 | on_c2c_msg_receive | C2CManageEvent |
| SUBSCRIBE_MESSAGE_STATUS | 订阅消息授权状态发生变更 | on_subscribe_message_status | SubscribeMessageStatusEvent |

互动与审核：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| INTERACTION_CREATE | 用户触发按钮等互动操作 | on_interaction_create | Interaction |
| MESSAGE_AUDIT_PASS | 消息审核通过 | on_message_audit_pass | MessageAudit |
| MESSAGE_AUDIT_REJECT | 消息审核不通过 | on_message_audit_reject | MessageAudit |
| MESSAGE_REACTION_ADD | 用户给消息添加表情表态 | on_message_reaction_add | Reaction |
| MESSAGE_REACTION_REMOVE | 用户移除消息表情表态 | on_message_reaction_remove | Reaction |

音频与音视频/直播：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| AUDIO_START | 音频开始播放 | on_audio_start | AudioAction |
| AUDIO_FINISH | 音频播放结束 | on_audio_finish | AudioAction |
| AUDIO_ON_MIC | 用户上麦 | on_audio_on_mic | AudioAction |
| AUDIO_OFF_MIC | 用户下麦 | on_audio_off_mic | AudioAction |
| AUDIO_OR_LIVE_CHANNEL_MEMBER_ENTER | 用户进入音视频或直播子频道 | on_audio_or_live_channel_member_enter | PublicAudio |
| AUDIO_OR_LIVE_CHANNEL_MEMBER_EXIT | 用户退出音视频或直播子频道 | on_audio_or_live_channel_member_exit | PublicAudio |

论坛与开放论坛：

| 事件类型 | 事件说明 | 回调方法 | 回调参数模型 |
| --- | --- | --- | --- |
| FORUM_THREAD_CREATE | 用户在论坛创建主题 | on_forum_thread_create | ForumThread |
| FORUM_THREAD_UPDATE | 用户在论坛更新主题 | on_forum_thread_update | ForumThread |
| FORUM_THREAD_DELETE | 用户在论坛删除主题 | on_forum_thread_delete | ForumThread |
| FORUM_POST_CREATE | 用户在论坛创建帖子 | on_forum_post_create | dict |
| FORUM_POST_DELETE | 用户在论坛删除帖子 | on_forum_post_delete | dict |
| FORUM_REPLY_CREATE | 用户在论坛发表回复或评论 | on_forum_reply_create | dict |
| FORUM_REPLY_DELETE | 用户在论坛删除回复或评论 | on_forum_reply_delete | dict |
| FORUM_PUBLISH_AUDIT_RESULT | 论坛发表内容审核结果下发 | on_forum_publish_audit_result | dict |
| OPEN_FORUM_THREAD_CREATE | 用户在开放论坛创建主题 | on_open_forum_thread_create | OpenForumThread |
| OPEN_FORUM_THREAD_UPDATE | 用户在开放论坛更新主题 | on_open_forum_thread_update | OpenForumThread |
| OPEN_FORUM_THREAD_DELETE | 用户在开放论坛删除主题 | on_open_forum_thread_delete | OpenForumThread |
| OPEN_FORUM_POST_CREATE | 用户在开放论坛创建帖子 | on_open_forum_post_create | dict |
| OPEN_FORUM_POST_DELETE | 用户在开放论坛删除帖子 | on_open_forum_post_delete | dict |
| OPEN_FORUM_REPLY_CREATE | 用户在开放论坛发表回复 | on_open_forum_reply_create | dict |
| OPEN_FORUM_REPLY_DELETE | 用户在开放论坛删除回复 | on_open_forum_reply_delete | dict |

系统事件：

| 事件类型 | 事件说明 | 回调方法 | 回调参数 |
| --- | --- | --- | --- |
| READY | WebSocket 连接并鉴权成功，机器人已准备好 | on_ready | 无参数 |
| RESUMED | WebSocket 断线后恢复会话成功 | on_resumed | 无参数 |

## 2. 主要事件对象字段

### Message

频道消息对象，常用字段：

- id：消息 ID
- channel_id：子频道 ID
- guild_id：频道 ID
- content：文本内容
- author：发送者 User 对象
- member：频道成员信息
- mentions：被 @ 的用户列表
- attachments：附件列表
- message_reference：引用消息信息
- seq：全局消息序号
- seq_in_channel：子频道消息序号
- timestamp：时间
- event_id：事件 ID
- raw：完整原始 payload 字典

### DirectMessage

私信消息对象，常用字段：

- id：消息 ID
- guild_id：来源频道 ID
- channel_id：私信会话 ID
- content：文本内容
- author：发送者 User 对象
- attachments：附件列表
- raw：完整原始 payload 字典

### GroupMessage

群消息对象，常用字段：

- id：消息 ID
- group_openid：群 OpenID
- content：文本内容
- author：发送者 User 对象
- mentions：被 @ 的用户列表
- attachments：附件列表
- msg_seq：消息序号
- timestamp：时间
- raw：完整原始 payload 字典

### C2CMessage

单聊消息对象，常用字段：

- id：消息 ID
- content：文本内容
- author：发送者 User 对象
- attachments：附件列表
- msg_seq：消息序号
- timestamp：时间
- raw：完整原始 payload 字典

### User

用户对象，常用字段：

- id：用户 ID
- username：用户名
- avatar：头像
- bot：是否机器人
- user_openid：单聊 OpenID
- member_openid：群成员 OpenID
- union_openid：跨 AppID 用户标识
- union_user_account：联合账号

### Guild

频道对象，常用字段：

- id：频道 ID
- name：频道名
- icon：头像
- owner_id：所有者 ID
- member_count：成员数
- max_members：最大成员数
- description：描述
- joined_at：加入时间

### Channel

子频道对象，常用字段：

- id：子频道 ID
- guild_id：所属频道 ID
- name：名称
- type：类型
- sub_type：子类型
- position：排序
- parent_id：分组 ID
- private_type：私密类型
- speak_permission：发言权限

### Member

频道成员对象，常用字段：

- user：User 对象
- nick：昵称
- roles：身份组 ID 列表
- joined_at：加入时间
- guild_id：频道 ID

### Interaction

互动事件对象，常用字段：

- id：互动 ID
- type：互动类型
- scene：场景
- chat_type：聊天类型
- guild_id：频道 ID
- channel_id：子频道 ID
- user_openid：用户 OpenID
- group_openid：群 OpenID
- group_member_openid：群成员 OpenID
- data：互动数据字典
- version：版本

### Reaction

表情表态对象，常用字段：

- user_id：用户 ID
- channel_id：子频道 ID
- guild_id：频道 ID
- emoji：表情数据字典
- target：表态目标字典

### MessageAudit

消息审核对象，常用字段：

- audit_id：审核 ID
- message_id：消息 ID
- guild_id：频道 ID
- channel_id：子频道 ID

### GroupMemberEvent

群成员事件对象，常用字段：

- group_openid：群 OpenID
- member_openid：群成员 OpenID
- user_openid：用户 OpenID
- timestamp：时间

### GroupJoinRequestEvent

入群申请事件对象，常用字段：

- group_openid：群 OpenID
- join_request_id：申请 ID
- member_openid：申请成员 OpenID
- union_openid：用户 OpenID
- username：用户名
- apply_at：申请时间
- verify_info：验证信息字典
- auto_approved：自动审批信息字典

## 3. 快捷回复

部分事件对象带 reply 方法：

    class MyBot(Client):
        async def on_at_message_create(self, message: Message):
            await message.reply(content="回复频道消息")

        async def on_direct_message_create(self, message: DirectMessage):
            await message.reply(content="回复私信")

        async def on_group_at_message_create(self, message: GroupMessage):
            await message.reply(content="回复群消息")

        async def on_c2c_message_create(self, message: C2CMessage):
            await message.reply(content="回复单聊消息")

reply 方法会自动使用当前消息的 channel_id、guild_id、group_openid 或 user_openid 作为目标。

## 4. 事件处理错误

如果事件回调抛出异常，默认会调用 on_error：

    class MyBot(Client):
        async def on_error(self, event_method, *args, **kwargs):
            print("事件处理出错：", event_method)

你可以覆盖 on_error 来接入自己的日志或告警。
