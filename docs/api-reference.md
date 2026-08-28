# API 参考

所有 API 都通过 client.api 调用。方法返回平台响应的 JSON 数据，204 响应返回 None。

## 1. 频道与子频道

- get_guild(guild_id)：获取频道详情
- get_channels(guild_id)：获取子频道列表
- get_channel(channel_id)：获取子频道详情
- create_channel(guild_id, name, type, sub_type, **fields)：创建子频道
- update_channel(channel_id, **fields)：修改子频道
- delete_channel(channel_id)：删除子频道
- get_online_nums(channel_id)：获取音视频/直播子频道在线成员数
- get_channel_user_permissions(channel_id, user_id)：获取子频道用户权限
- update_channel_user_permissions(channel_id, user_id, add, remove)：修改子频道用户权限
- get_channel_role_permissions(channel_id, role_id)：获取子频道身份组权限
- update_channel_role_permissions(channel_id, role_id, add, remove)：修改子频道身份组权限

## 2. 身份组与成员

- get_guild_roles(guild_id)：获取身份组列表
- create_guild_role(guild_id, **fields)：创建身份组
- update_guild_role(guild_id, role_id, **fields)：修改身份组
- delete_guild_role(guild_id, role_id)：删除身份组
- create_guild_role_member(guild_id, role_id, user_id, channel_id=None)：添加身份组成员
- delete_guild_role_member(guild_id, role_id, user_id, channel_id=None)：移除身份组成员
- get_guild_member(guild_id, user_id)：获取成员详情
- get_guild_members(guild_id, after, limit)：获取成员列表
- delete_guild_member(guild_id, user_id, add_blacklist, delete_history_msg_days)：删除成员
- get_guild_role_members(guild_id, role_id, start_index, limit)：获取身份组成员列表
- get_voice_members(channel_id)：获取语音频道成员列表

## 3. 禁言与消息频率

- mute_all(guild_id, mute_end_timestamp, mute_seconds)：全员禁言
- cancel_mute_all(guild_id)：取消全员禁言
- mute_member(guild_id, user_id, mute_end_timestamp, mute_seconds)：指定成员禁言
- mute_multi_member(guild_id, user_ids, mute_end_timestamp, mute_seconds)：批量成员禁言
- cancel_mute_multi_member(guild_id, user_ids)：取消批量成员禁言
- get_message_setting(guild_id)：获取频道消息频率设置

## 4. 频道消息与私信

- get_message(channel_id, message_id)：获取指定消息
- post_message(channel_id, content, embed, ark, message_reference, image, file_image, msg_id, event_id, markdown, keyboard, **fields)：发送频道消息
- recall_message(channel_id, message_id, hidetip)：撤回频道消息
- patch_guild_message(channel_id, patch_msg_id, ...)：修改频道消息
- create_dms(guild_id, user_id)：创建私信会话
- post_dms(guild_id, content, embed, ark, message_reference, image, file_image, msg_id, event_id, markdown, keyboard, **fields)：发送私信

## 5. 表情表态与精华

- put_reaction(channel_id, message_id, emoji_type, emoji_id)：添加表情表态
- delete_reaction(channel_id, message_id, emoji_type, emoji_id)：删除表情表态
- get_reaction_users(channel_id, message_id, emoji_type, emoji_id, cookie, limit)：获取表态用户列表
- put_pin(channel_id, message_id)：添加精华消息
- delete_pin(channel_id, message_id)：删除精华消息
- get_pins(channel_id)：获取精华消息列表

## 6. 日程、论坛、音频、公告

- get_schedules(channel_id, since)：获取日程列表
- get_schedule(channel_id, schedule_id)：获取日程详情
- create_schedule(channel_id, name, start_timestamp, end_timestamp, jump_channel_id, remind_type)：创建日程
- update_schedule(channel_id, schedule_id, ...)：修改日程
- delete_schedule(channel_id, schedule_id)：删除日程
- get_threads(channel_id)：获取帖子列表
- get_thread_detail(channel_id, thread_id)：获取帖子详情
- post_thread(channel_id, title, content, format)：发表帖子
- delete_thread(channel_id, thread_id)：删除帖子
- update_audio(channel_id, audio_control)：音频控制
- on_microphone(channel_id)：机器人上麦
- off_microphone(channel_id)：机器人下麦
- create_announce(guild_id, channel_id, message_id)：创建消息公告
- create_recommend_announce(guild_id, announces_type, recommend_channels)：创建推荐子频道公告
- delete_announce(guild_id, message_id)：删除公告

