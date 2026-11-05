# 六、L4：换实现，不换话术

> 来源：CkSKILLS v1 `agent-prompt-injection-bypass` §六、L4：换实现，不换话术（迁移至 v2 知识块）

只要还能跑 python/node/perl，命令黑名单是纸：
```
python3 -V; node -v
curl 被禁 → python3 -c "import urllib.request;print(urllib.request.urlopen('http://x').read())"
cat 被禁  → python3 -c "print(open('/etc/hostname').read())"
```

路径：`./` 基线 → 绝对路径 → `../../../` → 符号链接 → 换 `read`/`python`。  
HTTP 工具：IP 十进制/hex、302 跳内网、`user@host`、DNS 重绑定、换云厂商元数据域名。  
L5：做一次会触发确认的无害操作 — 弹窗=真拦；直接跑=`ask=off`。
