# 六、客户端连云端网关

> 来源：CkSKILLS v1 `agent-execution-channel-hijack` §六、客户端连云端网关（迁移至 v2 知识块）

桌面端 / App / 小程序若只是云端 Agent 的壳：

- 反编译提 **云端 BaseURL + Key + 签名**（`apk-reversing` / `asc-fast-hunt` / `recon-js-analysis`）
- 直连云 API，按第二节走
- 「客户端当肉鸡」= 云网关被劫持后客户端执行下发，证据在 takeover L3，不在本机编码 Agent 逃逸
