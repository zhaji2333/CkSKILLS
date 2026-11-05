# 一、静态审计方法（SAST）

> 来源：CkSKILLS v1 `source-code-audit` §一、静态审计方法（SAST）（迁移至 v2 知识块）

### 核心思路
```
输入点 → 传播链 → 危险函数（Sink）
```

### 审计关注
- 拼接：SQL/命令/路径/模板
- 反序列化：unserialize/readObject/pickle
- 模板渲染：用户输入进入模板引擎
- 命令执行：exec/system/ProcessBuilder
- 文件操作：上传/下载/包含/删除
- 鉴权分支：哪些接口缺少权限校验

### 输出格式
- 可疑调用链（输入 → 传播 → Sink）
- 关键代码片段
- 缺陷触发条件（参数、前置校验）
