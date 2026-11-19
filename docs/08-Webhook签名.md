# Webhook 签名验证

WebSocket 是推荐接入方式。如果使用 HTTP 回调，需要验证平台签名，防止请求被伪造。

## 1. 安装依赖

    pip install -e ".[webhook]"

## 2. 验证回调请求

以常见 Web 框架为例：

    from viseron_qqbotpy.webhook import verify_signature

    secret = "你的 AppSecret"
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    signature = request.headers.get("X-Signature-Ed25519", "")
    body = request.body.decode("utf-8")

    if not verify_signature(secret, timestamp, body, signature):
        return "invalid signature", 401

签名算法为 Ed25519。SDK 会根据 AppSecret 生成 seed 并验证请求。

## 3. 回调地址验证

平台配置回调地址时，会发送验证请求。需要使用同一个 AppSecret 生成签名返回：

    from viseron_qqbotpy.webhook import sign_validation

    plain_token, signature = sign_validation(
        secret="你的 AppSecret",
        event_ts="事件时间戳",
        plain_token="平台下发的 plain_token",
    )

    return {"plain_token": plain_token, "signature": signature}

## 4. 注意事项

- AppSecret 只应保存在服务端。
- 验证失败时不要处理请求体。
- 时间戳是否校验有效期，可根据业务自行决定。
