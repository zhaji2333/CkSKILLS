---
name: source-code-audit
description: 当拿到源码、代码片段、反编译产物，或用户要求代码审计时调用。负责输入点→传播链→危险函数Sink的静态审计，跨语言（PHP/Java/Python/Node/Go）危险函数速查，输出可疑调用链与缺陷触发条件。
---

# source-code-audit — 源码审计专项深度挖掘

## 何时调用（触发条件）

- 有源码（开源项目/泄露代码/反编译产物）
- 用户给代码片段要求审计
- 前端 source map 还原出完整源码
- APK 反编译后需要审计 Java/so 层
- 需要定位：拼接、反序列化、模板渲染、命令执行、文件操作、鉴权分支

## 一、静态审计方法（SAST）

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

## 二、危险函数速查（按语言）

### PHP
```
eval / assert / system / exec / passthru / shell_exec / popen
include / require / file_get_contents / unserialize
preg_replace(e修饰符) / create_function / $$变量覆盖
```

### Java
```
Runtime.exec / ProcessBuilder / readObject / XMLDecoder
SpEL / OGNL / MVEL / EL表达式
JNDI lookup / JdbcRowSetImpl / TemplatesImpl
```

### Python
```
eval / exec / os.system / subprocess / pickle.loads
yaml.load(Loader=Loader) / __import__ / compile
```

### Node.js
```
eval / Function() / child_process / vm.runInContext
__proto__ / constructor.prototype（原型污染）
```

### Go
```
os/exec.Command / text/template（SSTI）
sql拼接 / 不安全的反序列化
```

## 三、鉴权审计要点

- 接口/路由是否有统一鉴权中间件
- 是否存在免鉴权路径（白名单/静态资源/回调）
- 角色判断是否可信（前端传角色 vs 服务端查库）
- 对象级校验：是否只校验登录不校验归属
- 管理接口与普通接口的权限边界

## 四、结合其他技能

审计发现的具体漏洞类型转对应技能深化：
- 注入点 → `injection-vulns`
- 反序列化 → `deserialization-xxe`
- 文件操作 → `file-handling`
- 鉴权缺陷 → `auth-access-control`
- 加密/签名算法 → `auth-access-control`

## 五、输出与报告要点

- 每个漏洞：输入点 / 传播链 / Sink / 缺失的校验
- 附代码片段与触发条件
- 可利用性评估（前置条件、影响面）
- 修复方案（代码级）

