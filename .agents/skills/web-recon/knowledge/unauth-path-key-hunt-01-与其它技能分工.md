# 与其它技能分工

> 来源：CkSKILLS v1 `unauth-path-key-hunt` §与其它技能分工（迁移至 v2 知识块）

```
怀疑隐藏未授权
    │
    ▼
unauth-path-key-hunt     找 Host/路径/钥，证伪加密
    ├─ 拆 webpack / 脏收集 / 提字符串     → recon-js-analysis
    ├─ 路径已通，角色墙 / IDOR            → auth-access-control
    ├─ 路径已通，全方法 / 旧版 / 网关协议  → api-protocol-security
    ├─ 路径在包里                         → android / miniprogram
    └─ 已验证成稿                         → MD 报告（AGENTS.md 第 6 节）
```

拆 JS、Wayback、Packer 的细则以 `recon-js-analysis` 为准，此处不重复。
跨轮线索落盘以 `hunt-clueboard` 为准：开工先读 `hunts/<目标>/CLUEBOARD.md`，P2 指纹/405/`[]`/迁域结论当轮写回，禁止只写在对话里。
