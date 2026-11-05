# 二、云元数据（打内网核心）

> 来源：CkSKILLS v1 `ssrf-internal-network` §二、云元数据（打内网核心）（迁移至 v2 知识块）

```
AWS:     http://169.254.169.254/latest/meta-data/
阿里云:  http://100.100.100.200/latest/meta-data/
腾讯云:  http://metadata.tencentyun.com/latest/meta-data/
```

目标：获取临时凭证（IAM Role）、实例元数据、网络配置，进一步接管云资产。拿到凭据后的 STS 枚举、实例角色挖权与云助手横向见 `cloud-infra-supply-chain` 三、3.1。