## 7. 权限、用户与网关

- get_permissions(guild_id)：获取机器人在频道的 API 权限列表
- post_permission_demand(guild_id, channel_id, api_identify, desc)：创建权限授权链接
- me()：获取机器人详情
- me_guilds(guild_id, limit, desc)：获取机器人加入的频道列表
- get_ws_url()：获取通用 WSS 接入点
- get_ws_url_shard()：获取带分片 WSS 接入点

## 8. 群聊消息与富媒体

- post_group_message(group_openid, msg_type, content, markdown, keyboard, msg_id, event_id, msg_seq, media, message_reference, is_wakeup, **fields)：发送群聊消息
- recall_group_message(group_openid, message_id)：撤回群聊消息
- post_group_file(group_openid, file_type, url, srv_send_msg, file_name, upload_id)：群聊富媒体上传
- post_group_upload_prepare(group_id, file_type, file_size, file_name, md5, sha1, md5_10m)：群聊富媒体预上传
- post_group_upload_part_finish(group_id, upload_id, part_index, block_size, md5)：群聊分片上传完成

## 9. 单聊消息与富媒体

- post_c2c_message(openid, msg_type, content, markdown, keyboard, msg_id, event_id, msg_seq, media, message_reference, is_wakeup, **fields)：发送单聊消息
- recall_c2c_message(openid, message_id)：撤回单聊消息
- post_c2c_stream_message(openid, **fields)：流式发送单聊消息
- post_c2c_file(openid, file_type, url, srv_send_msg, file_name, upload_id)：单聊富媒体上传
- post_c2c_upload_prepare(user_id, file_type, file_size, file_name, md5, sha1, md5_10m)：单聊富媒体预上传
- post_c2c_upload_part_finish(user_id, upload_id, part_index, block_size, md5)：单聊分片上传完成

## 10. 群管理

- get_group_info(group_openid)：获取群基本信息
- get_group_bot_state(group_openid)：获取机器人群内状态
- get_group_join_request_list(group_openid, cursor, limit)：拉取入群申请列表
- approve_group_join_request(group_openid, member_openid, op, join_request_id, reject_reason, add_to_member_blacklist)：审批入群申请
- get_group_restrict_chat_setting(group_openid)：查询群禁言状态
- set_group_restrict_chat_setting(group_openid, members)：设置群成员禁言
- get_group_join_approval_strategies(cursor, limit)：查询入群自动审批策略列表
- create_group_join_approval_strategy(**fields)：创建入群自动审批策略
- update_group_join_approval_strategy(strategy_id, **fields)：修改入群自动审批策略
- delete_group_join_approval_strategy(strategy_id)：删除入群自动审批策略
- execute_group_join_approval_strategy(strategy_id)：执行入群自动审批策略
- update_group_join_approval_strategy_whitelist(strategy_id, **fields)：修改策略白名单

## 11. 菜单、面板与分享

- get_menu()：查询全局自定义菜单
- update_menu(menu)：修改全局自定义菜单
- get_panels()：查询指令面板列表
- create_panel(**fields)：创建指令面板
- get_panel(panel_id)：查询指令面板详情
- update_panel(panel_id, panel)：修改指令面板
- update_panel_target(panel_id, **fields)：修改指令面板关联对象
- delete_panel(panel_id)：删除指令面板
- create_url_link(url_link)：生成分享链接

## 12. 互动响应

- on_interaction_result(interaction_id, code)：响应互动事件

## 13. 错误类型

所有 HTTP 错误都会抛出 APIError 或其子类：

- AuthenticationFailedError：401 认证失败
- ForbiddenError：403 无权限
- NotFoundError：404 接口或资源不存在
- MethodNotAllowedError：405 方法不允许
- RateLimitError：429 频率限制
- ServerError：5xx 服务端错误

示例：

    from viseron_qqbotpy import APIError


    try:
        await self.api.get_guild("频道 ID")
    except APIError as exc:
        print(exc.status, exc.code, exc.trace_id, exc)
