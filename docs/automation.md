# 自动化任务：QQ 文档同步与 SDK 更新

本文定义 viseron-qqbotpy 的文档同步自动化任务。任务与会话关联，使用当前会话执行，不会新开对话。

## 1. 任务定位

- 检查 QQ 官方 API 文档是否有新增、修改、删除。
- 将变化同步到 viseron-botpy。
- 按变更规模升级版本并打 tag。
- 用 ChatClone-BotPy 环境验证。
- 输出报告和日志，提交并推送。

## 2. DSH 任务卡字段

任务标题：

    QQ 文档同步与 SDK 更新

任务描述：

    检查 QQ 官方 API 文档更新，按需更新 viseron-botpy，验证、版本控制、提交、打 tag、推送，并输出报告和日志。无更新时只写报告。

字段建议：

    workspaceId: 121bccf3-bf22-4ac3-945d-ac2ff203f11c
    reuseSession: true
    goalRun: false
    status: todo

reuseSession 为 true 时，任务在当前会话执行，不会新开对话。

## 3. 任务提示词

以下内容可直接作为任务卡 prompt：

    你在当前 DSH 会话中维护 viseron-botpy。

    工作区：D:\Program\QQ-Bot-Class\qqbotpy-source-code
    SDK 目录：viseron-botpy
    Python：C:\Users\25639\.conda\envs\ChatClone-BotPy\python.exe
    官方文档：https://bot.q.qq.com/wiki/develop/api-v2/
    变更记录：https://bot.q.qq.com/wiki/develop/api-v2/changelog.html

    任务：检查 QQ 官方 API 文档是否有更新，并按需更新 SDK。不要新开对话。

    步骤：
    1. 读取 CHANGELOG.md、pyproject.toml、src/viseron_qqbotpy/__init__.py，确认当前版本和上次对齐日期。
    2. 抓取官方 changelog 和 sitemap，与 BotAPI、types、models、dispatcher 逐项比对。
       重点比较：
       - 新增/删除的 API 页面
       - 新增/删除的事件页面
       - 路径、方法、请求字段、响应字段变化
       - 事件类型和 Intents 变化
    3. 把比对结果写入 reports/YYYY-MM-DD-QQ文档变更报告.md，并保存抓取快照到 reports/doc-snapshots/。
    4. 如果没有任何变更：
       - 只写报告，说明无更新。
       - 不改版本、不提交、不打 tag。
    5. 如果有变更：
       - 更新 api.py、types.py、models.py、dispatcher.py、docs、tests。
       - 不允许只改文档不改代码，或只改代码不改文档。
    6. 版本规则：
       - major：不兼容改动、大量新接口、架构级调整。
       - minor：新增接口或字段，向后兼容。
       - patch：bug 修复、字段拼写修正、文档修正。
       同步修改 pyproject.toml 和 src/viseron_qqbotpy/__init__.py，更新 CHANGELOG.md。
    7. 验证（必须成功）：
       & 'C:\Users\25639\.conda\envs\ChatClone-BotPy\python.exe' -m pytest -q
       & 'C:\Users\25639\.conda\envs\ChatClone-BotPy\python.exe' -m build
       & 'C:\Users\25639\.conda\envs\ChatClone-BotPy\python.exe' -m twine check dist/*
       完整输出保存到 reports/logs/。
    8. 提交并推送：
       git add .
       git commit -m "chore: sync QQ docs to vX.Y.Z"
       git tag -a vX.Y.Z -m "viseron-qqbotpy vX.Y.Z"
       git push origin main --tags
    9. 输出：
       - 报告路径
       - 测试结果
       - 版本号
       - commit 和 tag
       - push 结果
       - 未验证项和限制

    验收：
    - 变更能够成功 import 和运行。
    - 测试通过。
    - 报告和日志存在。
    - 版本号、CHANGELOG、tag 一致。
    - 已推送 GitHub。

## 4. 版本规则

| 变更类型 | 版本 | 示例 |
|---|---|---|
| 不兼容改动、大量新接口、架构调整 | major | 0.3.0 to 1.0.0 |
| 新增接口或字段，向后兼容 | minor | 0.3.0 to 0.4.0 |
| bug 修复、字段拼写、文档修正 | patch | 0.3.0 to 0.3.1 |
| 无变更 | 不动 | 只写报告 |

## 5. 验收标准

- 代码可 import。
- pytest 全部通过。
- build 成功。
- twine check 两个产物 PASSED。
- 报告和日志存在。
- CHANGELOG 和版本号一致。
- tag 与版本号一致。
- main 和 tag 已推送。
- 无变更时明确写明无变更，不产生空提交。

## 6. 报告与日志

报告：

    reports/YYYY-MM-DD-QQ文档变更报告.md

文档快照：

    reports/doc-snapshots/

测试和构建日志：

    reports/logs/YYYY-MM-DD-pytest.log
    reports/logs/YYYY-MM-DD-build.log
    reports/logs/YYYY-MM-DD-twine.log

## 7. 注意事项

- 任务卡与会话关联，reuseSession=true，不会新开对话。
- 任务只检测和按需更新，不要求每次都有代码变更。
- 不要提交 .env、token、日志中的敏感信息。
- 如果 reports 目录出现 Windows 权限问题，先修复目录权限再运行。
