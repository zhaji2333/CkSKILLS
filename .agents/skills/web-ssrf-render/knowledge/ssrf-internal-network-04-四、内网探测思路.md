# 四、内网探测思路

> 来源：CkSKILLS v1 `ssrf-internal-network` §四、内网探测思路（迁移至 v2 知识块）

1. **先验证可控性**：请求外网可控地址（Burp Collaborator / DNSLog / 自己的 VPS）确认请求发出
2. **内网网段探测**：扫描 127.0.0.1、10.x、172.16-31.x、192.168.x 常见端口
3. **Redis 未授权**：`gopher://` 写入 crontab/SSH key/主从复制 RCE
4. **管理面板**：内网 Jenkins/ES/Grafana/MySQL 等
5. **协议利用**：
   ```
   file:///etc/passwd
   gopher://127.0.0.1:6379/_<redis命令>
   dict://127.0.0.1:6379/info
   ```
6. **DNS 重绑定**：注册域名解析到 127.0.0.1/内网 IP，绕过 IP 校验
7. **重定向绕过**：302 跳转至内网/云元数据，绕过 URL 白名单
